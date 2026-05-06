from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import Optional
import json
from backend.modules.chatbot.chatbot_schemas import (
    ChatCreate,
    ChatResponse,
    ChatListResponse,
    MessageCreate,
    MessageRequest,
    MessageListResponse
)
from backend.modules.chatbot.chatbot_service import ChatbotService
from database import get_db
from core.dependencies import get_current_user_id


class ChatbotController:
    """Controller for chatbot endpoints."""
    
    def __init__(self):
        self.router = APIRouter()
        self._register_routes()
    
    def _register_routes(self):
        """Register all chatbot routes."""
        self.router.post("", response_model=ChatResponse, status_code=status.HTTP_201_CREATED)(self.create_chat)
        self.router.get("", response_model=ChatListResponse)(self.list_chats)
        self.router.get("/{chat_id}", response_model=ChatResponse)(self.get_chat)
        self.router.delete("/{chat_id}", status_code=status.HTTP_204_NO_CONTENT)(self.delete_chat)
        self.router.get("/{chat_id}/messages", response_model=MessageListResponse)(self.get_messages)
        self.router.post("/{chat_id}/messages")(self.send_message)
    
    def create_chat(
        self,
        chat_data: ChatCreate,
        user_id: str = Depends(get_current_user_id),
        db: Session = Depends(get_db)
    ) -> ChatResponse:
        """Create a new chat session."""
        service = ChatbotService(db)
        return service.create_chat(chat_data, user_id)
    
    def list_chats(
        self,
        document_id: Optional[str] = None,
        user_id: str = Depends(get_current_user_id),
        db: Session = Depends(get_db)
    ) -> ChatListResponse:
        """List user's chats."""
        service = ChatbotService(db)
        chats = service.list_chats(user_id, document_id)
        return ChatListResponse(items=chats)
    
    def get_chat(
        self,
        chat_id: str,
        user_id: str = Depends(get_current_user_id),
        db: Session = Depends(get_db)
    ) -> ChatResponse:
        """Get chat by ID."""
        service = ChatbotService(db)
        return service.get_chat(chat_id, user_id)
    
    def delete_chat(
        self,
        chat_id: str,
        user_id: str = Depends(get_current_user_id),
        db: Session = Depends(get_db)
    ) -> None:
        """Delete a chat."""
        service = ChatbotService(db)
        service.delete_chat(chat_id, user_id)
    
    def get_messages(
        self,
        chat_id: str,
        user_id: str = Depends(get_current_user_id),
        db: Session = Depends(get_db)
    ) -> MessageListResponse:
        """Get all messages for a chat."""
        service = ChatbotService(db)
        messages = service.get_messages(chat_id, user_id)
        return MessageListResponse(messages=messages)
    
    async def send_message(
        self,
        chat_id: str,
        message_data: MessageRequest,
        user_id: str = Depends(get_current_user_id),
        db: Session = Depends(get_db)
    ) -> StreamingResponse:
        """Send a message and get streaming response."""
        service = ChatbotService(db)
        
        async def generate():
            async for chunk in service.send_message(chat_id, message_data.content, user_id):
                yield f"data: {chunk.model_dump_json()}\n\n"
        
        return StreamingResponse(
            generate(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
            }
        )


chatbot_controller = ChatbotController()
router = chatbot_controller.router
