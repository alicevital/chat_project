from typing import List, Optional
from datetime import datetime
from bson import ObjectId
from app.models.message_model import MessageModel


class MessageRepository:
    """Repositório para operações de mensagens no MongoDB"""

    def __init__(self, db):
        self.db = db

    def create_message(self, message: MessageModel) -> dict:
        """Insere uma mensagem no MongoDB"""
        message_dict = message.model_dump(exclude_unset=True)
        
        result = self.db.messages.insert_one(message_dict)
        
        if not result.inserted_id:
            raise Exception("Falha ao inserir mensagem no DB")
        
        message_dict["_id"] = result.inserted_id
        return message_dict

    def get_messages_by_room(self, room_id: str, limit: int = 100) -> List[dict]:
        """Busca mensagens de uma sala específica, ordenadas por timestamp"""
        messages = list(
            self.db.messages.find({"room_id": room_id})
            .sort("timestamp", 1)  # 1 = ascendente (mais antigas primeiro)
            .limit(limit)
        )
        return messages

    def get_or_create_room_id(self, user_id1: str, user_id2: str) -> str:
        """
        Gera um ID único para a sala privada entre dois usuários.
        Ordena os IDs para garantir que a mesma sala seja usada
        independente de quem inicia a conversa.
        """
        # Ordena os IDs para garantir consistência
        sorted_ids = sorted([user_id1, user_id2])
        room_id = f"{sorted_ids[0]}_{sorted_ids[1]}"
        return room_id

