from sqlalchemy.orm import Session
from typing import List, Optional, AsyncGenerator
import re
from backend.modules.chatbot.chatbot_repository import ChatRepository, MessageRepository
from backend.modules.chatbot.chatbot_schemas import (
    ChatCreate,
    ChatResponse,
    MessageCreate,
    MessageResponse,
    StreamChunk
)
from backend.modules.chatbot.chatbot_models import Chat
from backend.modules.vector_search.vector_search_service import VectorSearchService
from backend.modules.document.document_models import DocumentChunk
from backend.modules.document.document_repository import DocumentChunkRepository
from backend.modules.media.media_repository import TranscriptSegmentRepository
from backend.core.openai_client import openai_service
from backend.core.redis_client import CacheService, redis_client
from fastapi import HTTPException, status
import json
from backend.core.logger import logger


class ChatbotService:
    """Service for chatbot business logic with RAG."""
    
    def __init__(self, db: Session):
        self.db = db
        self.chat_repo = ChatRepository(db)
        self.message_repo = MessageRepository(db)
        self.chunk_repo = DocumentChunkRepository(db)
        self.segment_repo = TranscriptSegmentRepository(db)
        self.cache_service = CacheService(redis_client)
    
    def create_chat(
        self,
        chat_data: ChatCreate,
        user_id: str
    ) -> ChatResponse:
        """Create a new chat session."""
        chat = self.chat_repo.create(chat_data, user_id)
        logger.info(f"Chat created: {chat.id} for user: {user_id}")
        return ChatResponse.model_validate(chat)
    
    def get_chat(self, chat_id: str, user_id: str) -> ChatResponse:
        """Get chat by ID."""
        chat = self.chat_repo.get_by_id(chat_id, user_id)
        if not chat:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chat not found"
            )
        return ChatResponse.model_validate(chat)
    
    def list_chats(
        self,
        user_id: str,
        document_id: Optional[str] = None
    ) -> List[ChatResponse]:
        """List user's chats."""
        chats = self.chat_repo.get_by_user(user_id, document_id)
        return [ChatResponse.model_validate(chat) for chat in chats]
    
    def delete_chat(self, chat_id: str, user_id: str) -> None:
        """Delete a chat."""
        chat = self.chat_repo.get_by_id(chat_id, user_id)
        if not chat:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chat not found"
            )
        self.message_repo.delete_by_chat(chat_id)
        self.chat_repo.delete(chat)
    
    def get_messages(self, chat_id: str, user_id: str) -> List[MessageResponse]:
        """Get all messages for a chat."""
        chat = self.chat_repo.get_by_id(chat_id, user_id)
        if not chat:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chat not found"
            )
        
        messages = self.message_repo.get_by_chat(chat_id)
        return [MessageResponse.from_orm(msg) for msg in messages]
    
    MAX_MESSAGE_LENGTH = 1500
    MAX_CONTEXT_LENGTH = 2500
    MAX_HISTORY_MESSAGES = 8
    MAX_TOTAL_TOKENS_ESTIMATE = 10000

    async def send_message(
        self,
        chat_id: str,
        content: str,
        user_id: str
    ) -> AsyncGenerator[StreamChunk, None]:
        """
        Send a message and get streaming response.
        
        Args:
            chat_id: Chat ID
            content: User message
            user_id: User ID
        
        Yields:
            StreamChunk with tokens
        """
        # Verify chat exists and belongs to user
        chat = self.chat_repo.get_by_id(chat_id, user_id)
        if not chat:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chat not found"
            )
        
        # Truncate and save user message
        if len(content) > self.MAX_MESSAGE_LENGTH * 2:
            content = content[:self.MAX_MESSAGE_LENGTH * 2] + "\n...[message truncated]"
        self.message_repo.create_with_metadata(chat_id, "user", content)
        
        # Check cache
        cache_key = f"chat:{chat_id}:{hash(content)}"
        cached_response = None
        try:
            cached_response = await self.cache_service.get(cache_key)
        except Exception as e:
            logger.warning(f"Cache get failed: {e}. Continuing without cache.")
        
        if cached_response:
            # Stream cached response
            try:
                response_data = json.loads(cached_response)
                for token in response_data["tokens"]:
                    yield StreamChunk(token=token, done=False)
                yield StreamChunk(token="", done=True)
                return
            except Exception as e:
                logger.warning(f"Failed to process cached response: {e}")
        
        # Get chat history (last N messages only)
        messages = self.message_repo.get_by_chat(chat_id)
        recent_messages = messages[-self.MAX_HISTORY_MESSAGES:]
        history = [
            {
                "role": msg.role,
                "content": msg.content[:self.MAX_MESSAGE_LENGTH] + "...[truncated]" if len(msg.content) > self.MAX_MESSAGE_LENGTH else msg.content
            }
            for msg in recent_messages
        ]
        
        # Retrieve relevant context if document is linked
        context = ""
        context_timestamp = None
        source_document = None
        if chat.document_id:
            context, context_timestamp, source_document = await self._retrieve_context(chat.document_id, content, user_id)
        
        # Build prompt with context
        system_prompt = self._build_system_prompt(context)
        
        # Prepare messages for LLM
        api_messages = [{"role": "system", "content": system_prompt}] + history

        # Token safety guard — rough char-based estimate (1 token ≈ 3-4 chars)
        total_chars = sum(len(m["content"]) for m in api_messages)
        estimated_tokens = total_chars // 3
        if estimated_tokens > self.MAX_TOTAL_TOKENS_ESTIMATE:
            logger.warning(
                f"Token estimate {estimated_tokens} exceeds limit {self.MAX_TOTAL_TOKENS_ESTIMATE}. "
                "Truncating system prompt and dropping older history messages."
            )
            # Truncate system prompt first
            system_content = api_messages[0]["content"]
            max_system_chars = self.MAX_CONTEXT_LENGTH
            api_messages[0]["content"] = system_content[:max_system_chars] + "\n...[truncated]"
            # If still too large, drop history messages from the start
            while len(api_messages) > 2 and sum(len(m["content"]) for m in api_messages) // 3 > self.MAX_TOTAL_TOKENS_ESTIMATE:
                api_messages.pop(1)
        
        # Stream response from LLM
        full_response = ""
        tokens = []
        timestamps = []
        
        stream = await openai_service.chat_completion(api_messages, stream=True)
        
        async for chunk in stream:
            if chunk.choices[0].delta.content:
                token = chunk.choices[0].delta.content
                full_response += token
                tokens.append(token)
                
                # Extract timestamp if present (format: [12.5])
                timestamp = self._extract_timestamp(token)
                if timestamp:
                    timestamps.append(timestamp)
                
                yield StreamChunk(token=token, timestamp=timestamp, done=False)
        
        # Save assistant message with metadata
        metadata = {
            "timestamps": timestamps,
            "context_timestamp": context_timestamp,
            "source_document": source_document
        } if timestamps or context_timestamp else None
        self.message_repo.create_with_metadata(chat_id, "assistant", full_response, metadata)
        
        # Cache response
        try:
            await self.cache_service.set(
                cache_key,
                json.dumps({"tokens": tokens, "metadata": metadata}),
                expire=3600
            )
        except Exception as e:
            logger.warning(f"Cache set failed: {e}")
        
        yield StreamChunk(token="", done=True)
    
    async def _retrieve_context(self, document_id: str, query: str, user_id: str) -> tuple:
        """
        Retrieve relevant context using vector search with timestamps.
        
        Args:
            document_id: Document ID
            query: User query
            user_id: User ID for security check
        
        Returns:
            Tuple of (context string, timestamp, source_document)
        """
        from backend.modules.document.document_models import Document
        
        # Get document to check if it's a video/audio (with user isolation)
        document = self.db.query(Document).filter(
            Document.id == document_id,
            Document.user_id == user_id
        ).first()
        
        # For video/audio, retrieve transcript segments directly
        if document and document.file_type in ["audio", "video"]:
            from backend.modules.media.media_repository import TranscriptRepository, TranscriptSegmentRepository
            transcript_repo = TranscriptRepository(self.db)
            segment_repo = TranscriptSegmentRepository(self.db)
            
            transcript = transcript_repo.get_by_document(document_id)
            if transcript:
                segments = segment_repo.get_by_transcript(transcript.id)
                if segments:
                    # Build context from all transcript segments
                    context_parts = []
                    for seg in segments:
                        context_parts.append(f"[{seg.start_time:.1f}s] {seg.content}")
                    
                    context = "\n\n".join(context_parts)
                    return context, segments[0].start_time if segments else None, str(document_id)
            
            # No transcript found
            return "", None, None
        
        # For PDFs, retrieve chunks directly from database
        chunks = self.db.query(DocumentChunk).filter(
            DocumentChunk.document_id == document_id
        ).order_by(DocumentChunk.chunk_index).limit(15).all()
        
        if not chunks:
            return "", None, None
        
        # Build context from all chunks
        context_parts = []
        for chunk in chunks:
            context_parts.append(chunk.content)
        
        context = "\n\n".join(context_parts)
        return context, None, str(document_id)
    
    def _build_system_prompt(self, context: str) -> str:
        """Build system prompt with context."""
        base_prompt = """You are a helpful AI assistant that answers questions about documents and media content.
Use the provided context to answer questions accurately. If the context doesn't contain the answer, say so.
When referring to specific parts of audio/video content, include timestamps in the format [timestamp]."""
        
        if context:
            if len(context) > self.MAX_CONTEXT_LENGTH:
                context = context[:self.MAX_CONTEXT_LENGTH] + "\n...[content truncated]"
            return f"{base_prompt}\n\nContext:\n{context}"
        
        return base_prompt
    
    def _extract_timestamp(self, text: str) -> Optional[float]:
        """Extract timestamp from text if present."""
        # Look for pattern like [12.5] or [1:30]
        match = re.search(r'\[(\d+(?:\.\d+)?)\]', text)
        if match:
            return float(match.group(1))
        return None
