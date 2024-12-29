from typing import Optional
from anthropic import Anthropic
import os
from dotenv import load_dotenv

load_dotenv()

class ClaudeModel:
    def __init__(self):
        self.client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        self.model = "claude-3-sonnet-20240229"
        self.max_tokens = 4096
        self.temperature = 0.7

    def predict(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        try:
            messages = []
            
            # Add system prompt if provided
            if system_prompt:
                messages.append({
                    "role": "system",
                    "content": system_prompt
                })
            
            # Add user message
            messages.append({
                "role": "user",
                "content": prompt
            })
            
            response = self.client.messages.create(
                model=self.model,
                messages=messages,
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )
            
            return response.content[0].text
            
        except Exception as e:
            print(f"Error in Claude model: {str(e)}")
            return "I apologize, but I encountered an error. Please try again."