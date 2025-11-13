from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class MessageModel(BaseModel):
    chat_id: str
    remetente_id: str
    destinatario_id: Optional[str] = None
    conteudo: str
    data: datetime.now

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {str: str}
