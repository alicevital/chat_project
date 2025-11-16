import datetime
import os
import aio_pika
import asyncio
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
    rabbit_conn = await aio_pika.connect_robust(os.getenv("RABBITMQ_URI", "amqp://guest:guest@localhost:5672"))
    rabbit_channel = await rabbit_conn.channel()



async def start_global_chat():
    await connect_rabbit()
    asyncio.create_task(start_global_consumer(rabbit_conn, clients))


@GlobalRouter.websocket("/ws/{username}")
async def ws_endpoint(ws: WebSocket, username: str):
    await ws.accept()
    clients.add(ws)

    try:
        while True:
            text = await ws.receive_text()
            time = datetime.datetime.now().strftime("%H:%M")

            final_message = f"[{time}] {username}: {text}"

            await rabbit_channel.default_exchange.publish(
                aio_pika.Message(
                    body=final_message.encode()
                ),
                routing_key="global_chat"
            )

    except WebSocketDisconnect:
        clients.remove(ws)