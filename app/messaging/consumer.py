# consumer.py
import json, pika, json, asyncio
from datetime import datetime
from app.database.database import get_database
from app.websocket.manager import manager
from models import MessageModel

def save_messages(data: dict):
    db = get_database()

    message = MessageModel(**data)

    db.messages.insert_one(message.dict()) 
    return message.dict()

def start_consumer():
    connection = pika.BlockingConnection(pika.ConnectionParameters("localhost"))
    channel = connection.channel()

    channel.queue_declare(queue="chat_queue", durable=True)

    def callback(ch, method, properties, body):
        data = json.loads(body)

        saved_message = save_messages(data)

        asyncio.run(manager.broadcast_json(saved_message))

    channel.basic_consume(
        queue="chat_queue",
        on_message_callback=callback,
        auto_ack=False
    )

    print("Consumer aguardando mensagens...")
    channel.start_consuming()
