from fastapi import WebSocket
from typing import Dict
from datetime import datetime
import asyncio
import json
from app.database.database import get_database
from app.models.user_model import UserModel
from app.models.message_model import MessageModel


class WebSocketManager:
    
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.lock = asyncio.Lock()

    async def connect(self, socket_id: str, websocket: WebSocket, user: UserModel):
        await websocket.accept()

        async with self.lock:
            self.active_connections[socket_id] = websocket

        db = get_database()

        existing = await db.users.find_one({"email": user.email, "connected": True})
        if existing:
            await websocket.send_text('{"message": "Usuário já conectado"}')
            self.active_connections.pop(socket_id)
            await websocket.close()
            raise Exception("Usuário já conectado")

        await db.users.update_one(
            {"email": user.email},
            {
                "$set": {
                    "connected": True,
                    "socket_id": socket_id,
                    "last_seen": datetime.utcnow(),
                }
            },
            upsert=True,
        )

        return user

    async def disconnect(self, socket_id: str):

        async with self.lock:
            self.active_connections.pop(socket_id, None)

        db = get_database()
        await db.users.update_one(
            {"socket_id": socket_id},
            {
                "$set": {
                    "connected": False,
                    "last_seen": datetime.utcnow()
                }
            }
        )

    async def send_private_message(self, message: MessageModel, socket_id: str):

        websocket = self.active_connections.get(socket_id)
        if not websocket:
            raise Exception("Conexão inativa")

        db = get_database()
        user = await db.users.find_one({"socket_id": socket_id, "connected": True})
        if not user:
            raise Exception("Usuário não conectado")

        await websocket.send_text(message.json())

    async def disconnect_user(self, socket_id: str):
        
        if socket_id in self.active_connections:
            await self.active_connections[socket_id].close()

    async def broadcast(self, message: str):
        
        db = get_database()

        async with self.lock:
            
            users_connected = db.users.find({"connected": True})
            valid_socket_ids = []
            async for user in users_connected:
                valid_socket_ids.append(user.get("socket_id"))

            for s_id in list(self.active_connections.keys()):
                if s_id not in valid_socket_ids:
                    self.active_connections.pop(s_id)

            connections = list(self.active_connections.values())

        coros = [ws.send_text(message) for ws in connections]

        if coros:
            await asyncio.gather(*coros, return_exceptions=True)


manager = WebSocketManager()
