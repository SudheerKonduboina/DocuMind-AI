from sqlalchemy.orm import Session
from typing import List, Optional
from backend.modules.document.document_models import DocumentChunk
from backend.modules.media.media_models import TranscriptSegment


class VectorSearchRepository:
    """Repository for vector search operations."""

    def __init__(self, db: Session):
        self.db = db

    def get_chunk_by_id(self, chunk_id: str) -> Optional[DocumentChunk]:
        """Get a document chunk by ID."""
        return self.db.query(DocumentChunk).filter(DocumentChunk.id == chunk_id).first()

    def get_chunks_by_ids(self, chunk_ids: List[str]) -> List[DocumentChunk]:
        """Get multiple document chunks by IDs."""
        return (
            self.db.query(DocumentChunk).filter(DocumentChunk.id.in_(chunk_ids)).all()
        )

    def get_chunks_by_document(self, document_id: str) -> List[DocumentChunk]:
        """Get all chunks for a document."""
        return (
            self.db.query(DocumentChunk)
            .filter(DocumentChunk.document_id == document_id)
            .all()
        )

    def get_transcript_segment_by_id(
        self, segment_id: str
    ) -> Optional[TranscriptSegment]:
        """Get a transcript segment by ID."""
        return (
            self.db.query(TranscriptSegment)
            .filter(TranscriptSegment.id == segment_id)
            .first()
        )
