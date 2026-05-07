from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import Optional
from backend.modules.document.document_schemas import DocumentResponse, DocumentListResponse, DocumentUpdate
from backend.modules.document.document_service import DocumentService
from backend.database import get_db
from backend.core.dependencies import get_current_user_id, get_optional_user_id
from backend.config.settings import settings
import tempfile
import os


class DocumentController:
    """Controller for document endpoints."""
    
    def __init__(self):
        self.router = APIRouter()
        self._register_routes()
    
    def _register_routes(self):
        """Register all document routes."""
        self.router.post("/upload", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)(self.upload_document)
        self.router.get("", response_model=DocumentListResponse)(self.list_documents)
        self.router.get("/{document_id}", response_model=DocumentResponse)(self.get_document)
        self.router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)(self.delete_document)
        self.router.post("/{document_id}/reprocess", response_model=DocumentResponse)(self.reprocess_document)
    
    async def upload_document(
        self,
        file: UploadFile = File(...),
        title: Optional[str] = Form(None),
        user_id: str = Depends(get_current_user_id),
        db: Session = Depends(get_db)
    ) -> DocumentResponse:
        """Upload a document (PDF, audio, or video)."""
        # Validate file size
        file_size = 0
        content = await file.read()
        file_size = len(content)
        
        if file_size > settings.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File size exceeds maximum allowed size of {settings.MAX_FILE_SIZE} bytes"
            )
        
        # Validate file type
        file_extension = file.filename.split(".")[-1].lower() if file.filename else ""
        if file_extension not in settings.ALLOWED_FILE_TYPES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File type not allowed. Allowed types: {', '.join(settings.ALLOWED_FILE_TYPES)}"
            )
        
        # Determine file type category
        if file_extension == "pdf":
            file_type = "pdf"
        elif file_extension in ["mp3", "wav", "m4a"]:
            file_type = "audio"
        elif file_extension in ["mp4", "mov", "avi"]:
            file_type = "video"
        else:
            file_type = "pdf"  # default
        
        # Save to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{file_extension}") as temp_file:
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        try:
            service = DocumentService(db)
            return await service.upload_document(
                file_path=temp_file_path,
                filename=file.filename,
                file_size=file_size,
                file_type=file_type,
                user_id=user_id,
                title=title
            )
        except Exception as e:
            # Clean up temp file on error
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to upload document: {str(e)}"
            )
    
    def list_documents(
        self,
        page: int = 1,
        limit: int = 20,
        file_type: Optional[str] = None,
        user_id: str = Depends(get_current_user_id),
        db: Session = Depends(get_db)
    ) -> DocumentListResponse:
        """List user's documents."""
        service = DocumentService(db)
        result = service.list_documents(user_id, page, limit, file_type)
        return DocumentListResponse(**result)
    
    def get_document(
        self,
        document_id: str,
        user_id: str = Depends(get_current_user_id),
        db: Session = Depends(get_db)
    ) -> DocumentResponse:
        """Get document details."""
        service = DocumentService(db)
        return service.get_document(document_id, user_id)
    
    async def delete_document(
        self,
        document_id: str,
        user_id: str = Depends(get_current_user_id),
        db: Session = Depends(get_db)
    ) -> None:
        """Delete a document."""
        service = DocumentService(db)
        await service.delete_document(document_id, user_id)
    
    async def reprocess_document(
        self,
        document_id: str,
        user_id: Optional[str] = Depends(get_optional_user_id),
        db: Session = Depends(get_db)
    ) -> DocumentResponse:
        """Re-process a stuck audio/video document."""
        # For reprocessing, if no user_id provided, use the document's owner
        service = DocumentService(db)
        if not user_id:
            # Get document first to find owner
            from backend.modules.document.document_repository import DocumentRepository
            doc_repo = DocumentRepository(db)
            document = doc_repo.get_by_id_for_reprocess(document_id)
            if not document:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Document not found"
                )
            user_id = str(document.user_id)
        return await service.reprocess_media_document(document_id, user_id)


document_controller = DocumentController()
router = document_controller.router
