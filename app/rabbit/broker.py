import aio_pika
import os

RABBITMQ_URL = os.getenv("RABBITMQ_URL","amqp://guest:guest@rabbitmq/")

async def send_to_queue(message: str):
    connection = await aio_pika.connect_robust(RABBITMQ_URL)
    channel = await connection.channel()
    await channel.default_exchange.publish(
        aio_pika.Message(body=message.encode()),
        routing_ket="chat_queue"
    )
    await connection.close()
    