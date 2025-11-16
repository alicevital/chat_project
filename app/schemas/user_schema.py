from pydantic import BaseModel, Field
from typing import Optional

# Schema criar usuário (sem ID)
class CreateUser(BaseModel):
    name: str
    email: str
    password: str

# Schema resposta (com ID como str opcional)
class UserSchema(BaseModel):
    id: Optional[str] = Field(default=None, description="ID gerado pelo MongoDB (str)")
    name: str
    email: str
    password: str

    model_config = {
        "from_attributes": True,  # Pydantic v2: permite criar de dicts (ex: do Mongo)
        "validate_assignment": True  # Valida ao atribuir valores
    }

class LoginSchema(BaseModel):
    email: str
    password: str