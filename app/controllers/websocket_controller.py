from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import pika, json
import os
import uuid
WebSocketRouter = APIRouter()
from datetime import datetime
from app.schemas.message_schema import CreateMessage
from app.rabbit.publisher import send_to_exchange

# Lista de conexões
global_connections = dict()
private_connections = {} # chave: user_id, valor: websocket(s)

RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@rabbitmq:5672/")

def publish_message(queue, message):
    connection = pika.BlockingConnection(pika.URLParameters(RABBITMQ_URL))
    channel = connection.channel()
    channel.queue_declare(queue=queue, durable=True)
    channel.basic_publish(exchange="", routing_key=queue, body=json.dumps(message))
    connection.close()

@WebSocketRouter.websocket("/ws/global")
async def ws_global(websocket: WebSocket):
    id = str(uuid.uuid4())
    await websocket.accept()
    global_connections[id] = websocket
    try:       
        while True:
            try:
                data = await websocket.receive_text()
                
                # Valida se a mensagem não está vazia
                if not data or not data.strip():
                    await websocket.send_text(json.dumps({
                        "status": "error",
                        "error": "Mensagem não pode estar vazia"
                    }))
                    continue
                
                # Tenta parsear JSON se possível, senão trata como texto simples
                sender_id = id  # Default: usa ID da conexão
                content = data  # Default: usa o texto recebido
                
                try:
                    message_data = json.loads(data)
                    if isinstance(message_data, dict):
                        sender_id = message_data.get("sender_id", id)
                        content = message_data.get("content", data)
                        # Valida se content existe e não está vazio
                        if not content or not str(content).strip():
                            content = data if data else ""
                    else:
                        # Se for JSON mas não dict, converte para string
                        content = str(message_data)
                except json.JSONDecodeError:
                    # Se não for JSON válido, trata como texto simples
                    pass
                
                # Valida conteúdo após processamento
                if not content or not str(content).strip():
                    await websocket.send_text(json.dumps({
                        "status": "error",
                        "error": "Conteúdo da mensagem não pode estar vazio"
                    }))
                    continue
                
                # Valida sender_id
                if not sender_id or not str(sender_id).strip():
                    sender_id = id
                
                # Estrutura mensagem conforme MessageSchema
                try:
                    message = CreateMessage(
                        chat_id="global",
                        sender_id=str(sender_id).strip(),
                        recipient_id=None,  # Chat global não tem destinatário específico
                        content=str(content).strip(),
                        data=datetime.now()
                    )
                    
                    # Envia para exchange fanout via publisher
                    await send_to_exchange(message)
                    
                    # Confirma recebimento ao cliente
                    await websocket.send_text(json.dumps({
                        "status": "sent",
                        "message": message.model_dump()
                    }))
                    
                except ValueError as ve:
                    # Erro de validação do Pydantic
                    await websocket.send_text(json.dumps({
                        "status": "error",
                        "error": f"Erro de validação: {str(ve)}"
                    }))
                except Exception as e:
                    # Outros erros (ex: conexão RabbitMQ)
                    await websocket.send_text(json.dumps({
                        "status": "error",
                        "error": f"Erro ao enviar mensagem: {str(e)}"
                    }))
                    
            except Exception as e:
                # Erro ao receber mensagem
                await websocket.send_text(json.dumps({
                    "status": "error",
                    "error": f"Erro ao processar mensagem: {str(e)}"
                }))
                
    except WebSocketDisconnect:
        if id in global_connections:
            del global_connections[id]
    except Exception as e:
        # Erro geral na conexão
        print(f"Erro na conexão WebSocket: {e}")
        if id in global_connections:
            del global_connections[id]


@WebSocketRouter.websocket("/ws/private/{target_user_id}")
async def ws_private(websocket: WebSocket, target_user_id: str):
    await websocket.accept()
    if target_user_id not in private_connections:
        private_connections[target_user_id] = set()
    private_connections[target_user_id].add(websocket)

    try:
        while True:
            raw = await websocket.receive_text()
            data = json.loads(raw)
            message = {
                "chat_type": "private",
                "target": target_user_id,
                "message": data
            }
            publish_message("chat_private", message)
    except WebSocketDisconnect:
        private_connections[target_user_id].remove(websocket)
