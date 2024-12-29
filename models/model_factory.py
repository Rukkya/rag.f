from typing import Dict, Any
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from .claude_model import ClaudeModel
from langchain_community.llms import HuggingFacePipeline
from transformers import pipeline
import os
from dotenv import load_dotenv

load_dotenv()

class ModelFactory:
    @staticmethod
    def create_model(model_name: str) -> Any:
        models = {
            "openai": lambda: ChatOpenAI(
                model_name="gpt-3.5-turbo",
                temperature=0.7
            ),
            "gemini": lambda: ChatGoogleGenerativeAI(
                model="gemini-pro",
                google_api_key=os.getenv("GOOGLE_API_KEY"),
                temperature=0.7
            ),
            "claude": lambda: ClaudeModel(),
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
        
        return models[model_name]()