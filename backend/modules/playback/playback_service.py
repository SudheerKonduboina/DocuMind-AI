from sqlalchemy.orm import Session
from typing import Optional
from backend.modules.playback.playback_schemas import PlaybackSegmentRequest, PlaybackSegmentResponse
from backend.modules.media.media_repository import TranscriptRepository, TranscriptSegmentRepository
from backend.modules.document.document_repository import DocumentRepository
from backend.core.s3_client import s3_service
from fastapi import HTTPException, status


class PlaybackService:
    """Service for playback operations."""
    
    def __init__(self, db: Session):
        self.transcript_repo = TranscriptRepository(db)
        self.segment_repo = TranscriptSegmentRepository(db)
        self.document_repo = DocumentRepository(db)
    
    async def get_playback_segment(
        self,
        document_id: str,
        user_id: str,
        request: PlaybackSegmentRequest
    ) -> PlaybackSegmentResponse:
        """
        Get playback segment for a timestamp.
        
        Args:
            document_id: Document ID
            user_id: User ID
            request: Playback segment request
        
        Returns:
            Playback segment with start/end times and transcript
        """
        # Verify document exists and belongs to user
        document = self.document_repo.get_by_id(document_id, user_id)
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )
        
        # Get transcript
        transcript = self.transcript_repo.get_by_document(document_id)
        if not transcript:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Transcript not found for this document"
            )
        
        # Calculate segment boundaries
        start_time = max(0, request.timestamp - request.duration / 2)
        end_time = min(transcript.duration_seconds or request.timestamp + request.duration, 
                      request.timestamp + request.duration / 2)
        
        # Get transcript segments within the time range
        segments = self.segment_repo.get_by_time_range(transcript.id, start_time, end_time)
        
        # Combine segment texts
        transcript_text = " ".join([segment.content for segment in segments])
        
        # Generate presigned S3 URL for the media file
        s3_url = None
        if document.s3_key:
            s3_url = await s3_service.generate_presigned_url(document.s3_key, expiration=3600)
        
        return PlaybackSegmentResponse(
            start_time=start_time,
            end_time=end_time,
            transcript=transcript_text,
            s3_url=s3_url
        )
    
    async def get_media_url(self, document_id: str, user_id: str) -> str:
        """
        Get presigned URL for media file.
        
        Args:
            document_id: Document ID
            user_id: User ID
        
        Returns:
            Presigned S3 URL
        """
        # Verify document exists and belongs to user
        document = self.document_repo.get_by_id(document_id, user_id)
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )
        
        # Generate presigned URL
        s3_url = await s3_service.generate_presigned_url(document.s3_key, expiration=3600)
        return s3_url
