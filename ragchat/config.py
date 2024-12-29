"""Application configuration"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Data directory
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

# Database
DATABASE_URL = f"sqlite:///{DATA_DIR}/ragapp.db"

# API Keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
HF_TOKEN = os.getenv("HF_TOKEN")

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