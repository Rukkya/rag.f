from typing import Dict, Any, List, Optional
from ...database.db_manager import DatabaseManager
from .cleaner import DataCleaner
from .fetcher import DataFetcher
from ..embedding import EmbeddingManager
from ..text import TextChunker

class DataManager:
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        self.data_fetcher = DataFetcher()
        self.cleaner = DataCleaner()
        self.chunker = TextChunker()
        self.embedding_manager = EmbeddingManager()
        self.update_interval = 24  # hours
    
    async def update_data(self, chat_id: int, model_name: str) -> None:
        """Update all data sources if needed"""
        try:
            # Check if update is needed
            latest_data = self.db_manager.get_latest_feed_data(chat_id)
            if latest_data and latest_data.age_hours < self.update_interval:
                return
            
            # Fetch new data
            all_data = await self.data_fetcher.fetch_all_data()
            
            # Process and store data
            for category, entries in all_data["rss"].items():
                cleaned_entries = []
                for entry in entries:
                    cleaned_text = self.cleaner.clean_rss_entry(entry)
                    if cleaned_text.strip():
                        cleaned_entries.append(cleaned_text)
                
                if cleaned_entries:
                    # Create embeddings
                    chunks = self.chunker.chunk_text("\n\n".join(cleaned_entries))
                    embedding_id = self.embedding_manager.create_embeddings(
                        str(chat_id),
                        chunks,
                        model_name
                    )
                    
                    # Store in database
                    self.db_manager.update_feed_data(
                        chat_id,
                        category,
                        "rss",
                        {
                            "entries": cleaned_entries,
                            "embedding_id": embedding_id
                        }
                    )
            
        except Exception as e:
            print(f"Error updating data: {str(e)}")
    
    def get_relevant_context(self, query: str, chat_id: str, model_name: str,
                           limit: int = 5) -> Optional[str]:
        """Get relevant context from all sources"""
        try:
            context = self.embedding_manager.search_similar(
                chat_id,
                query,
                model_name,
                limit
            )
            return "\n\n".join(context) if context else None
        except Exception as e:
            print(f"Error getting context: {str(e)}")
            return None