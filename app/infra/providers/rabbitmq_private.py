import aio_pika

rabbit_conn = None
rabbit_channel = None

async def init_rabbit():
    global rabbit_conn, rabbit_channel

    rabbit_conn = await aio_pika.connect_robust("amqp://guest:guest@rabbitmq:5672")
    rabbit_channel = await rabbit_conn.channel()

    # exchange dos chats privados
    await rabbit_channel.declare_exchange(
        "private_chat",
        aio_pika.ExchangeType.DIRECT,
        durable=True
    )