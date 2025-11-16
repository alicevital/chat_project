from typing import List
import re
from app.infra.providers.hash_provider import hash_generator, hash_verifier
from app.repositories.user_repository import UserRepository
from app.schemas.user_schema import CreateUser, UserSchema
from app.middlewares.exceptions import BadRequestError, NotFoundError, UnauthorizedError, InternalServerError



class UserService:

    def __init__(self, repository: UserRepository):
        self.repository = repository

    def create_user(self, user: CreateUser) -> UserSchema:

        # Verifica se já existe um email desse no db, caso já exista, não continuar codigo
        if self.repository.get_user_by_email(user.email):
            raise UnauthorizedError("Usuário já existente")
        
        
        # Verifica se há o padrão certo do email
        if not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', user.email):
            raise BadRequestError("E mail inválido")
        

        hashed_password = hash_generator(user.password)


        if hash_verifier(user.password, hashed_password) == False:
            raise InternalServerError("Senha não verificada")
        
        user.password = hashed_password
    

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
            list = []
            
            if not users:
                return BadRequestError("Não Há Usuários")
            
            for doc in users:
                list.append(
                    UserSchema(
                        id=str(doc["_id"]),
                        name=doc["name"],
                        email=doc["email"],
                        password=doc["password"]
                    ) 
                )
            return list
        
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

        updated_user = self.repository.get_user_by_id(user_id)

        if not updated_user:
            raise BadRequestError("")


         # Verifica se há o padrão certo do email
        if not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', user.email):
            raise BadRequestError("E mail inválido")
        

        if not self.repository.get_user_by_id(user_id)["email"] == user.email:
                # Verifica se já existe um email desse no db, caso já exista, não continuar codigo
                if self.repository.get_user_by_email(user.email):
                    raise UnauthorizedError("Usuário já existente")
        

        hashed_password = hash_generator(user.password)


        if hash_verifier(user.password, hashed_password) == False:
            raise InternalServerError("Senha não verificada")
        
        user.password = hashed_password
        
        
        try:      

            if not self.repository.update_user(user_id, user):
                raise NotFoundError(user_id)
                    

            return UserSchema(
                id=user_id,
                name= user.name,
                email= user.email,
                password= user.password
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
