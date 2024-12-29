from fastapi import APIRouter, HTTPException, WebSocket
from typing import List
from ..schemas.chat import ChatMessage, ChatResponse
from ..websocket import ConnectionManager
from ...database.db_manager import DatabaseManager
from ...models.model_factory import ModelFactory
from ...utils.document_processor import DocumentProcessor
from ...utils.data_manager import DataManager
from datetime import datetime

router = APIRouter()
manager = ConnectionManager()
db_manager = DatabaseManager()
doc_processor = DocumentProcessor()
data_manager = DataManager(db_manager)

@router.websocket("/ws/chat/{chat_id}")
async def websocket_endpoint(websocket: WebSocket, chat_id: int):
    try:
        await manager.connect(websocket, chat_id)
        while True:
            data = await websocket.receive_json()
            response = await process_message(chat_id, data.get("content", ""))
            await manager.broadcast_message(chat_id, response)
    except Exception as e:
        await manager.disconnect(websocket, chat_id)

@router.post("/chat/{chat_id}/messages", response_model=ChatResponse)
async def send_message(chat_id: int, message: ChatMessage):
    return await process_message(chat_id, message.content, message.role)

async def process_message(chat_id: int, content: str, role: str = "user") -> ChatResponse:
    chat = db_manager.get_chat_by_id(chat_id)
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    
    # Save user message
    db_manager.add_message(chat_id, role, content)
    
    if role == "user":
        # Get context and generate response
        doc_context = doc_processor.search_similar(str(chat_id), content, chat.model)
        feed_context = data_manager.get_relevant_context(content, str(chat_id), chat.model)
        context = "\n".join(doc_context + [feed_context]) if feed_context else "\n".join(doc_context)
        
        # Get model response
        model = ModelFactory.create_model(chat.model)
        prompt = f"Context: {context}\n\nQuestion: {content}"
        response = model.predict(prompt)
        
        # Save assistant message
        db_manager.add_message(chat_id, "assistant", response)
        
        return ChatResponse(
            id=chat_id,
            content=response,
            role="assistant",
            timestamp=datetime.utcnow()
        )
    
    return ChatResponse(
        id=chat_id,
        content=content,
        role=role,
        timestamp=datetime.utcnow()
    )