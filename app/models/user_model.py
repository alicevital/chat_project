from pydantic import BaseModel
from typing import Optional



class UserModel(BaseModel):

    id: Optional[str] = None  
    name: str
    password: str  

    class Config:
        # Permite que o Pydantic serialize para dict para inserir no Mongo -->
        arbitrary_types_allowed = True
        json_encoders = {str: str}

