from pydantic import BaseModel, Field
from typing import Optional


class PlaybackSegmentRequest(BaseModel):
    """Schema for playback segment request."""

    timestamp: float = Field(..., ge=0)
    duration: float = Field(default=30.0, ge=1, le=300)


class PlaybackSegmentResponse(BaseModel):
    """Schema for playback segment response."""

    start_time: float
    end_time: float
    transcript: str
    s3_url: Optional[str] = None
