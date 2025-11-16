async def start_global_consumer(rabbit_conn, clients):
    channel = await rabbit_conn.channel()
    queue = await channel.declare_queue("global_chat", durable=True)

    async with queue.iterator() as q:
        async for msg in q:
            async with msg.process():
                for ws in list(clients):
                    try:
                        await ws.send_text(msg.body.decode())
                    except:
                        clients.remove(ws)
