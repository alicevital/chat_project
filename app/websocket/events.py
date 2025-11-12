import asyncio
from fastapi import APIRouter, WebSocket
from app.websocket.manager import manager
from app.rabbit.broker import send_to_queue

router = APIRouter()

@router.websocket("/ws/chat")
async def websocker_chat(websocket: WebSocket):
    '''
    Cria as rotas do chat por meio de websockets
    '''
    await manager.connect(websocket)
    try:
        while True:
            mensagem= await websocket.receive_text()
            await send_to_queue(mensagem)

    except:
        manager.disconnect(websocket)