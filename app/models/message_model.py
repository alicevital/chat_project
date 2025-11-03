from pydantic import BaseModel

from typing import Optional

class MessageModel(BaseModel):
    id: str
    name_user: str
    content: str

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {str:str}
