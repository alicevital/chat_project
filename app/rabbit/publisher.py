import aio_pika #biblioteca assíncrona para comunicar com rabbitmq
import os #para ler variáveis de ambiente
import asyncio # necesário para executar funções async
import json #permite converter objetos python em json 
from app.schemas.message_schema import CreateMessage, MessageSchema
from typing import Union

RABBITMQ_URL = os.getenv("RABBITMQ_URL","amqp://guest:guest@rabbitmq/") # lê a variável de ambiente rabbitmq e se não existir usa a url
EXCHANGE_NAME = "chat_global_exchange"  # Nome da exchange fanout para chat global

# Variável global para reutilizar conexão
_connection = None
_channel = None

async def get_connection():
    """Obtém ou cria uma conexão reutilizável com RabbitMQ"""
    global _connection, _channel
    try:
        if _connection is None or _connection.is_closed:
            _connection = await aio_pika.connect_robust(RABBITMQ_URL)
            _channel = await _connection.channel()
        elif _channel is None or _channel.is_closed:
            _channel = await _connection.channel()
        return _connection, _channel
    except Exception as e:
        # Reset conexão em caso de erro
        _connection = None
        _channel = None
        raise ConnectionError(f"Erro ao conectar com RabbitMQ: {e}")

async def send_to_exchange(message: Union[CreateMessage, MessageSchema, dict]): 
    """
    Função assíncrona que recebe uma mensagem (MessageSchema, CreateMessage ou dict)
    e envia para a exchange fanout no RabbitMQ
    """
    max_retries = 3
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            connection, channel = await get_connection()
            
            # Declara a exchange do tipo fanout
            exchange = await channel.declare_exchange(
                EXCHANGE_NAME,
                aio_pika.ExchangeType.FANOUT,
                durable=True
            )
            
            # Valida e converte mensagem para dict se necessário
            if isinstance(message, (CreateMessage, MessageSchema)):
                message_dict = message.model_dump()
            elif isinstance(message, dict):
                message_dict = message
            else:
                raise ValueError(f"Tipo de mensagem não suportado: {type(message)}. Esperado: CreateMessage, MessageSchema ou dict")
            
            # Valida campos obrigatórios
            required_fields = ['chat_id', 'sender_id', 'content']
            for field in required_fields:
                if field not in message_dict or not message_dict[field]:
                    raise ValueError(f"Campo obrigatório '{field}' está faltando ou vazio")
            
            # Converte datetime para string ISO format
            if 'data' in message_dict:
                if hasattr(message_dict['data'], 'isoformat'):
                    message_dict['data'] = message_dict['data'].isoformat()
                elif not isinstance(message_dict['data'], str):
                    # Se não for datetime nem string, converte para string
                    message_dict['data'] = str(message_dict['data'])
            
            # Serializa para JSON
            try:
                message_body = json.dumps(message_dict, default=str)
            except (TypeError, ValueError) as e:
                raise ValueError(f"Erro ao serializar mensagem para JSON: {e}")
            
            # Valida se o body não está vazio
            if not message_body or len(message_body.encode()) == 0:
                raise ValueError("Mensagem serializada está vazia")
            
            # Publica na exchange fanout (não precisa de routing_key para fanout)
            await exchange.publish(
                aio_pika.Message(
                    body=message_body.encode('utf-8'),
                    delivery_mode=aio_pika.DeliveryMode.PERSISTENT  # Mensagem persistente
                ),
                routing_key=""  # Fanout não usa routing_key, mas pode ser string vazia
            )
            
            # Sucesso, sai do loop de retry
            return
            
        except (ConnectionError, Exception) as e:
            # Verifica se é erro de conexão do aio_pika
            if "connection" in str(e).lower() or "amqp" in str(e).lower():
                # Erro de conexão - tenta reconectar
                retry_count += 1
                if retry_count >= max_retries:
                    print(f"Erro ao conectar com RabbitMQ após {max_retries} tentativas: {e}")
                    raise ConnectionError(f"Não foi possível conectar com RabbitMQ após {max_retries} tentativas: {e}")
                # Reset conexão para forçar nova conexão na próxima tentativa
                global _connection, _channel
                _connection = None
                _channel = None
                await asyncio.sleep(1)  # Aguarda 1 segundo antes de tentar novamente
            else:
                # Outros erros de conexão
                retry_count += 1
                if retry_count >= max_retries:
                    raise
                await asyncio.sleep(1)
            
        except ValueError as ve:
            # Erro de validação - não tenta novamente
            print(f"Erro de validação na mensagem: {ve}")
            raise
            
        except Exception as e:
            # Outros erros
            print(f"Erro ao enviar mensagem para exchange: {e}")
            if retry_count >= max_retries - 1:
                raise
            retry_count += 1
            await asyncio.sleep(0.5)  # Aguarda antes de tentar novamente

async def send_to_queue(message: str): 
    """
    Função legada mantida para compatibilidade.
    Função assíncrona que recebe a mensagem e envia ao rabbitmq
    """
    connection = await aio_pika.connect_robust(RABBITMQ_URL)
    channel = await connection.channel()
    await channel.default_exchange.publish(
        aio_pika.Message(body=message.encode()),
        routing_key="chat_queue"
    )
    await connection.close()

async def close_connection():
    """Fecha a conexão global quando necessário"""
    global _connection, _channel
    if _channel and not _channel.is_closed:
        await _channel.close()
    if _connection and not _connection.is_closed:
        await _connection.close()
    _connection = None
    _channel = None
    