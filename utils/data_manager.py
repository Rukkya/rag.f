from database.db_manager import DatabaseManager
from utils.data_fetcher import DataFetcher
from utils.feed_processor import FeedProcessor
from datetime import datetime, timedelta
import asyncio

class DataManager:
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        self.data_fetcher = DataFetcher()
        self.feed_processor = FeedProcessor()
        self.update_interval = 24  # hours
    
    async def update_data(self, chat_id: str = None, model_name: str = None):
        """Update all data sources if needed"""
        try:
            # Check if update is needed
            latest_data = self.db_manager.get_latest_feed_data()
            if latest_data and latest_data.age_hours < self.update_interval:
                return
            
            # Fetch new data
            all_data = await self.data_fetcher.fetch_all_data()
            
            # Store in database
            for category, data in all_data["rss"].items():
                self.db_manager.update_feed_data("rss", category, data)
            
            for source, data in all_data["api"].items():
                self.db_manager.update_feed_data("api", source, data)
            
            # Process and embed feed data if chat_id and model_name are provided
            if chat_id and model_name:
                self.feed_processor.process_and_embed_feeds(
                    chat_id,
                    model_name,
                    all_data["rss"],
                    all_data["api"]
                )
            
        except Exception as e:
            print(f"Error updating data: {str(e)}")
    
    def get_relevant_context(self, query: str, chat_id: str = None, 
                           model_name: str = None, limit: int = 5) -> str:
        """Get relevant context from all sources"""
        try:
            # Get context from feeds
            feed_context = self.feed_processor.search_feed_data(
                chat_id, query, model_name, limit
            ) if chat_id and model_name else []
            
            # Format context
            all_context = []
            if feed_context:
                all_context.extend(feed_context)
            
            return "\n".join(all_context) if all_context else ""
            
        except Exception as e:
            print(f"Error getting context: {str(e)}")
            return ""