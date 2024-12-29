"""Chat model definition."""
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Table, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base

# Association table for chat participants
chat_participants = Table(
    'chat_participants',
    Base.metadata,
    Column('chat_id', Integer, ForeignKey('chats.id', ondelete='CASCADE')),
    Column('user_id', Integer, ForeignKey('users.id', ondelete='CASCADE'))
)

class Chat(Base):
    __tablename__ = 'chats'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True)
    model = Column(String(50))
    api_key = Column(String(100), unique=True, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_shared = Column(Boolean, default=False)
    
    # Relationships
    participants = relationship(
        "User",
        secondary=chat_participants,
        back_populates="chats"
    )
    messages = relationship("Message", back_populates="chat", cascade="all, delete-orphan")
    documents = relationship("Document", back_populates="chat", cascade="all, delete-orphan")
    feed_data = relationship("FeedData", back_populates="chat", cascade="all, delete-orphan")