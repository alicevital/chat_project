import asyncio
from fastapi import WebSocket, WebSocketDisconnect, APIRouter
import datetime
import aio_pika
import os
from app.database.database import get_database

PrivateRouter = APIRouter()

# salas do chat privado (apenas websockets)
private_rooms = {}  # { room_id: set(WebSocket) }

# conexões RabbitMQ (1 canal por sala)
rabbit_connections = {}  # { room_id: channel }


async def get_channel(room_id: str):
    """
    Cria conexão + canal + queue exclusiva para a sala, se ainda não existir.
    """
    if room_id in rabbit_connections:
        return rabbit_connections[room_id]

    conn = await aio_pika.connect_robust(
        os.getenv("RABBITMQ_URI")
    )
    channel = await conn.channel()

    # cria fila da sala
    await channel.declare_queue(room_id, durable=True)

    rabbit_connections[room_id] = channel
    return channel

db = get_database()
private_collection = db["private_messages"]

@PrivateRouter.websocket("/ws/private/{room_id}/{username}")
async def private_chat(ws: WebSocket, room_id: str, username: str):
    await ws.accept()

    # cria sala se não existir
    if room_id not in private_rooms:
        private_rooms[room_id] = set()

    # limite de 2 usuários
    if len(private_rooms[room_id]) >= 2:
        await ws.send_text("A sala está cheia: apenas 2 usuários podem entrar.")
        await ws.close()
        return

    # adiciona usuário à sala
    private_rooms[room_id].add(ws)


    # Historico de Mensagens Privadas anteriores Persistidas no Mongo 
    try:
        cursor = private_collection.find({"room_id": room_id}).sort("_id", 1)

        for msg in cursor:
            formatted = f"[{msg['timestamp']}] {msg['sender']}: {msg['message']}"
            await ws.send_text(formatted)
    except Exception as e:
        print("Erro carregando histórico:", e)

    # obtém canal RabbitMQ da sala
    channel = await get_channel(room_id)
    queue = await channel.declare_queue(room_id, durable=True)

    # consumidor dessa sala
    async def consume():
        async with queue.iterator() as q:
            async for message in q:
                async with message.process():
                    msg = message.body.decode()

                    # envia a todos conectados
                    for conn in list(private_rooms[room_id]):
                        try:
                            await conn.send_text(msg)
                        except:
                            private_rooms[room_id].remove(conn)

    # inicia consumidor em background
    asyncio.create_task(consume())

    try:
        while True:
            text = await ws.receive_text()
            time = datetime.datetime.now(datetime.timezone.utc).strftime("%H:%M")

            final_message = f"[{time}] {username}: {text}"

            # envia msg para a fila da sala (todos recebem)
            await channel.default_exchange.publish(
                aio_pika.Message(body=final_message.encode()
                ),
                routing_key=room_id
            )

            private_collection.insert_one({
                "room_id": room_id,
                "sender": username,
                "message": text,
                "timestamp": time
            })

    except WebSocketDisconnect:
        private_rooms[room_id].remove(ws)

        # se a sala ficar vazia, pode liberar o canal opcionalmente
        if len(private_rooms[room_id]) == 0:
            del private_rooms[room_id]
            rabbit_connections.pop(room_id,None)

