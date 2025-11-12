from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import pika, json
import os
import uuid
WebSocketRouter = APIRouter()

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
    global_connections[id] =websocket
    try:
        while True:
            data = await websocket.receive_text()
            message = {"chat_type": "global", "message": data}
            publish_message("chat_global", message)
    except WebSocketDisconnect:
        del global_connections[id]#(websocket)


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
