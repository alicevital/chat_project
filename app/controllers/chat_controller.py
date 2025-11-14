import json
import asyncio
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException, Header
from typing import Dict, List, Optional
from jose import jwt, JWTError

from app.database.database import get_database
from app.repositories.message_repository import MessageRepository
from app.repositories.user_repository import UserRepository
from app.services.message_service import MessageService
from app.schemas.message_schema import CreateMessage, ChatMessage, MessageResponse
from app.infra.providers.rabbitmq_provider import publish_message
from app.main import SECRET_KEY, ALGORITHM


ChatRouter = APIRouter(tags=['Chat WebSocket'])

# Estrutura para gerenciar conexões ativas: {room_id: [websocket1, websocket2]}
active_connections: Dict[str, List[WebSocket]] = {}

# Mapeamento de WebSocket para user_id e room_id
websocket_info: Dict[WebSocket, Dict[str, str]] = {}


def get_db():
    db = get_database()
    try:
        yield db
    finally:
        pass


def verify_token(token: str) -> str:
    """Valida o token JWT e retorna o user_id"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise ValueError("Token inválido: user_id não encontrado")
        return user_id
    except JWTError as e:
        raise ValueError(f"Token inválido: {str(e)}")


def get_current_user_id(authorization: Optional[str] = Header(None, alias="Authorization")) -> str:
    """Extrai e valida o token JWT do header Authorization"""
    if not authorization:
        raise HTTPException(status_code=401, detail="Token não fornecido")
    
    try:
        # Remove "Bearer " se presente
        token = authorization.replace("Bearer ", "") if authorization.startswith("Bearer ") else authorization
        return verify_token(token)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))


def get_message_service():
    """Dependency para obter MessageService"""
    db = get_database()
    message_repository = MessageRepository(db)
    user_repository = UserRepository(db)
    return MessageService(message_repository, user_repository)


async def send_to_room(room_id: str, message: dict):
    """Envia mensagem para todos os WebSockets conectados na sala"""
    global active_connections
    if room_id in active_connections:
        disconnected = []
        for websocket in active_connections[room_id]:
            try:
                await websocket.send_json(message)
            except Exception as e:
                print(f"Erro ao enviar mensagem para WebSocket: {str(e)}")
                disconnected.append(websocket)
        
        # Remove conexões desconectadas
        for ws in disconnected:
            active_connections[room_id].remove(ws)
            if ws in websocket_info:
                del websocket_info[ws]
            if len(active_connections[room_id]) == 0:
                del active_connections[room_id]


@ChatRouter.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):
    """Endpoint WebSocket para chat privado"""
    global active_connections
    await websocket.accept()
    print("web socket aceito")
    user_id = None
    room_id = None
    db = get_database()
    message_repository = MessageRepository(db)
    user_repository = UserRepository(db)
    message_service = MessageService(message_repository, user_repository)
    
    try:
        # Espera pela primeira mensagem de autenticação
        auth_received = False
        print("começo do trycatch")
        
        while True:
            print("começo do while (while true)")
            data = await websocket.receive_text()
            print("antes do mensage data ", data)
            message_data = json.loads(data)
            print(message_data)
            
            # Primeira mensagem deve ser de autenticação
            if not auth_received:
                if message_data.get("type") != "auth":
                    await websocket.send_json({
                        "type": "error",
                        "message": "Primeira mensagem deve ser de autenticação com token JWT"
                    })
                    await websocket.close()
                    break
                
                try:
                    token = message_data.get("token")
                    if not token:
                        await websocket.send_json({
                            "type": "error",
                            "message": "Token JWT não fornecido"
                        })
                        await websocket.close()
                        break
                    
                    user_id = verify_token(token)
                    auth_received = True
                    
                    await websocket.send_json({
                        "type": "auth_success",
                        "message": "Autenticação realizada com sucesso",
                        "user_id": user_id
                    })
                    
                except ValueError as e:
                    await websocket.send_json({
                        "type": "error",
                        "message": str(e)
                    })
                    await websocket.close()
                    break
            
            # Mensagens subsequentes são mensagens de chat
            else:
                if message_data.get("type") != "message":
                    await websocket.send_json({
                        "type": "error",
                        "message": "Tipo de mensagem inválido"
                    })
                    continue
                
                try:
                    create_message = CreateMessage(**message_data)
                    
                    # Valida se o receiver_id é diferente do sender_id
                    if create_message.receiver_id == user_id:
                        await websocket.send_json({
                            "type": "error",
                            "message": "Você não pode enviar mensagem para si mesmo"
                        })
                        continue
                    
                    # Cria a mensagem e persiste no MongoDB
                    message_response = message_service.create_message(
                        sender_id=user_id,
                        receiver_id=create_message.receiver_id,
                        content=create_message.content
                    )
                    
                    # Obtém o room_id
                    room_id = message_response.room_id
                    
                    # Armazena informações da conexão
                    websocket_info[websocket] = {
                        "user_id": user_id,
                        "room_id": room_id
                    }
                    
                    # Adiciona WebSocket à lista de conexões ativas da sala
                    if room_id not in active_connections:
                        active_connections[room_id] = []
                    
                    if websocket not in active_connections[room_id]:
                        active_connections[room_id].append(websocket)
                        #  active_connections[id] = websocket
                    
                    # Prepara mensagem para enviar via WebSocket
                    chat_message = ChatMessage(
                        type="message",
                        room_id=room_id,
                        sender_id=user_id,
                        receiver_id=create_message.receiver_id,
                        content=create_message.content,
                        timestamp=message_response.timestamp
                    )
                    
                    # Publica no RabbitMQ (executa em thread para não bloquear)
                    message_dict = chat_message.model_dump()
                    loop = asyncio.get_event_loop()
                    await loop.run_in_executor(None, publish_message, room_id, message_dict)
                    
                    # Envia para todos os WebSockets da sala (incluindo o remetente)
                    await send_to_room(room_id, message_dict)
                    # id, mes
                except Exception as e:
                    await websocket.send_json({
                        "type": "error",
                        "message": f"Erro ao processar mensagem: {str(e)}"
                    })
    
    except WebSocketDisconnect:
        # Remove conexão ao desconectar
        if websocket in websocket_info:
            info = websocket_info[websocket]
            room_id = info.get("room_id")
            if room_id and room_id in active_connections:
                if websocket in active_connections[room_id]:
                    active_connections[room_id].remove(websocket)
                if len(active_connections[room_id]) == 0:
                    del active_connections[room_id]
            del websocket_info[websocket]
    
    except Exception as e:
        print(f"Erro na conexão WebSocket: {str(e)}")
        try:
            await websocket.close()
        except:
            pass


@ChatRouter.get("/messages/history/{receiver_id}", response_model=List[MessageResponse])
async def get_chat_history(
    receiver_id: str,
    current_user_id: str = Depends(get_current_user_id),
    service: MessageService = Depends(get_message_service)
):
    """Busca histórico de mensagens entre o usuário atual e o receiver_id"""
    try:
        # Gera o room_id
        room_id = service.get_room_id(current_user_id, receiver_id)
        # Busca histórico
        messages = service.get_chat_history(room_id)
        return messages
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))