import asyncio #usado para executar tarefas assíncronas
import json
import pika
from motor.motor_asyncio import AsyncIOMotorClient
from app.schemas.message_schema import MessageSchema
from datetime import datetime
from pydantic import ValidationError

MONGO_URI = "mongodb://root:root@mongo:27017" #conecta ao mongodb
EXCHANGE_NAME = "chat_global_exchange"  # Nome da exchange fanout (deve ser o mesmo do publisher)
QUEUE_NAME = "chat_global_messages"  # Nome da fila vinculada à exchange

client = AsyncIOMotorClient(MONGO_URI)
db = client.db_chat
messages = db.messages  # coleção no Mongo

async def save_message(msg_data: dict):
    """
    Salva mensagem no MongoDB após validação
    """
    try:
        # Converte string ISO para datetime se necessário
        if 'data' in msg_data and isinstance(msg_data['data'], str):
            try:
                msg_data['data'] = datetime.fromisoformat(msg_data['data'])
            except (ValueError, AttributeError):
                # Se falhar, usa datetime atual
                msg_data['data'] = datetime.now()
        elif 'data' not in msg_data:
            msg_data['data'] = datetime.now()
        
        # Valida mensagem contra MessageSchema
        try:
            validated_message = MessageSchema(**msg_data)
            # Converte para dict para inserção no MongoDB
            message_dict = validated_message.model_dump(exclude={'id'})  # Exclui id pois MongoDB gera
        except ValidationError as e:
            print(f"Erro de validação da mensagem: {e}")
            # Salva mesmo assim com os dados recebidos, mas adiciona flag de validação
            msg_data['_validation_error'] = str(e)
            message_dict = msg_data
        
        # Insere no MongoDB
        result = await messages.insert_one(message_dict)
        print(f"Mensagem salva com sucesso. ID: {result.inserted_id}")
        return result.inserted_id
        
    except Exception as e:
        print(f"Erro ao salvar mensagem no MongoDB: {e}")
        raise

def callback(ch, method, properties, body):
    """
    Callback chamado pelo pika quando uma mensagem chega na fila
    """
    try:
        # Valida se body não está vazio
        if not body:
            print("Erro: Mensagem vazia recebida")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
            return
        
        # Decodifica o body
        try:
            body_str = body.decode('utf-8')
        except UnicodeDecodeError as e:
            print(f"Erro ao decodificar mensagem (UTF-8): {e}")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
            return
        
        # Valida se body_str não está vazio após decodificação
        if not body_str or not body_str.strip():
            print("Erro: Mensagem decodificada está vazia")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
            return
        
        # Parse JSON
        try:
            msg_data = json.loads(body_str)
        except json.JSONDecodeError as e:
            print(f"Erro ao decodificar JSON da mensagem: {e}")
            print(f"Conteúdo recebido: {body_str[:100]}...")  # Mostra primeiros 100 chars
            # Rejeita mensagem e não reenvia (mensagem malformada)
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
            return
        
        # Valida se msg_data é um dict
        if not isinstance(msg_data, dict):
            print(f"Erro: Mensagem não é um dicionário. Tipo: {type(msg_data)}")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
            return
        
        print(f"Mensagem recebida: {msg_data.get('chat_id', 'N/A')} - {msg_data.get('content', 'N/A')[:50]}...")
        
        # Salva no MongoDB de forma assíncrona
        try:
            asyncio.run(save_message(msg_data))
            # Confirma recebimento (ack) da mensagem apenas se salvou com sucesso
            ch.basic_ack(delivery_tag=method.delivery_tag)
        except ValidationError as ve:
            # Erro de validação - mensagem foi salva mas com flag de erro
            print(f"Erro de validação (mensagem salva com flag): {ve}")
            ch.basic_ack(delivery_tag=method.delivery_tag)  # Ainda confirma pois foi salva
        except Exception as e:
            print(f"Erro ao salvar mensagem no MongoDB: {e}")
            # Rejeita mensagem mas permite reenvio (pode ser erro temporário)
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
        
    except Exception as e:
        print(f"Erro inesperado no callback: {e}")
        import traceback
        traceback.print_exc()
        # Rejeita mensagem mas permite reenvio em caso de erro inesperado
        try:
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
        except Exception as nack_error:
            print(f"Erro ao fazer nack: {nack_error}")

def start_consumer():
    """
    Inicia o consumer que consome mensagens da exchange fanout
    """
    connection = None
    channel = None
    
    try:
        # Abre conexão com RabbitMQ
        try:
            connection = pika.BlockingConnection(pika.ConnectionParameters("rabbitmq"))
            channel = connection.channel()
        except pika.exceptions.AMQPConnectionError as e:
            print(f"Erro ao conectar com RabbitMQ: {e}")
            print("Verifique se o RabbitMQ está rodando e acessível em 'rabbitmq'")
            raise
        except Exception as e:
            print(f"Erro inesperado ao conectar com RabbitMQ: {e}")
            raise
        
        # Declara a exchange do tipo fanout
        try:
            channel.exchange_declare(
                exchange=EXCHANGE_NAME,
                exchange_type='fanout',
                durable=True
            )
            print(f"Exchange '{EXCHANGE_NAME}' declarada com sucesso")
        except Exception as e:
            print(f"Erro ao declarar exchange: {e}")
            raise
        
        # Declara a fila (exclusiva=False para persistir, auto_delete=False)
        try:
            result = channel.queue_declare(
                queue=QUEUE_NAME,
                durable=True,
                exclusive=False,
                auto_delete=False
            )
            print(f"Fila '{QUEUE_NAME}' declarada. {result.method.message_count} mensagens aguardando")
        except Exception as e:
            print(f"Erro ao declarar fila: {e}")
            raise
        
        # Vincula a fila à exchange
        try:
            channel.queue_bind(
                exchange=EXCHANGE_NAME,
                queue=QUEUE_NAME
            )
            print(f"Fila '{QUEUE_NAME}' vinculada à exchange '{EXCHANGE_NAME}'")
        except Exception as e:
            print(f"Erro ao vincular fila à exchange: {e}")
            raise
        
        # Configura o consumer
        try:
            channel.basic_consume(
                queue=QUEUE_NAME,
                on_message_callback=callback,
                auto_ack=False  # Confirmação manual (ack) após processar
            )
        except Exception as e:
            print(f"Erro ao configurar consumer: {e}")
            raise
        
        print(f"Aguardando mensagens da exchange '{EXCHANGE_NAME}' na fila '{QUEUE_NAME}'...")
        print("Pressione CTRL+C para parar")
        
        # Inicia consumo
        channel.start_consuming()
        
    except KeyboardInterrupt:
        print("\nInterrompendo consumer...")
        if channel:
            try:
                channel.stop_consuming()
            except Exception as e:
                print(f"Erro ao parar consumo: {e}")
        if connection and not connection.is_closed:
            try:
                connection.close()
            except Exception as e:
                print(f"Erro ao fechar conexão: {e}")
        print("Consumer interrompido com sucesso")
    except pika.exceptions.AMQPConnectionError as e:
        print(f"Erro de conexão com RabbitMQ: {e}")
        if connection and not connection.is_closed:
            connection.close()
        raise
    except Exception as e:
        print(f"Erro no consumer: {e}")
        import traceback
        traceback.print_exc()
        if channel:
            try:
                channel.stop_consuming()
            except:
                pass
        if connection and not connection.is_closed:
            try:
                connection.close()
            except:
                pass
        raise

if __name__ == "__main__":
    start_consumer()
