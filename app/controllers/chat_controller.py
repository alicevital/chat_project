from fastapi import APIRouter
from motor.motor_asyncio import AsyncIOMotorClient
import os

ChatRouter = APIRouter()

MONGO_URI = os.getenv("MONGO_URI")
client = AsyncIOMotorClient(MONGO_URI)
db = client["db_chat"]

@ChatRouter.get("/chat/global/history")
async def get_global_history(limit: int = 50):
    """
    Retorna as últimas mensagens do chat global.
    """
    messages = (
        await db.mensagens
        .find({"chat_id": "global"})
        .sort("timestamp", -1)
        .limit(limit)
        .to_list(length=limit)
    )

    # Inverter para mostrar do mais antigo → mais novo
    messages.reverse()
    return messages
