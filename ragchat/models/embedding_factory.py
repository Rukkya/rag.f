"""Factory for creating embedding models."""
from typing import Any
from langchain_openai import OpenAIEmbeddings
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.embeddings import HuggingFaceEmbeddings
import os
from ..config import MODEL_CONFIGS

class EmbeddingFactory:
    @staticmethod
    def create_embeddings(model_name: str) -> Any:
        """Create and return appropriate embedding model based on the chat model."""
        
        # API-based embeddings
        api_embeddings = {
            "openai": lambda: OpenAIEmbeddings(
                model="text-embedding-ada-002",
                openai_api_key=os.getenv("OPENAI_API_KEY")
            ),
            "gemini": lambda: GoogleGenerativeAIEmbeddings(
                model="models/embedding-001",
                google_api_key=os.getenv("GOOGLE_API_KEY")
            ),
        }
        
        # Open source embeddings configurations
        os_embeddings = {
            "bloom": {
                "model_name": "sentence-transformers/all-mpnet-base-v2",
                "model_kwargs": {'device': 'cpu'},
                "encode_kwargs": {'normalize_embeddings': True}
            },
            "llama": {
                "model_name": "sentence-transformers/all-MiniLM-L6-v2",
                "model_kwargs": {'device': 'cpu'},
                "encode_kwargs": {'normalize_embeddings': True}
            },
            "mpt": {
                "model_name": "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
                "model_kwargs": {'device': 'cpu'},
                "encode_kwargs": {'normalize_embeddings': True}
            },
            "claude": {  # Using a good default for Claude since it doesn't have its own embeddings
                "model_name": "sentence-transformers/all-mpnet-base-v2",
                "model_kwargs": {'device': 'cpu'},
                "encode_kwargs": {'normalize_embeddings': True}
            }
        }
        
        try:
            # Check if it's an API-based model
            if model_name in api_embeddings:
                return api_embeddings[model_name]()
            
            # For open source models, use HuggingFace embeddings with appropriate config
            if model_name in os_embeddings:
                config = os_embeddings[model_name]
                return HuggingFaceEmbeddings(
                    model_name=config["model_name"],
                    model_kwargs=config["model_kwargs"],
                    encode_kwargs=config["encode_kwargs"]
                )
            
            # Default to a robust open-source embedding model
            return HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-mpnet-base-v2",
                model_kwargs={'device': 'cpu'},
                encode_kwargs={'normalize_embeddings': True}
            )
            
        except Exception as e:
            print(f"Error creating embedding model: {str(e)}")
            # Fallback to a reliable open-source model
            return HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-mpnet-base-v2",
                model_kwargs={'device': 'cpu'},
                encode_kwargs={'normalize_embeddings': True}
            )