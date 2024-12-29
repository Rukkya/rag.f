"""RAG Chat Application Package"""

__version__ = "1.0.0"

# Import core components for easier access
from .database.db_manager import DatabaseManager
from .models.model_factory import ModelFactory
from .utils.data.manager import DataManager
from .utils.document.processor import DocumentProcessor

__all__ = [
    'DatabaseManager',
    'ModelFactory',
    'DataManager',
    'DocumentProcessor'
]