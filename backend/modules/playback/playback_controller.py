from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from backend.modules.playback.playback_schemas import PlaybackSegmentRequest, PlaybackSegmentResponse
from backend.modules.playback.playback_service import PlaybackService
from database import get_db
from core.dependencies import get_current_user_id


class PlaybackController:
    """Controller for playback endpoints."""
    
    def __init__(self):
        self.router = APIRouter()
        self._register_routes()
    
    def _register_routes(self):
        """Register all playback routes."""
        self.router.get("/{document_id}/segment", response_model=PlaybackSegmentResponse)(self.get_playback_segment)
        self.router.get("/{document_id}/url")(self.get_media_url)
    
    async def get_playback_segment(
        self,
        document_id: str,
        timestamp: float = Query(..., ge=0),
        duration: float = Query(30.0, ge=1, le=300),
        user_id: str = Depends(get_current_user_id),
        db: Session = Depends(get_db)
    ) -> PlaybackSegmentResponse:
        """Get playback segment for a timestamp."""
        service = PlaybackService(db)
        request = PlaybackSegmentRequest(timestamp=timestamp, duration=duration)
        return await service.get_playback_segment(document_id, user_id, request)
    
    async def get_media_url(
        self,
        document_id: str,
        user_id: str = Depends(get_current_user_id),
        db: Session = Depends(get_db)
    ) -> dict:
        """Get presigned URL for media file."""
        service = PlaybackService(db)
        s3_url = await service.get_media_url(document_id, user_id)
        return {"url": s3_url}


playback_controller = PlaybackController()
router = playback_controller.router
