from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class MessageModel(BaseModel):
    chat_id: str
    remetente_id: str
    destinatario_id: Optional[str] = None
    conteudo: str
    data: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {str: str}
