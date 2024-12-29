#!/usr/bin/env python3
import os
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from ragchat.database import DatabaseManager, Base

def init_database():
    """Initialize the database and create tables"""
    try:
        # Create data directory if it doesn't exist
        data_dir = project_root / "data"
        data_dir.mkdir(exist_ok=True)
        
        # Initialize database manager
        db_manager = DatabaseManager()
        
        # Create all tables
        Base.metadata.create_all(db_manager.engine)
        
        print("Database initialized successfully!")
        
    except Exception as e:
        print(f"Error initializing database: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    init_database()