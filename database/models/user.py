"""User model definition."""
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base
from .chat import chat_participants

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(100), unique=True)
    email = Column(String(255), unique=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    chats = relationship(
        "Chat",
        secondary=chat_participants,
        back_populates="participants"
    )