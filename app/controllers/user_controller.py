from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect, HTTPException, Query
from typing import List
from datetime import datetime, timedelta, timezone

from app.schemas.user_schema import CreateUser, UserSchema, LoginSchema
from app.database.database import get_database
from app.repositories.user_repository import UserRepository
from app.services.user_service import UserService
from app.services.chat_manager import manager
from app.infra.providers.hash_provider import hash_verifier
from app.main import  ALGORITHM, SECRET_KEY, ACCESS_TOKEN_EXPIRE_MINUTES
from jose import jwt, JWTError


UserRouter = APIRouter(tags=['CRUD de Usuários'])
active_connections = set()

def get_db():
    db = get_database()
    try:
        yield db
    finally:
        pass

def get_user_service(db=Depends(get_db)) -> UserService:
    repository = UserRepository(db)
    return UserService(repository)

def create_token(user_id, duration_token=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)):
    expiration_date = datetime.now(timezone.utc) + duration_token
    dic_info = {"sub": str(user_id), "exp": expiration_date}
    encoded_token = jwt.encode(dic_info, SECRET_KEY, ALGORITHM)
    return encoded_token

async def get_user_from_token_ws(token: str, db):
    try:
        payload = jwt.decode(token, SECRET_KEY, ALGORITHM)
        user_id: str = payload["sub"]
        if user_id is None:
            return None
        repository = UserRepository(db)
        user = repository.get_user_by_email(user_id)
        return user

    except JWTError:
        return None

@UserRouter.post("/users/register", response_model=UserSchema)
def create_user(user: CreateUser, service: UserService = Depends(get_user_service)):
    return service.create_user(user)



@UserRouter.get("/users", response_model=List[UserSchema])
def list_all_users(service: UserService = Depends(get_user_service)):
    return service.get_all_users()



@UserRouter.get("/users/{user_id}", response_model=UserSchema)
def get_user(user_id: str, service: UserService = Depends(get_user_service)):
    return service.get_user_by_id(user_id)



@UserRouter.put("/users/{user_id}", response_model=UserSchema)
def update_user(user: CreateUser, user_id: str, service: UserService = Depends(get_user_service)):
    return service.update_user(user_id, user)



@UserRouter.delete("/users/{user_id}", )
def delete_user(user_id: str, service: UserService = Depends(get_user_service)):
    return service.delete_user(user_id)

@UserRouter.post("/users/login")
def login(login_schema: LoginSchema, db=Depends(get_db)):
    repository = UserRepository(db)

    user = repository.get_user_by_email(login_schema.email)

    if not user or not hash_verifier(login_schema.password, user["password"]):
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    else:
        access_token = create_token(str(user["_id"]))
        return {
            "email": user["email"],
            "access_token": access_token,
            "token_type": "Bearer" 
        }
    
@UserRouter.websocket("/ws/chat")
async def websocket_endpoint(websocket: WebSocket, token: str = Query(...), db = Depends(get_db)):

    user = await get_user_from_token_ws(token, db)

    if user is None: 
        await websocket.close(code=404)
        return

    user_identifier = user["email"]

    await manager.connect_websocket(websocket)

    await manager.broadcast_message(f"{user_identifier} entrou no chat.")

    try:
        while True:
            data = await websocket.receive_text()

            msg = f"{user_identifier}: {data}"
            await manager.broadcast_message(msg)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast_message(f"{user_identifier} saiu do chat.")