from typing import List

from fastapi import WebSocket

class ConnectionManager:
    '''
        Gerencia as conexões websockets
    '''

    def __init__(self):
        self.connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.connections:
            self.connections.remove(websocket)

    async def broadcast(self, message: str):
        for ws in self.connections:
            await ws.send_text(message)

manager = ConnectionManager()                        