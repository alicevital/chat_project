from fastapi import APIRouter, Depends
from typing import List

from app.schemas.user_schema import CreateUser, UserSchema
from app.database.database import get_database
from app.repositories.user_repository import UserRepository
from app.services.user_service import UserService


UserRouter = APIRouter()


def get_db():
    db = get_database()
    try:
        yield db
    finally:
        pass



# Dependência para o Service (injeta Repository e DB)
def get_user_service(db=Depends(get_db)) -> UserService:
    repository = UserRepository(db)
    return UserService(repository)



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



@UserRouter.delete("/users/{user_id}")
def delete_user(user_id: str, service: UserService = Depends(get_user_service)):
    return service.delete_user(user_id)
