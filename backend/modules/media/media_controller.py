from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import Optional
from backend.modules.media.media_schemas import (
    TranscriptWithSegmentsResponse,
    TranscriptSegmentResponse,
)
from backend.modules.media.media_service import MediaService
from backend.database import get_db
from backend.core.dependencies import get_current_user_id


class MediaController:
    """Controller for media endpoints."""

    def __init__(self):
        self.router = APIRouter()
        self._register_routes()

    def _register_routes(self):
        """Register all media routes."""
        self.router.get(
            "/{document_id}/transcript", response_model=TranscriptWithSegmentsResponse
        )(self.get_transcript)
        self.router.get(
            "/{document_id}/segments", response_model=list[TranscriptSegmentResponse]
        )(self.get_transcript_segments)
        self.router.delete(
            "/{document_id}/transcript", status_code=status.HTTP_204_NO_CONTENT
        )(self.delete_transcript)

    def get_transcript(
        self,
        document_id: str,
        user_id: str = Depends(get_current_user_id),
        db: Session = Depends(get_db),
    ) -> TranscriptWithSegmentsResponse:
        """Get transcript for a document."""
        # Note: In production, verify user owns the document
        service = MediaService(db)
        return service.get_transcript(document_id)

    def get_transcript_segments(
        self,
        document_id: str,
        start_time: Optional[float] = None,
        end_time: Optional[float] = None,
        user_id: str = Depends(get_current_user_id),
        db: Session = Depends(get_db),
    ) -> list[TranscriptSegmentResponse]:
        """Get transcript segments, optionally filtered by time range."""
        service = MediaService(db)
        return service.get_transcript_segments(document_id, start_time, end_time)

    def delete_transcript(
        self,
        document_id: str,
        user_id: str = Depends(get_current_user_id),
        db: Session = Depends(get_db),
    ) -> None:
        """Delete transcript for a document."""
        service = MediaService(db)
        service.delete_transcript(document_id)


media_controller = MediaController()
router = media_controller.router
