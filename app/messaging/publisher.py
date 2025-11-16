import pika, json

def publish_message(data: dict):
    connection = pika.BlockingConnection(pika.ConnectionParameters("localhost"))
    channel = connection.channel()

    channel.queue_declare(queue="chat_queue", durable=True)

    channel.basic_publish(
        exchange="",
        routing_key="chat_queue",
        body=json.dumps(data)
    )

    connection.close()
