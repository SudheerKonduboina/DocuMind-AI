from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship
import uuid
from database import Base
from database.types import GUID
from sqlalchemy.sql import func


class Transcript(Base):
    """Transcript model for audio/video transcriptions."""
    
    __tablename__ = "transcripts"
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    document_id = Column(GUID(), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True)
    full_text = Column(String, nullable=False)
    language = Column(String(10), default="en")
    duration_seconds = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    segments = relationship("TranscriptSegment", back_populates="transcript", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Transcript(id={self.id}, document_id={self.document_id}, language={self.language})>"


class TranscriptSegment(Base):
    """Transcript segment model for timestamped text segments."""
    
    __tablename__ = "transcript_segments"
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    transcript_id = Column(GUID(), ForeignKey("transcripts.id", ondelete="CASCADE"), nullable=False, index=True)
    content = Column(String, nullable=False)
    start_time = Column(Float, nullable=False)
    end_time = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    transcript = relationship("Transcript", back_populates="segments")
    
    def __repr__(self):
        return f"<TranscriptSegment(id={self.id}, start={self.start_time}, end={self.end_time})>"
