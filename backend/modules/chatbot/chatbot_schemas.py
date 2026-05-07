from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
import uuid


class ChatBase(BaseModel):
    """Base chat schema."""
    title: Optional[str] = None


class ChatCreate(ChatBase):
    """Schema for chat creation."""
    document_id: Optional[uuid.UUID] = None


class ChatResponse(ChatBase):
    """Schema for chat response."""
    id: uuid.UUID
    user_id: uuid.UUID
    document_id: Optional[uuid.UUID] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ChatListResponse(BaseModel):
    """Schema for chat list response."""
    items: List[ChatResponse]


class MessageBase(BaseModel):
    """Base message schema."""
    role: str = Field(..., pattern=r"^(user|assistant|system)$")
    content: str


class MessageCreate(MessageBase):
    """Schema for message creation."""
    chat_id: uuid.UUID


class MessageRequest(BaseModel):
    """Schema for message request body from frontend."""
    content: str


class MessageResponse(MessageBase):
    """Schema for message response."""
    id: uuid.UUID
    chat_id: uuid.UUID
    metadata: Optional[dict] = None
    created_at: datetime
    
    class Config:
        from_attributes = True
        populate_by_name = True
    
    @classmethod
    def from_orm(cls, obj):
        """Custom from_orm to handle metadata field mapping."""
        data = {
            "id": obj.id,
            "chat_id": obj.chat_id,
            "role": obj.role,
            "content": obj.content,
            "metadata": getattr(obj, "message_metadata", None),
            "created_at": obj.created_at
        }
        return cls(**data)


class MessageListResponse(BaseModel):
    """Schema for message list response."""
    messages: List[MessageResponse]


class StreamChunk(BaseModel):
    """Schema for streaming response chunk."""
    token: str
    timestamp: Optional[float] = None
    done: bool = False


class ChatbotAnswer(BaseModel):
    """Schema for chatbot answer with timestamp."""
    answer: str
    timestamp: Optional[float] = None
    source_document: Optional[str] = None
