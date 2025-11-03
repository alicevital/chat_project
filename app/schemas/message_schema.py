from pydantic import BaseModel, Field

from typing import Optional

from datetime import datetime

from app.schemas.user_schema import UserSchema

class CreateMessage(BaseModel):
    name_user: UserSchema
    data_send: datetime
    message: str

class MessageSchema(BaseModel):
    id: Optional[str] = Field(default=None, description="ID gerado pelo MongoDB (str)")
    name_user: UserSchema
    data_send: datetime
    message: str

    model_config = {
        "from_attributes": True,
        "validate_assignment": True
    }
    