from pydantic import BaseModel

from typing import Optional

from app.schemas.user_schema import UserSchema

from datetime import datetime

class MessageModel(BaseModel):
    id: str
    name_user: UserSchema
    data_send: datetime
    message: str

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {str:str}
