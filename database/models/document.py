"""Document model definition."""
from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base

class Document(Base):
    __tablename__ = 'documents'
    
    id = Column(Integer, primary_key=True)
    chat_id = Column(Integer, ForeignKey('chats.id', ondelete='CASCADE'))
    filename = Column(String(255))
    content = Column(Text)
    embedding_id = Column(String(255))
    
    # Relationships
    chat = relationship("Chat", back_populates="documents")