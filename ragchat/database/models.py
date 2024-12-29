from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Boolean, JSON, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

# Association table for chat participants
chat_participants = Table(
    'chat_participants',
    Base.metadata,
    Column('chat_id', Integer, ForeignKey('chats.id', ondelete='CASCADE')),
    Column('user_id', Integer, ForeignKey('users.id', ondelete='CASCADE'))
)

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

class Message(Base):
    __tablename__ = 'messages'
    
    id = Column(Integer, primary_key=True)
    chat_id = Column(Integer, ForeignKey('chats.id', ondelete='CASCADE'))
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    role = Column(String(20))
    content = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    chat = relationship("Chat", back_populates="messages")
    user = relationship("User")

class Document(Base):
    __tablename__ = 'documents'
    
    id = Column(Integer, primary_key=True)
    chat_id = Column(Integer, ForeignKey('chats.id', ondelete='CASCADE'))
    filename = Column(String(255))
    content = Column(Text)
    embedding_id = Column(String(255))
    
    # Relationships
    chat = relationship("Chat", back_populates="documents")

class FeedData(Base):
    __tablename__ = 'feed_data'
    
    id = Column(Integer, primary_key=True)
    chat_id = Column(Integer, ForeignKey('chats.id', ondelete='CASCADE'))
    category = Column(String(50))
    source = Column(String(100))
    data = Column(JSON)
    last_updated = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    chat = relationship("Chat", back_populates="feed_data")
    
    @property
    def age_hours(self):
        if self.last_updated:
            delta = datetime.utcnow() - self.last_updated
            return delta.total_seconds() / 3600
        return float('inf')