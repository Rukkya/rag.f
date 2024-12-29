from sqlalchemy import create_engine, exists
from sqlalchemy.orm import sessionmaker, scoped_session
from .models import Base, Chat, Message, Document, User, FeedData
from datetime import datetime
import uuid
import os
from ..config import DATABASE_URL

class DatabaseManager:
    def __init__(self):
        # Create database directory if it doesn't exist
        os.makedirs('data', exist_ok=True)
        
        # Initialize database
        self.engine = create_engine(DATABASE_URL)
        self.session_factory = sessionmaker(bind=self.engine)
        self.Session = scoped_session(self.session_factory)
        
        # Create tables
        Base.metadata.create_all(self.engine)
    
    def create_user(self, username: str, email: str):
        """Create a new user"""
        session = self.Session()
        try:
            user = User(username=username, email=email)
            session.add(user)
            session.commit()
            return user.id
        except Exception as e:
            session.rollback()
            raise
        finally:
            session.close()
    
    def create_chat(self, name: str, model: str, user_id: int = None):
        """Create a new chat"""
        session = self.Session()
        try:
            chat = Chat(
                name=name,
                model=model,
                api_key=str(uuid.uuid4())
            )
            
            if user_id:
                user = session.query(User).get(user_id)
                if user:
                    chat.participants.append(user)
            
            session.add(chat)
            session.commit()
            return chat.id, None
        except Exception as e:
            session.rollback()
            return None, str(e)
        finally:
            session.close()
    
    def get_chat_by_id(self, chat_id: int):
        """Get chat by ID"""
        session = self.Session()
        try:
            return session.query(Chat).filter(Chat.id == chat_id).first()
        finally:
            session.close()
    
    def get_chat_by_api_key(self, api_key: str):
        """Get chat by API key"""
        session = self.Session()
        try:
            return session.query(Chat).filter(Chat.api_key == api_key).first()
        finally:
            session.close()
    
    def get_latest_feed_data(self, chat_id: int):
        """Get the most recently updated feed data for a chat"""
        session = self.Session()
        try:
            return session.query(FeedData).filter(
                FeedData.chat_id == chat_id
            ).order_by(FeedData.last_updated.desc()).first()
        finally:
            session.close()
    
    def update_feed_data(self, chat_id: int, category: str, source: str, data: dict):
        """Update or create feed data"""
        session = self.Session()
        try:
            feed_data = session.query(FeedData).filter_by(
                chat_id=chat_id,
                category=category,
                source=source
            ).first()
            
            if feed_data:
                feed_data.data = data
                feed_data.last_updated = datetime.utcnow()
            else:
                feed_data = FeedData(
                    chat_id=chat_id,
                    category=category,
                    source=source,
                    data=data
                )
                session.add(feed_data)
            
            session.commit()
        finally:
            session.close()
    
    def get_all_chats(self):
        """Get all chats"""
        session = self.Session()
        try:
            return session.query(Chat).order_by(Chat.created_at.desc()).all()
        finally:
            session.close()
    
    def add_message(self, chat_id: int, role: str, content: str, user_id: int = None):
        """Add a message to a chat"""
        session = self.Session()
        try:
            message = Message(
                chat_id=chat_id,
                user_id=user_id,
                role=role,
                content=content
            )
            session.add(message)
            session.commit()
        finally:
            session.close()
    
    def get_chat_messages(self, chat_id: int):
        """Get all messages for a chat"""
        session = self.Session()
        try:
            return session.query(Message).filter(
                Message.chat_id == chat_id
            ).order_by(Message.timestamp.asc()).all()
        finally:
            session.close()
    
    def add_document(self, chat_id: int, filename: str, content: str, embedding_id: str):
        """Add a document to a chat"""
        session = self.Session()
        try:
            document = Document(
                chat_id=chat_id,
                filename=filename,
                content=content,
                embedding_id=embedding_id
            )
            session.add(document)
            session.commit()
        finally:
            session.close()