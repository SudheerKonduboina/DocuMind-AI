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
from core.openai_client import openai_service
from core.redis_client import CacheService, redis_client
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
        return [MessageResponse.model_validate(msg) for msg in messages]
    
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
        
        # Save user message
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
        
        # Get chat history
        messages = self.message_repo.get_by_chat(chat_id)
        history = [
            {"role": msg.role, "content": msg.content}
            for msg in messages
        ]
        
        # Retrieve relevant context if document is linked
        context = ""
        context_timestamp = None
        source_document = None
        if chat.document_id:
            context, context_timestamp, source_document = await self._retrieve_context(chat.document_id, content)
        
        # Build prompt with context
        system_prompt = self._build_system_prompt(context)
        
        # Prepare messages for LLM
        api_messages = [{"role": "system", "content": system_prompt}] + history
        
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
    
    async def _retrieve_context(self, document_id: str, query: str) -> tuple:
        """
        Retrieve relevant context using vector search with timestamps.
        
        Args:
            document_id: Document ID
            query: User query
        
        Returns:
            Tuple of (context string, timestamp, source_document)
        """
        vector_service = VectorSearchService(self.db)
        
        # Search for relevant chunks
        results = await vector_service.search(query, top_k=5)
        
        if not results:
            logger.info("Vector search returned no results. Falling back to initial document chunks.")
            # Fallback: get first 5 chunks of the document
            chunks = self.db.query(DocumentChunk).filter(
                DocumentChunk.document_id == document_id
            ).order_by(DocumentChunk.chunk_index).limit(5).all()
            
            if not chunks:
                return "", None, None
            
            context = "\n\n".join([c.content for c in chunks])
            return context, getattr(chunks[0], 'start_time', None), str(document_id)
        
        # Retrieve chunk content
        chunk_ids = [r[0] for r in results]
        chunks = self.chunk_repo.get_by_ids(chunk_ids)
        
        # Build context and extract timestamp from best match
        context_parts = []
        best_timestamp = None
        source_document = None
        
        for chunk in chunks:
            context_parts.append(chunk.content)
            # Use the first chunk's timestamp as the best match
            if best_timestamp is None and hasattr(chunk, 'start_time'):
                best_timestamp = chunk.start_time
            if source_document is None and hasattr(chunk, 'document_id'):
                source_document = str(chunk.document_id)
        
        context = "\n\n".join(context_parts)
        return context, best_timestamp, source_document
    
    def _build_system_prompt(self, context: str) -> str:
        """Build system prompt with context."""
        base_prompt = """You are a helpful AI assistant that answers questions about documents and media content.
Use the provided context to answer questions accurately. If the context doesn't contain the answer, say so.
When referring to specific parts of audio/video content, include timestamps in the format [timestamp]."""
        
        if context:
            return f"{base_prompt}\n\nContext:\n{context}"
        
        return base_prompt
    
    def _extract_timestamp(self, text: str) -> Optional[float]:
        """Extract timestamp from text if present."""
        # Look for pattern like [12.5] or [1:30]
        match = re.search(r'\[(\d+(?:\.\d+)?)\]', text)
        if match:
            return float(match.group(1))
        return None
