from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class MessageModel(BaseModel):
    """Modelo de mensagem para persistência no MongoDB"""
    sender_id: str
    receiver_id: str
    content: str
    timestamp: datetime
    room_id: str

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class MessagePrivate(BaseModel):
    pass