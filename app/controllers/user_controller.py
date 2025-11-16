from fastapi import APIRouter, Depends, WebSocket, HTTPException
from typing import List
from datetime import datetime, timedelta, timezone
from app.schemas.user_schema import CreateUser, UserSchema, LoginSchema
from app.database.database import get_database
from app.repositories.user_repository import UserRepository
from app.services.user_service import UserService
from app.infra.providers.hash_provider import hash_verifier
from main import ALGORITHM, SECRET_KEY, ACCESS_TOKEN_EXPIRE_MINUTES
from jose import jwt, JWTError


UserRouter = APIRouter(tags=['CRUD de Usuários'])
active_connections = set()

def get_db():

    '''Função que abre conexão com banco de dados, faz injeção de dependencias e fecha a conexão'''
    
    db = get_database()
    try:
        yield db
    finally:
        db.close()


def get_user_service(db=Depends(get_db)) -> UserService:

    '''Função que fornece o user_service '''

    repository = UserRepository(db)
    return UserService(repository)


def create_token(user_id, duration_token=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)):
  
    '''Função que cria token de autenticação para realização do login autenticado'''

    expiration_date = datetime.now(timezone.utc) + duration_token
    dic_info = {"sub": str(user_id), "exp": expiration_date}
    encoded_token = jwt.encode(dic_info, SECRET_KEY, ALGORITHM)
    return encoded_token


@UserRouter.post("/users/register", response_model=UserSchema)
def create_user(user: CreateUser, service: UserService = Depends(get_user_service)):

    '''Criação de usuário utilizando o modelo do CreateUser'''

    return service.create_user(user)


@UserRouter.get("/users", response_model=List[UserSchema])
def list_all_users(service: UserService = Depends(get_user_service)):
    
    '''Função que lista todos os usuários criados e armazenados'''

    return service.get_all_users()


@UserRouter.get("/users/{user_id}", response_model=UserSchema)
def get_user(user_id: str, service: UserService = Depends(get_user_service)):

    '''Função que mostrar usuário cadastrado a partir de seu id pesquisado'''

    return service.get_user_by_id(user_id)


@UserRouter.put("/users/{user_id}", response_model=UserSchema)
def update_user(user: CreateUser, user_id: str, service: UserService = Depends(get_user_service)):

    '''Função que atualiza usuário cadastrado a partir de seu id pesquisado'''

    return service.update_user(user_id, user)


@UserRouter.delete("/users/{user_id}", )
def delete_user(user_id: str, service: UserService = Depends(get_user_service)):

    '''Função que deleta usuário cadastrado a partir de seu id pesquisado'''

    return service.delete_user(user_id)


@UserRouter.post("/users/login")
def login(login_schema: LoginSchema, db=Depends(get_db)):
    ''' Utiliza o token de autenticação para logar o usuário na aplicação'''
    repository = UserRepository(db)

    user = repository.get_user_by_email(login_schema.email)

    if not user or not hash_verifier(login_schema.password, user["password"]):
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    else:
        access_token = create_token(user["_id"])
        return {
            "email": user["email"],
            "access_token": access_token,
            "token_type": "Bearer" 
        }