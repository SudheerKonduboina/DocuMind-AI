from sqlalchemy.orm import Session
from typing import Optional, List
from backend.modules.media.media_models import Transcript, TranscriptSegment
from backend.modules.media.media_schemas import TranscriptCreate, TranscriptSegmentCreate


class TranscriptRepository:
    """Repository for transcript data access."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, transcript_data: TranscriptCreate) -> Transcript:
        """Create a new transcript."""
        db_transcript = Transcript(
            document_id=transcript_data.document_id,
            full_text=transcript_data.full_text,
            language=transcript_data.language,
            duration_seconds=transcript_data.duration_seconds
        )
        self.db.add(db_transcript)
        self.db.commit()
        self.db.refresh(db_transcript)
        return db_transcript
    
    def get_by_document(self, document_id: str) -> Optional[Transcript]:
        """Get transcript by document ID."""
        return self.db.query(Transcript).filter(
            Transcript.document_id == document_id
        ).first()
    
    def get_by_id(self, transcript_id: str) -> Optional[Transcript]:
        """Get transcript by ID."""
        return self.db.query(Transcript).filter(Transcript.id == transcript_id).first()
    
    def update(self, transcript: Transcript) -> Transcript:
        """Update transcript."""
        self.db.commit()
        self.db.refresh(transcript)
        return transcript
    
    def delete(self, transcript: Transcript) -> None:
        """Delete transcript."""
        self.db.delete(transcript)
        self.db.commit()


class TranscriptSegmentRepository:
    """Repository for transcript segment data access."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, segment_data: TranscriptSegmentCreate) -> TranscriptSegment:
        """Create a new transcript segment."""
        db_segment = TranscriptSegment(
            transcript_id=segment_data.transcript_id,
            content=segment_data.content,
            start_time=segment_data.start_time,
            end_time=segment_data.end_time
        )
        self.db.add(db_segment)
        self.db.commit()
        self.db.refresh(db_segment)
        return db_segment
    
    def create_batch(self, segments_data: List[TranscriptSegmentCreate]) -> List[TranscriptSegment]:
        """Create multiple transcript segments in batch."""
        db_segments = [
            TranscriptSegment(
                transcript_id=segment.transcript_id,
                content=segment.content,
                start_time=segment.start_time,
                end_time=segment.end_time
            )
            for segment in segments_data
        ]
        self.db.add_all(db_segments)
        self.db.commit()
        for segment in db_segments:
            self.db.refresh(segment)
        return db_segments
    
    def get_by_transcript(self, transcript_id: str) -> List[TranscriptSegment]:
        """Get all segments for a transcript."""
        return self.db.query(TranscriptSegment).filter(
            TranscriptSegment.transcript_id == transcript_id
        ).order_by(TranscriptSegment.start_time).all()
    
    def get_by_time_range(
        self,
        transcript_id: str,
        start_time: float,
        end_time: float
    ) -> List[TranscriptSegment]:
        """Get segments within a time range."""
        return self.db.query(TranscriptSegment).filter(
            TranscriptSegment.transcript_id == transcript_id,
            TranscriptSegment.start_time >= start_time,
            TranscriptSegment.end_time <= end_time
        ).order_by(TranscriptSegment.start_time).all()
    
    def delete_by_transcript(self, transcript_id: str) -> int:
        """Delete all segments for a transcript."""
        count = self.db.query(TranscriptSegment).filter(
            TranscriptSegment.transcript_id == transcript_id
        ).delete()
        self.db.commit()
        return count
