"""Model factory for creating language model instances."""
from typing import Any
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.llms import HuggingFacePipeline
from transformers import pipeline
from .claude_model import ClaudeModel
from ..config import MODEL_CONFIGS

load_dotenv()

class ModelFactory:
    @staticmethod
    def create_model(model_name: str) -> Any:
        """Create and return appropriate language model based on the model name."""
        
        # API-based models
        api_models = {
            "openai": lambda: ChatOpenAI(
                model_name=MODEL_CONFIGS["openai"]["model"],
                temperature=MODEL_CONFIGS["openai"]["temperature"]
            ),
            "gemini": lambda: ChatGoogleGenerativeAI(
                model=MODEL_CONFIGS["gemini"]["model"],
                google_api_key=os.getenv("GOOGLE_API_KEY"),
                temperature=MODEL_CONFIGS["gemini"]["temperature"]
            ),
            "claude": lambda: ClaudeModel(),
        }
        
        # Open source models
        os_models = {
            "bloom": lambda: HuggingFacePipeline(
                pipeline=pipeline(
                    "text-generation",
                    model="bigscience/bloom-1b7",
                    token=os.getenv("HF_TOKEN")
                )
            ),
            "llama": lambda: HuggingFacePipeline(
                pipeline=pipeline(
                    "text-generation",
                    model="meta-llama/Llama-2-7b-chat-hf",
                    token=os.getenv("HF_TOKEN")
                )
            ),
            "mpt": lambda: HuggingFacePipeline(
                pipeline=pipeline(
                    "text-generation",
                    model="mosaicml/mpt-7b",
                    token=os.getenv("HF_TOKEN")
                )
            )
        }
        
        try:
            # Check if it's an API-based model
            if model_name in api_models:
                return api_models[model_name]()
            
            # Check if it's an open source model
            if model_name in os_models:
                return os_models[model_name]()
            
            # Default to OpenAI if model not found
            print(f"Warning: Model {model_name} not found, using OpenAI as fallback")
            return api_models["openai"]()
            
        except Exception as e:
            print(f"Error creating model {model_name}: {str(e)}")
            # Fallback to OpenAI in case of error
            return api_models["openai"]()