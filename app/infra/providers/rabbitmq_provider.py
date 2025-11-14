import pika
import json
import os
from typing import Callable, Optional
from pika.exceptions import AMQPConnectionError, AMQPChannelError

RABBITMQ_URI = os.getenv("RABBITMQ_URI", "amqp://guest:guest@localhost:5672")
EXCHANGE_NAME = "chat_exchange"
EXCHANGE_TYPE = "direct"

def get_rabbitmq_connection():
    """Cria e retorna uma conexão com o RabbitMQ"""
    try:
        parameters = pika.URLParameters(RABBITMQ_URI)
        connection = pika.BlockingConnection(parameters)
        return connection
    except AMQPConnectionError as e:
        raise Exception(f"Erro ao conectar ao RabbitMQ: {str(e)}")

def setup_exchange_and_queue(channel, room_id: str):
    """Configura exchange e fila para uma sala específica"""
    queue_name = f"chat_room_{room_id}"
    routing_key = f"room.{room_id}"
    
    # Declara exchange
    channel.exchange_declare(
        exchange=EXCHANGE_NAME,
        exchange_type=EXCHANGE_TYPE,
        durable=True
    )
    
    # Declara fila
    channel.queue_declare(
        queue=queue_name,
        durable=True
    )
    
    # Faz bind da fila com o exchange
    channel.queue_bind(
        exchange=EXCHANGE_NAME,
        queue=queue_name,
        routing_key=routing_key
    )
    
    return queue_name, routing_key

def publish_message(room_id: str, message: dict):
    """Publica uma mensagem na fila do RabbitMQ para uma sala específica"""
    try:
        connection = get_rabbitmq_connection()
        channel = connection.channel()
        
        queue_name, routing_key = setup_exchange_and_queue(channel, room_id)
        
        # Publica mensagem
        channel.basic_publish(
            exchange=EXCHANGE_NAME,
            routing_key=routing_key,
            body=json.dumps(message, default=str),
            properties=pika.BasicProperties(
                delivery_mode=2,  # Torna a mensagem persistente
            )
        )
        
        connection.close()
        return True
    except Exception as e:
        print(f"Erro ao publicar mensagem no RabbitMQ: {str(e)}")
        return False

def consume_messages(room_id: str, callback: Callable):
    """Consome mensagens de uma fila específica e chama o callback"""
    try:
        connection = get_rabbitmq_connection()
        channel = connection.channel()
        
        queue_name, routing_key = setup_exchange_and_queue(channel, room_id)
        
        def on_message(ch, method, properties, body):
            try:
                message = json.loads(body)
                callback(message)
                ch.basic_ack(delivery_tag=method.delivery_tag)
            except Exception as e:
                print(f"Erro ao processar mensagem: {str(e)}")
                ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
        
        channel.basic_consume(
            queue=queue_name,
            on_message_callback=on_message,
            auto_ack=False
        )
        
        return connection, channel
    except Exception as e:
        print(f"Erro ao consumir mensagens do RabbitMQ: {str(e)}")
        return None, None

