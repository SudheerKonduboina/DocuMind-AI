from sqlalchemy.orm import Session
from typing import List, Optional
import pypdf
from backend.modules.document.document_repository import DocumentRepository, DocumentChunkRepository
from backend.modules.document.document_schemas import DocumentCreate, DocumentUpdate, DocumentResponse, DocumentChunkCreate
from backend.modules.document.document_models import Document
from core.s3_client import s3_service
from core.openai_client import openai_service
from fastapi import HTTPException, status
import tempfile
import os


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
        title: Optional[str] = None
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
            file_size=file_size
        )
        document = self.document_repo.create(document_data, user_id)
        
        # Process document asynchronously
        if file_type == "pdf":
            await self._process_pdf(document.id, file_path)
        
        # Clean up local file
        os.remove(file_path)
        
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
            DocumentChunkCreate(
                document_id=document_id,
                chunk_index=i,
                content=chunk
            )
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
    
    def _chunk_text(self, text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
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
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )
        return DocumentResponse.model_validate(document)
    
    def list_documents(
        self,
        user_id: str,
        page: int = 1,
        limit: int = 20,
        file_type: Optional[str] = None
    ) -> dict:
        """List user's documents with pagination."""
        skip = (page - 1) * limit
        documents, total = self.document_repo.get_by_user(user_id, skip, limit, file_type)
        
        return {
            "total": total,
            "page": page,
            "limit": limit,
            "items": [DocumentResponse.model_validate(doc) for doc in documents]
        }
    
    def delete_document(self, document_id: str, user_id: str) -> None:
        """Delete document and associated data."""
        document = self.document_repo.get_by_id(document_id, user_id)
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )
        
        # Delete from S3
        import asyncio
        asyncio.create_task(s3_service.delete_file(document.s3_key))
        
        # Delete chunks
        self.chunk_repo.delete_by_document(document_id)
        
        # Delete document
        self.document_repo.delete(document)
    
    def get_document_chunks(self, document_id: str, user_id: str) -> List[str]:
        """Get all chunks for a document."""
        document = self.document_repo.get_by_id(document_id, user_id)
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )
        
        chunks = self.chunk_repo.get_by_document(document_id)
        return [chunk.content for chunk in chunks]
