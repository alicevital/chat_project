import asyncio
import json
import pika
from motor.motor_asyncio import AsyncIOMotorClient

MONGO_URI = "mongodb://root:root@mongo:27017"
client = AsyncIOMotorClient(MONGO_URI)
db = client.db_chat
messages = db.messages  # coleção no Mongo

async def save_message(msg_data):
    await messages.insert_one(msg_data)

def callback(ch, method, properties, body):
    msg_data = json.loads(body.decode())
    asyncio.run(save_message(msg_data))

def start_consumer():
    connection = pika.BlockingConnection(pika.ConnectionParameters("rabbitmq"))
    channel = connection.channel()
    channel.queue_declare(queue="chat_messages")
    channel.basic_consume(queue="chat_messages", on_message_callback=callback, auto_ack=True)
    print(" [*] Aguardando mensagens...")
    channel.start_consuming()

if __name__ == "__main__":
    start_consumer()
