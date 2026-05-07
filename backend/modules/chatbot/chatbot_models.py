from sqlalchemy import Column, String, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
import uuid
from backend.database import Base
from backend.database.types import GUID
from sqlalchemy.sql import func


class Chat(Base):
    """Chat model for conversation sessions."""

    __tablename__ = "chats"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    user_id = Column(
        GUID(), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    document_id = Column(
        GUID(),
        ForeignKey("documents.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    title = Column(String(500))
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    messages = relationship(
        "ChatMessage", back_populates="chat", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Chat(id={self.id}, title={self.title})>"


class ChatMessage(Base):
    """Chat message model for individual messages."""

    __tablename__ = "chat_messages"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    chat_id = Column(
        GUID(), ForeignKey("chats.id", ondelete="CASCADE"), nullable=False, index=True
    )
    role = Column(String(20), nullable=False)  # 'user', 'assistant', 'system'
    content = Column(String, nullable=False)
    message_metadata = Column(JSON, nullable=True)  # For storing timestamps, etc.
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    # Relationships
    chat = relationship("Chat", back_populates="messages")

    def __repr__(self):
        return f"<ChatMessage(id={self.id}, role={self.role})>"
