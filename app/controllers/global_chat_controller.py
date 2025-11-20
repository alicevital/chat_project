import os
import datetime
import aio_pika
import asyncio
from app.core.config import RABBITMQ_URI
from app.database.database import get_database
from app.infra.providers.rabbitmq_global_consumer import start_global_consumer
from fastapi import APIRouter, WebSocket
from fastapi.websockets import WebSocketDisconnect


GlobalRouter = APIRouter(tags=['Chat Global'])
clients = set()

# conexão única com RabbitMQ
rabbit_conn = None
rabbit_channel = None


async def connect_rabbit():
    global rabbit_conn, rabbit_channel
    rabbit_conn = await aio_pika.connect_robust(RABBITMQ_URI)
    rabbit_channel = await rabbit_conn.channel()



async def start_global_chat():
    await connect_rabbit()
    asyncio.create_task(start_global_consumer(rabbit_conn, clients))


# >>> COLLECTION DO MONGO <<<
db = get_database()
global_collection = db["global_messages"] 


@GlobalRouter.websocket("/ws/{username}")
async def ws_endpoint(ws: WebSocket, username: str):
    await ws.accept()
    clients.add(ws)

    # Historico de Mensagens publicas anteriores Persistidas no Mongo
    try:
        cursor = global_collection.find().sort("_id", 1)
        for msg in cursor:
            formatted = f"[{msg['timestamp']}] {msg['sender']}: {msg['message']}"
            await ws.send_text(formatted)
    except Exception as e:
        print("Erro carregando histórico:", e)

    try:
        while True:
            text = await ws.receive_text()
            if len(text) > 150:
                text = "..."
                return "Payload too large"
                
            time = datetime.datetime.now(datetime.timezone.utc).strftime("%H:%M")

            final_message = f"[{time}] {username}: {text}"

            # Envia para RabbitMQ (broadcast)
            await rabbit_channel.default_exchange.publish(
                aio_pika.Message(
                    body=final_message.encode()
                ),
                routing_key="global_chat"
            )

            # >>> PERSISTE NO MONGO <<<
            global_collection.insert_one({
                "sender": username,
                "message": text,
                "timestamp": time
            })

    except WebSocketDisconnect:
        clients.remove(ws)