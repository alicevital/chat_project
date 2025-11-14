from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class AuthMessage(BaseModel):
    """Schema para primeira mensagem de autenticação via WebSocket"""
    type: str = Field(default="auth", description="Tipo da mensagem")
    token: str = Field(..., description="Token JWT para autenticação")

class CreateMessage(BaseModel):
    """Schema para criar mensagem"""
    type: str = Field(default="message", description="Tipo da mensagem")
    receiver_id: str = Field(..., description="ID do usuário destinatário")
    content: str = Field(..., min_length=1, description="Conteúdo da mensagem")

class MessageResponse(BaseModel):
    """Schema de resposta de mensagem"""
    id: Optional[str] = None
    sender_id: str
    receiver_id: str
    content: str
    timestamp: datetime
    room_id: str

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class ChatMessage(BaseModel):
    """Schema para mensagem enviada via WebSocket"""
    type: str = Field(default="message", description="Tipo da mensagem")
    room_id: str
    sender_id: str
    receiver_id: str
    content: str
    timestamp: datetime

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
