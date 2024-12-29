from chromadb.config import Settings

def get_chroma_settings():
    """Get ChromaDB settings with the latest recommended configuration"""
    return Settings(
        is_persistent=True,
        persist_directory="chroma_db",
        anonymized_telemetry=False
    )