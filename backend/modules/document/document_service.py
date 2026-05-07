from sqlalchemy.orm import Session
from typing import List, Optional
import pypdf
from backend.modules.document.document_repository import (
    DocumentRepository,
    DocumentChunkRepository,
)
from backend.modules.document.document_schemas import (
    DocumentCreate,
    DocumentResponse,
    DocumentChunkCreate,
)
from backend.core.s3_client import s3_service
from fastapi import HTTPException, status
import tempfile
import os
import asyncio
from backend.modules.media.media_service import MediaService


class DocumentService:
    """Service for document business logic."""

    def __init__(self, db: Session):
        self.document_repo = DocumentRepository(db)
        self.chunk_repo = DocumentChunkRepository(db)

    async def upload_document(
        self,
        file_path: str,
        filename: str,
        file_size: int,
        file_type: str,
        user_id: str,
        title: Optional[str] = None,
    ) -> DocumentResponse:
        """
        Upload and process a document.

        Args:
            file_path: Local file path
            filename: Original filename
            file_size: File size in bytes
            file_type: File type (pdf, audio, video)
            user_id: User ID
            title: Optional title (defaults to filename)

        Returns:
            Created document response
        """
        # Generate S3 key
        s3_key = f"{user_id}/{filename}"

        # Upload to S3
        await s3_service.upload_file(file_path, s3_key)

        # Create document record
        document_data = DocumentCreate(
            title=title or filename,
            file_type=file_type,
            s3_key=s3_key,
            file_size=file_size,
        )
        document = self.document_repo.create(document_data, user_id)

        # Process document asynchronously
        if file_type == "pdf":
            await self._process_pdf(document.id, file_path)
            # Clean up local file after PDF processing
            os.remove(file_path)
        elif file_type in ["audio", "video"]:
            # Trigger media transcription
            media_service = MediaService(self.document_repo.db)
            # Use background task to avoid blocking the upload response
            # File cleanup happens inside _process_media after transcription
            asyncio.create_task(
                self._process_media(media_service, document.id, file_path)
            )

        return DocumentResponse.model_validate(document)

    async def _process_pdf(self, document_id: str, file_path: str) -> None:
        """
        Process PDF document: extract text and create chunks.

        Args:
            document_id: Document ID
            file_path: Local PDF file path
        """
        # Extract text from PDF
        text_content = self._extract_pdf_text(file_path)

        # Chunk the text
        chunks = self._chunk_text(text_content, chunk_size=1000, overlap=200)

        # Create chunk records
        chunk_data_list = [
            DocumentChunkCreate(document_id=document_id, chunk_index=i, content=chunk)
            for i, chunk in enumerate(chunks)
        ]

        self.chunk_repo.create_batch(chunk_data_list)

        # Update document status
        self.document_repo.update_status(document_id, "completed")

    def _extract_pdf_text(self, file_path: str) -> str:
        """Extract text from PDF file."""
        text_content = []
        with open(file_path, "rb") as file:
            pdf_reader = pypdf.PdfReader(file)
            for page in pdf_reader.pages:
                text_content.append(page.extract_text())
        return "\n".join(text_content)

    def _chunk_text(
        self, text: str, chunk_size: int = 1000, overlap: int = 200
    ) -> List[str]:
        """
        Split text into overlapping chunks.

        Args:
            text: Input text
            chunk_size: Maximum chunk size in characters
            overlap: Overlap between chunks

        Returns:
            List of text chunks
        """
        chunks = []
        start = 0

        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end]
            chunks.append(chunk)
            start = end - overlap

        return chunks

    def get_document(self, document_id: str, user_id: str) -> DocumentResponse:
        """Get document by ID with user isolation."""
        document = self.document_repo.get_by_id(document_id, user_id)
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Document not found"
            )
        return DocumentResponse.model_validate(document)

    def list_documents(
        self,
        user_id: str,
        page: int = 1,
        limit: int = 20,
        file_type: Optional[str] = None,
    ) -> dict:
        """List user's documents with pagination."""
        skip = (page - 1) * limit
        documents, total = self.document_repo.get_by_user(
            user_id, skip, limit, file_type
        )

        return {
            "total": total,
            "page": page,
            "limit": limit,
            "items": [DocumentResponse.model_validate(doc) for doc in documents],
        }

    async def delete_document(self, document_id: str, user_id: str) -> None:
        """Delete document and associated data."""
        document = self.document_repo.get_by_id(document_id, user_id)
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Document not found"
            )

        # Delete from S3/local storage
        try:
            await s3_service.delete_file(document.s3_key)
        except Exception as e:
            from backend.core.logger import logger

            logger.error(f"Failed to delete file {document.s3_key}: {e}")

        # Delete chunks (for PDFs)
        self.chunk_repo.delete_by_document(document_id)

        # Delete transcript and segments (for audio/video)
        if document.file_type in ["audio", "video"]:
            from backend.modules.media.media_repository import (
                TranscriptRepository,
                TranscriptSegmentRepository,
            )

            transcript_repo = TranscriptRepository(self.document_repo.db)
            segment_repo = TranscriptSegmentRepository(self.document_repo.db)

            transcript = transcript_repo.get_by_document(document_id)
            if transcript:
                # Delete segments first
                segment_repo.delete_by_transcript(transcript.id)
                # Delete transcript
                transcript_repo.delete(transcript)

        # Delete document
        self.document_repo.delete(document)

    def get_document_chunks(self, document_id: str, user_id: str) -> List[str]:
        """Get all chunks for a document."""
        document = self.document_repo.get_by_id(document_id, user_id)
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Document not found"
            )

        chunks = self.chunk_repo.get_by_document(document_id)
        return [chunk.content for chunk in chunks]

    async def reprocess_media_document(
        self, document_id: str, user_id: str
    ) -> DocumentResponse:
        """
        Re-process a stuck audio/video document.

        Args:
            document_id: Document ID
            user_id: User ID

        Returns:
            Updated document response
        """
        document = self.document_repo.get_by_id(document_id, user_id)
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Document not found"
            )

        if document.file_type not in ["audio", "video"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only audio/video documents can be reprocessed",
            )

        # Download from S3 to local temp file
        temp_file_path = None
        try:
            temp_file_path = tempfile.mktemp(suffix=f".{document.file_type}")
            await s3_service.download_file(document.s3_key, temp_file_path)

            # Trigger transcription
            media_service = MediaService(self.document_repo.db)
            await media_service.transcribe_media(temp_file_path, document_id)

            # Update document status
            self.document_repo.update_status(document_id, "completed")

        except Exception as e:
            from backend.core.logger import logger

            logger.error(f"Media reprocessing failed for {document_id}: {str(e)}")
            self.document_repo.update_status(document_id, "failed")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Reprocessing failed: {str(e)}",
            )
        finally:
            if temp_file_path and os.path.exists(temp_file_path):
                os.remove(temp_file_path)

        return DocumentResponse.model_validate(document)

    async def _process_media(
        self, media_service: MediaService, document_id: str, file_path: str
    ) -> None:
        """
        Process audio/video: transcribe using Whisper and update status.

        Args:
            document_id: Document ID
            file_path: Local file path
        """
        try:
            # Transcribe media (this updates transcripts table)
            await media_service.transcribe_media(file_path, document_id)

            # Update document status
            self.document_repo.update_status(document_id, "completed")

            # Clean up local file after processing
            if os.path.exists(file_path):
                os.remove(file_path)

        except Exception as e:
            from backend.core.logger import logger

            logger.error(f"Media processing failed for {document_id}: {str(e)}")
            self.document_repo.update_status(document_id, "failed")
            if os.path.exists(file_path):
                os.remove(file_path)
