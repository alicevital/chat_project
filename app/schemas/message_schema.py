from pydantic import BaseModel, Field

from typing import Optional

class CreateMessage(BaseModel):
    name_user: str
    