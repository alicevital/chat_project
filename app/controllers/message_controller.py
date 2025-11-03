from fastapi import APIRouter, Depends
from typing import List
from app.schemas.message_schema import CreateMessage, MessageSchema
from app.database.database import get_database
from app.repositories.message_repository import MessageRepository

MessageRouter = APIRouter()

def get_db():
    db = get_database()
    try:
        yield db
    finally:
        pass

def get_message_service(db=Depends(get_db)) -> MessageService:
    