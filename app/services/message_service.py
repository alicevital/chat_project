from datetime import datetime, timezone
from typing import List
from app.repositories.message_repository import MessageRepository
from app.repositories.user_repository import UserRepository
from app.models.message_model import MessageModel
from app.schemas.message_schema import MessageResponse
from app.middlewares.exceptions import NotFoundError, BadRequestError


class MessageService:
    """Serviço para lógica de negócio de mensagens"""

    def __init__(self, message_repository: MessageRepository, user_repository: UserRepository):
        self.message_repository = message_repository
        self.user_repository = user_repository

    def get_room_id(self, user_id1: str, user_id2: str) -> str:
        """
        Gera ou obtém o ID da sala privada entre dois usuários.
        Valida se ambos os usuários existem.
        """
        # Valida se os usuários existem
        user1 = self.user_repository.get_user_by_id(user_id1)
        user2 = self.user_repository.get_user_by_id(user_id2)
        
        if not user1:
            raise NotFoundError(f"Usuário {user_id1} não encontrado")
        
        if not user2:
            raise NotFoundError(f"Usuário {user_id2} não encontrado")
        
        # Gera o room_id
        room_id = self.message_repository.get_or_create_room_id(user_id1, user_id2)
        return room_id

    def create_message(self, sender_id: str, receiver_id: str, content: str) -> MessageResponse:

        """ Cria uma nova mensagem e persiste no MongoDB """
        
        # Valida se o conteúdo não está vazio
        if not content or not content.strip():
            raise BadRequestError("Conteúdo da mensagem não pode estar vazio")
        
        # Valida se os usuários existem
        sender = self.user_repository.get_user_by_id(sender_id)
        receiver = self.user_repository.get_user_by_id(receiver_id)
        
        if not sender:
            raise NotFoundError(f"Usuário remetente {sender_id} não encontrado")
        
        if not receiver:
            raise NotFoundError(f"Usuário destinatário {receiver_id} não encontrado")
        
        # Gera o room_id
        room_id = self.get_room_id(sender_id, receiver_id)
        
        # Cria o modelo de mensagem
        message = MessageModel(
            sender_id=sender_id,
            receiver_id=receiver_id,
            content=content.strip(),
            timestamp=datetime.now(),
            room_id=room_id
        )
        
        # Persiste no MongoDB
        try:
            message_dict = self.message_repository.create_message(message)
            
            return MessageResponse(
                id=str(message_dict["_id"]),
                sender_id=message_dict["sender_id"],
                receiver_id=message_dict["receiver_id"],
                content=message_dict["content"],
                timestamp=message_dict["timestamp"],
                room_id=message_dict["room_id"]
            )
        except Exception as e:
            raise BadRequestError(f"Erro ao criar mensagem: {str(e)}")

    def get_chat_history(self, room_id: str, limit: int = 100) -> List[MessageResponse]:
        """Busca o histórico de mensagens de uma sala"""
        try:
            messages = self.message_repository.get_messages_by_room(room_id, limit)
            
            return [
                MessageResponse(
                    id=str(msg["_id"]),
                    sender_id=msg["sender_id"],
                    receiver_id=msg["receiver_id"],
                    content=msg["content"],
                    timestamp=msg["timestamp"],
                    room_id=msg["room_id"]
                )
                for msg in messages
            ]
        except Exception as e:
            raise BadRequestError(f"Erro ao buscar histórico: {str(e)}")

