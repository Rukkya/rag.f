from pydantic import BaseModel
from datetime import datetime

class ChatMessage(BaseModel):
    content: str
    role: str = "user"

class ChatResponse(BaseModel):
    id: int
    content: str
    role: str
    timestamp: datetime