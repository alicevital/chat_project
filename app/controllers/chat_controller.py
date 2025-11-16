from fastapi import WebSocket, WebSocketDisconnect, APIRouter
import datetime

PrivateRouter = APIRouter()

# salas do chat privado
private_rooms = {}  # { room_id: set(WebSocket, WebSocket) }

@PrivateRouter.websocket("/ws/private/{room_id}/{username}")
async def private_chat(ws: WebSocket, room_id: str, username: str):
    
    # cria sala se não existir
    if room_id not in private_rooms:
        private_rooms[room_id] = set()

    # 🚫 SE A SALA JÁ TEM 2 PESSOAS → RECUSAR TERCEIRO
    if len(private_rooms[room_id]) >= 2:
        await ws.accept()
        await ws.send_text("A sala está cheia: apenas 2 pessoas podem participar deste chat privado.")
        await ws.close()
        return
    
    # conecta usuário
    await ws.accept()
    private_rooms[room_id].add(ws)

    try:
        while True:
            text = await ws.receive_text()
            time = datetime.datetime.now().strftime("%H:%M")

            final_message = f"[{time}] {username}: {text}"

            # envia para todos da sala
            for conn in list(private_rooms[room_id]):
                try:
                    await conn.send_text(final_message)
                except:
                    private_rooms[room_id].remove(conn)

    except WebSocketDisconnect:
        private_rooms[room_id].remove(ws)