"""Application configuration settings."""
import os
from pathlib import Path
from dotenv import load_dotenv
from chromadb.config import Settings

# Load environment variables
load_dotenv()

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Data directory
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

# Database
DATABASE_URL = f"sqlite:///{DATA_DIR}/ragapp.db"

# Model configurations
MODEL_CONFIGS = {
    "openai": {
        "model": "gpt-3.5-turbo",
        "temperature": 0.7
    },
    "claude": {
        "model": "claude-3-sonnet-20240229",
        "temperature": 0.7,
        "max_tokens": 4096
    },
    "gemini": {
        "model": "gemini-pro",
        "temperature": 0.7
    }
}

def get_chroma_settings():
    """Get ChromaDB settings."""
    return Settings(
        is_persistent=True,
        persist_directory=str(DATA_DIR / "chroma_db"),
        anonymized_telemetry=False
    )