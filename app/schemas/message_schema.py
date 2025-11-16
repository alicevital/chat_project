from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class CreateMessage(BaseModel):
    chat_id: str
    sender_id: str
    recipient_id: str
    content: str
    data: datetime.now

class MessageSchema(BaseModel):
    id: Optional[str] = Field(default=None, description="ID gerado pelo Mongodb")
    chat_id: str
    sender_id: str
    recipient_id: str
    content: str
    data: datetime.now

    model_config = {
        "from_attributes": True,
        "validate_assignment": True
    }
    