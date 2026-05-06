from sqlalchemy.orm import Session
from typing import Optional, List
from backend.modules.chatbot.chatbot_models import Chat, ChatMessage
from backend.modules.chatbot.chatbot_schemas import ChatCreate, MessageCreate


class ChatRepository:
    """Repository for chat data access."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, chat_data: ChatCreate, user_id: str) -> Chat:
        """Create a new chat."""
        db_chat = Chat(
            user_id=user_id,
            document_id=chat_data.document_id,
            title=chat_data.title or "New Chat"
        )
        self.db.add(db_chat)
        self.db.commit()
        self.db.refresh(db_chat)
        return db_chat
    
    def get_by_id(self, chat_id: str, user_id: str) -> Optional[Chat]:
        """Get chat by ID with user isolation."""
        return self.db.query(Chat).filter(
            Chat.id == chat_id,
            Chat.user_id == user_id
        ).first()
    
    def get_by_user(self, user_id: str, document_id: Optional[str] = None) -> List[Chat]:
        """Get all chats for a user."""
        query = self.db.query(Chat).filter(Chat.user_id == user_id)
        
        if document_id:
            query = query.filter(Chat.document_id == document_id)
        
        return query.order_by(Chat.updated_at.desc()).all()
    
    def update(self, chat: Chat) -> Chat:
        """Update chat."""
        self.db.commit()
        self.db.refresh(chat)
        return chat
    
    def delete(self, chat: Chat) -> None:
        """Delete chat."""
        self.db.delete(chat)
        self.db.commit()


class MessageRepository:
    """Repository for chat message data access."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, message_data: MessageCreate) -> ChatMessage:
        """Create a new message."""
        db_message = ChatMessage(
            chat_id=message_data.chat_id,
            role=message_data.role,
            content=message_data.content
        )
        self.db.add(db_message)
        self.db.commit()
        self.db.refresh(db_message)
        return db_message
    
    def create_with_metadata(
        self,
        chat_id: str,
        role: str,
        content: str,
        metadata: Optional[dict] = None
    ) -> ChatMessage:
        """Create a message with metadata."""
        db_message = ChatMessage(
            chat_id=chat_id,
            role=role,
            content=content,
            message_metadata=metadata
        )
        self.db.add(db_message)
        self.db.commit()
        self.db.refresh(db_message)
        return db_message
    
    def get_by_chat(self, chat_id: str) -> List[ChatMessage]:
        """Get all messages for a chat."""
        return self.db.query(ChatMessage).filter(
            ChatMessage.chat_id == chat_id
        ).order_by(ChatMessage.created_at.asc()).all()
    
    def delete_by_chat(self, chat_id: str) -> int:
        """Delete all messages for a chat."""
        count = self.db.query(ChatMessage).filter(
            ChatMessage.chat_id == chat_id
        ).delete()
        self.db.commit()
        return count
