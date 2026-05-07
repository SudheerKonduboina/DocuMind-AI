from sqlalchemy.orm import Session
from backend.modules.summarization.summarization_repository import SummaryRepository
from backend.modules.summarization.summarization_schemas import SummaryCreate, SummaryResponse, SummaryUpdate
from backend.modules.summarization.summarization_models import Summary
from backend.modules.document.document_repository import DocumentChunkRepository
from backend.modules.media.media_repository import TranscriptRepository
from backend.core.openai_client import openai_service
from backend.core.redis_client import CacheService
from fastapi import HTTPException, status
from backend.core.redis_client import redis_client


class SummarizationService:
    """Service for summarization business logic."""
    
    def __init__(self, db: Session):
        self.summary_repo = SummaryRepository(db)
        self.chunk_repo = DocumentChunkRepository(db)
        self.transcript_repo = TranscriptRepository(db)
        self.cache_service = CacheService(redis_client)
    
    async def generate_summary(
        self,
        document_id: str,
        user_id: str,
        summary_type: str = "auto"
    ) -> SummaryResponse:
        """
        Generate a summary for a document.
        
        Args:
            document_id: Document ID
            user_id: User ID
            summary_type: Type of summary ('auto' or 'on_demand')
        
        Returns:
            Summary response
        """
        # Check cache
        cache_key = f"summary:{document_id}:{user_id}"
        cached_summary = await self.cache_service.get(cache_key)
        
        if cached_summary and summary_type == "auto":
            # Return cached summary for auto-generated
            summary_data = SummaryCreate(
                document_id=document_id,
                user_id=user_id,
                content=cached_summary,
                summary_type="auto"
            )
            summary = self.summary_repo.create(summary_data)
            return SummaryResponse.model_validate(summary)
        
        # Get document content
        content = await self._get_document_content(document_id)
        
        if not content:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No content available for summarization"
            )
        
        # Generate summary using OpenAI
        summary_text = await openai_service.summarize_text(content, max_length=500)
        
        # Create or update summary
        existing_summary = self.summary_repo.get_by_document(document_id, user_id)
        
        if existing_summary:
            summary = self.summary_repo.update(existing_summary, SummaryUpdate(content=summary_text))
        else:
            summary_data = SummaryCreate(
                document_id=document_id,
                user_id=user_id,
                content=summary_text,
                summary_type=summary_type
            )
            summary = self.summary_repo.create(summary_data)
        
        # Cache summary
        await self.cache_service.set(cache_key, summary_text, expire=86400)  # 24 hours
        
        return SummaryResponse.model_validate(summary)
    
    async def _get_document_content(self, document_id: str) -> str:
        """
        Get document content for summarization.
        
        Args:
            document_id: Document ID
        
        Returns:
            Combined text content
        """
        # Try to get document chunks first
        chunks = self.chunk_repo.get_by_document(document_id)
        if chunks:
            return "\n\n".join([chunk.content for chunk in chunks])
        
        # Try to get transcript
        transcript = self.transcript_repo.get_by_document(document_id)
        if transcript:
            return transcript.full_text
        
        return ""
    
    def get_summary(self, document_id: str, user_id: str) -> SummaryResponse:
        """Get summary for a document."""
        summary = self.summary_repo.get_by_document(document_id, user_id)
        if not summary:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Summary not found. Generate one first."
            )
        return SummaryResponse.model_validate(summary)
    
    async def regenerate_summary(self, document_id: str, user_id: str) -> SummaryResponse:
        """Regenerate summary for a document."""
        return await self.generate_summary(document_id, user_id, summary_type="on_demand")
    
    def delete_summary(self, document_id: str, user_id: str) -> None:
        """Delete summary for a document."""
        summary = self.summary_repo.get_by_document(document_id, user_id)
        if summary:
            self.summary_repo.delete(summary)
