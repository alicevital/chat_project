from sqlalchemy import \
    Column, Integer, String, ForeignKey, DateTime

from datetime import datetime
from app.database.database import Base



class MessagesModel(Base):

    __tablename__ = "messages"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    content = Column(String(500))
    timestamp = Column(DateTime, default=datetime.now)