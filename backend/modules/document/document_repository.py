from sqlalchemy.orm import Session
from typing import Optional, List
from backend.modules.document.document_models import Document, DocumentChunk
from backend.modules.document.document_schemas import DocumentCreate, DocumentUpdate, DocumentChunkCreate


class DocumentRepository:
    """Repository for document data access."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, document_data: DocumentCreate, user_id: str) -> Document:
        """Create a new document."""
        db_document = Document(
            user_id=user_id,
            title=document_data.title,
            file_type=document_data.file_type,
            s3_key=document_data.s3_key,
            file_size=document_data.file_size,
            status="processing"
        )
        self.db.add(db_document)
        self.db.commit()
        self.db.refresh(db_document)
        return db_document
    
    def get_by_id(self, document_id: str, user_id: str) -> Optional[Document]:
        """Get document by ID with user isolation."""
        return self.db.query(Document).filter(
            Document.id == document_id,
            Document.user_id == user_id
        ).first()
    
    def get_by_user(
        self,
        user_id: str,
        skip: int = 0,
        limit: int = 20,
        file_type: Optional[str] = None
    ) -> tuple[List[Document], int]:
        """
        Get documents by user with pagination.
        
        Returns:
            Tuple of (documents list, total count)
        """
        query = self.db.query(Document).filter(Document.user_id == user_id)
        
        if file_type:
            query = query.filter(Document.file_type == file_type)
        
        total = query.count()
        documents = query.order_by(Document.created_at.desc()).offset(skip).limit(limit).all()
        
        return documents, total
    
    def update(self, document: Document, update_data: DocumentUpdate) -> Document:
        """Update document."""
        for field, value in update_data.model_dump(exclude_unset=True).items():
            setattr(document, field, value)
        
        self.db.commit()
        self.db.refresh(document)
        return document
    
    def delete(self, document: Document) -> None:
        """Delete document."""
        self.db.delete(document)
        self.db.commit()
    
    def update_status(self, document_id: str, status: str) -> Optional[Document]:
        """Update document status."""
        document = self.db.query(Document).filter(Document.id == document_id).first()
        if document:
            document.status = status
            self.db.commit()
            self.db.refresh(document)
        return document
    
    def get_by_id_for_reprocess(self, document_id: str) -> Optional[Document]:
        """Get document by ID without user isolation (for reprocessing)."""
        import uuid
        try:
            # Convert string to UUID for proper comparison
            document_uuid = uuid.UUID(document_id)
            return self.db.query(Document).filter(Document.id == document_uuid).first()
        except (ValueError, AttributeError):
            # If conversion fails, try direct string comparison
            return self.db.query(Document).filter(Document.id == document_id).first()


class DocumentChunkRepository:
    """Repository for document chunk data access."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, chunk_data: DocumentChunkCreate) -> DocumentChunk:
        """Create a new document chunk."""
        db_chunk = DocumentChunk(
            document_id=chunk_data.document_id,
            chunk_index=chunk_data.chunk_index,
            content=chunk_data.content,
            start_page=chunk_data.start_page,
            end_page=chunk_data.end_page
        )
        self.db.add(db_chunk)
        self.db.commit()
        self.db.refresh(db_chunk)
        return db_chunk
    
    def create_batch(self, chunks_data: List[DocumentChunkCreate]) -> List[DocumentChunk]:
        """Create multiple document chunks in batch."""
        db_chunks = [
            DocumentChunk(
                document_id=chunk.document_id,
                chunk_index=chunk.chunk_index,
                content=chunk.content,
                start_page=chunk.start_page,
                end_page=chunk.end_page
            )
            for chunk in chunks_data
        ]
        self.db.add_all(db_chunks)
        self.db.commit()
        for chunk in db_chunks:
            self.db.refresh(chunk)
        return db_chunks
    
    def get_by_document(self, document_id: str) -> List[DocumentChunk]:
        """Get all chunks for a document."""
        return self.db.query(DocumentChunk).filter(
            DocumentChunk.document_id == document_id
        ).order_by(DocumentChunk.chunk_index).all()
    
    def get_by_ids(self, chunk_ids: List[str]) -> List[DocumentChunk]:
        """Get chunks by IDs."""
        return self.db.query(DocumentChunk).filter(
            DocumentChunk.id.in_(chunk_ids)
        ).all()
    
    def delete_by_document(self, document_id: str) -> int:
        """Delete all chunks for a document."""
        count = self.db.query(DocumentChunk).filter(
            DocumentChunk.document_id == document_id
        ).delete()
        self.db.commit()
        return count
