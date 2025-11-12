from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class MessageCreate(BaseModel):
    chat_id: str
    remetente_id: str
    destinatario_id: Optional[str] = None
    conteudo: str

class MessageDB(MessageCreate):
    timestamp: datetime
