from typing import List
from bson import ObjectId

from app.repositories.user_repository import UserRepository
from app.schemas.user_schema import CreateUser, UserSchema
from app.middlewares.exceptions import BadRequestError, NotFoundError



class UserService:

    def __init__(self, repository: UserRepository):
        self.repository = repository



    def create_user(self, user: CreateUser) -> UserSchema:

        try:
            user_created = self.repository.create_user(user)

            if not user_created:
                raise BadRequestError("user não criado, verifique credenciais")
            
            return UserSchema(
                name=user_created["name"],
                email= user_created["email"],
                password=user_created["password"]
            )
        
        except Exception as e:
            raise BadRequestError(f"Erro ao criar user: {str(e)}")



    def get_all_users(self) -> List[UserSchema]:

        try:

            users = self.repository.get_all_users()

            for doc in users:

                return [
                    UserSchema(
                        id=str(doc["_id"]),
                        name=doc["name"],
                        email=doc["email"],
                        password=doc["password"]
                    ) 
                ]
        
        except Exception as e:
            raise Exception(f"Erro ao listar users: {str(e)}")



    def get_user_by_id(self, user_id: str) -> UserSchema:

        try:

            user = self.repository.get_user_by_id(user_id)

            if not user:
                raise NotFoundError(user_id)
            
            return UserSchema(
                id=str(user["_id"]),
                name=user["name"],
                email=user["email"],
                password=user["password"]
            )
        
        except Exception as e:
            raise Exception(f"Erro ao buscar user: {str(e)}")



    def update_user(self, user_id: str, user: CreateUser) -> UserSchema:
        
        try:

            if not self.repository.update_user(user_id, user):
                raise NotFoundError(user_id)
            
            updated_user = self.repository.get_user_by_id(user_id)

            return UserSchema(
                id=user_id,
                name=updated_user["name"],
                email=updated_user["email"],
                password=updated_user["password"]
            )
        
        except Exception as e:
            raise Exception(f"Erro ao atualizar user: {str(e)}")



    def delete_user(self, user_id: str) -> dict:

        try:

            if not self.repository.delete_user(user_id):
                raise NotFoundError(user_id)
            
            return {"mensagem": "user deletado com sucesso"}
        
        except Exception as e:
            raise Exception(f"Erro ao deletar user: {str(e)}")
