from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from fastapi import Depends
from datetime import datetime
from app.models.user_model import UserModel
from app.models.message_model import MessageModel
from app.database.database import get_database
from app.websocket.manager import manager
from app.messaging.publisher import publish_message

ws_router = APIRouter()

@ws_router.websocket("/ws/chat/global")
async def websocket_global_chat(websocket: WebSocket):
    await manager.connect(websocket)

    try:
        while True:
            data = await websocket.receive_json()

            message = MessageModel(**data)

            publish_message(message.dict())

    except WebSocketDisconnect:
        manager.disconnect(websocket)


@ws_router.get("/chat/global/history")
def get_global_chat_history():
    db = get_database()

    messages = list(
        db.messages.find({"chat_id": "global"}).sort("data", 1)
    )

    # Converter ObjectId para string
    for m in messages:
        m["_id"] = str(m["_id"])

    return messages

