from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from fastapi import Depends
from datetime import datetime
from models.user_model import UserModel
from models.message_model import MessageModel
from server.db import get_db
from websocket.manager import manager

router = APIRouter(prefix="/ws", tags=["WebSocket"])

@router.websocket("/connect/{socket_id}")
async def websocket_endpoint(websocket: WebSocket, socket_id: str):
 
    await websocket.accept()

    try:
        user_data = await websocket.receive_json()
        user = UserModel(**user_data)

        await manager.connect(socket_id, websocket, user)

        while True:
            data = await websocket.receive_text()
            print(f"Mensagem recebida do socket {socket_id}: {data}")

    except WebSocketDisconnect:
        print(f"Socket {socket_id} desconectou")
        await manager.disconnect(socket_id)

    except Exception as e:
        print("Erro:", e)
        await manager.disconnect(socket_id)
        await websocket.close()

@router.post("/send")
async def send_private_message(message: MessageModel):

    db = get_db()
    
    dest = await db.users.find_one({"_id": message.destinatario_id})
    if not dest or "socket_id" not in dest:
        return {"error": "Destinatário não encontrado ou offline"}

    socket_dest = dest["socket_id"]

    await manager.send_private_message(message, socket_dest)

    await db.messages.insert_one(message.dict())

    return {"status": "mensagem enviada"}


@router.post("/broadcast")
async def broadcast_message(payload: dict):
    
    msg = payload.get("message", "")
    await manager.broadcast(msg)
    return {"status": "broadcast enviado"}
