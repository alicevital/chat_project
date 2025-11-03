from typing import List

import re

from app.repositories.message_repository import MessageRepository

from app.schemas.message_schema import CreateMessage, MessageSchema

from app.middlewares.exceptions import BadRequestError, NotFoundError, UnauthorizedError

class MessageService:

    def __init__(self, repository: MessageRepository):
        self.repository = repository

    def create_message(self, message: CreateMessage) -> MessageSchema:
        pass

    def get_all_messages(self) -> List[MessageSchema]:
        pass

    