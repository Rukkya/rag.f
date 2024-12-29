"""Feed data model definition."""
from sqlalchemy import Column, Integer, String, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base

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
        """Calculate the age of the feed data in hours."""
        if self.last_updated:
            delta = datetime.utcnow() - self.last_updated
            return delta.total_seconds() / 3600
        return float('inf')