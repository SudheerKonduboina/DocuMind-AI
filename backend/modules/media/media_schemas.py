from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
import uuid


class TranscriptBase(BaseModel):
    """Base transcript schema."""
    full_text: str
    language: str = "en"
    duration_seconds: Optional[int] = None


class TranscriptCreate(TranscriptBase):
    """Schema for transcript creation."""
    document_id: uuid.UUID


class TranscriptResponse(TranscriptBase):
    """Schema for transcript response."""
    id: uuid.UUID
    document_id: uuid.UUID
    created_at: datetime
    
    class Config:
        from_attributes = True


class TranscriptSegmentBase(BaseModel):
    """Base transcript segment schema."""
    content: str
    start_time: float = Field(..., ge=0)
    end_time: float = Field(..., ge=0)


class TranscriptSegmentCreate(TranscriptSegmentBase):
    """Schema for transcript segment creation."""
    transcript_id: uuid.UUID


class TranscriptSegmentResponse(TranscriptSegmentBase):
    """Schema for transcript segment response."""
    id: uuid.UUID
    transcript_id: uuid.UUID
    created_at: datetime
    
    class Config:
        from_attributes = True


class TranscriptWithSegmentsResponse(TranscriptResponse):
    """Schema for transcript with segments."""
    segments: List[TranscriptSegmentResponse]
