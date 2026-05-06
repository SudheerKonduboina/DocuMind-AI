from sqlalchemy.orm import Session
from typing import List, Optional
import json
import whisper
from backend.modules.media.media_repository import TranscriptRepository, TranscriptSegmentRepository
from backend.modules.media.media_schemas import (
    TranscriptCreate,
    TranscriptResponse,
    TranscriptSegmentCreate,
    TranscriptSegmentResponse,
    TranscriptWithSegmentsResponse
)
from backend.modules.media.media_models import Transcript
from core.openai_client import openai_service
from fastapi import HTTPException, status
import re
from backend.core.logger import logger


class MediaService:
    """Service for media processing business logic."""
    
    def __init__(self, db: Session):
        self.transcript_repo = TranscriptRepository(db)
        self.segment_repo = TranscriptSegmentRepository(db)
    
    async def transcribe_media(
        self,
        file_path: str,
        document_id: str,
        language: str = "en"
    ) -> TranscriptWithSegmentsResponse:
        """
        Transcribe audio/video file using local Whisper with timestamps.
        
        Args:
            file_path: Local file path
            document_id: Document ID
            language: Language code
        
        Returns:
            Transcript with timestamped segments
        """
        logger.info(f"Starting transcription for document: {document_id}")
        
        # Use local Whisper model for timestamped transcription
        try:
            model = whisper.load_model("base")
            result = model.transcribe(file_path, language=language)
            
            transcript_text = result["text"]
            segments_data = result["segments"]
            
            logger.info(f"Whisper transcription completed | segments_count: {len(segments_data)}")
            
        except Exception as e:
            logger.error(f"Whisper transcription failed: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Transcription failed: {str(e)}"
            )
        
        # Create transcript record
        transcript_data = TranscriptCreate(
            document_id=document_id,
            full_text=transcript_text,
            language=language
        )
        transcript = self.transcript_repo.create(transcript_data)
        logger.info(f"Transcript created: {transcript.id} for document: {document_id}")
        
        # Create timestamped segments from Whisper output
        segments = self._create_timestamped_segments(transcript.id, segments_data)
        
        # Update duration from actual Whisper data
        if segments_data:
            max_end_time = max(seg["end"] for seg in segments_data)
            transcript.duration_seconds = int(max_end_time)
            self.transcript_repo.update(transcript)
        
        return TranscriptWithSegmentsResponse(
            id=transcript.id,
            document_id=transcript.document_id,
            full_text=transcript.full_text,
            language=transcript.language,
            duration_seconds=transcript.duration_seconds,
            created_at=transcript.created_at,
            segments=[TranscriptSegmentResponse.model_validate(seg) for seg in segments]
        )
    
    def _create_timestamped_segments(self, transcript_id: str, whisper_segments: List[dict]) -> List:
        """
        Create transcript segments from Whisper timestamped output.
        
        Args:
            transcript_id: Transcript ID
            whisper_segments: Whisper output segments with timestamps
        
        Returns:
            List of created segment objects
        """
        segments = []
        
        for seg in whisper_segments:
            segment_data = TranscriptSegmentCreate(
                transcript_id=transcript_id,
                content=seg["text"].strip(),
                start_time=seg["start"],
                end_time=seg["end"]
            )
            
            segment = self.segment_repo.create(segment_data)
            segments.append(segment)
        
        logger.info(f"Created {len(segments)} timestamped segments")
        return segments
    
    def get_transcript(self, document_id: str) -> TranscriptWithSegmentsResponse:
        """Get transcript for a document."""
        transcript = self.transcript_repo.get_by_document(document_id)
        if not transcript:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Transcript not found"
            )
        
        segments = self.segment_repo.get_by_transcript(transcript.id)
        
        return TranscriptWithSegmentsResponse(
            id=transcript.id,
            document_id=transcript.document_id,
            full_text=transcript.full_text,
            language=transcript.language,
            duration_seconds=transcript.duration_seconds,
            created_at=transcript.created_at,
            segments=[TranscriptSegmentResponse.model_validate(seg) for seg in segments]
        )
    
    def get_transcript_segments(
        self,
        document_id: str,
        start_time: Optional[float] = None,
        end_time: Optional[float] = None
    ) -> List[TranscriptSegmentResponse]:
        """Get transcript segments, optionally filtered by time range."""
        transcript = self.transcript_repo.get_by_document(document_id)
        if not transcript:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Transcript not found"
            )
        
        if start_time is not None and end_time is not None:
            segments = self.segment_repo.get_by_time_range(transcript.id, start_time, end_time)
        else:
            segments = self.segment_repo.get_by_transcript(transcript.id)
        
        return [TranscriptSegmentResponse.model_validate(seg) for seg in segments]
    
    def delete_transcript(self, document_id: str) -> None:
        """Delete transcript for a document."""
        transcript = self.transcript_repo.get_by_document(document_id)
        if transcript:
            self.segment_repo.delete_by_transcript(transcript.id)
            self.transcript_repo.delete(transcript)
