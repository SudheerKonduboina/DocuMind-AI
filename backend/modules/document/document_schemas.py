from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
import uuid


class DocumentBase(BaseModel):
    """Base document schema."""

    title: str = Field(..., min_length=1, max_length=500)
    file_type: str = Field(..., pattern=r"^(pdf|audio|video)$")


class DocumentCreate(DocumentBase):
    """Schema for document creation."""

    s3_key: str
    file_size: int


class DocumentUpdate(BaseModel):
    """Schema for document update."""

    title: Optional[str] = Field(None, min_length=1, max_length=500)
    status: Optional[str] = Field(None, pattern=r"^(processing|completed|failed)$")


class DocumentResponse(DocumentBase):
    """Schema for document response."""

    id: uuid.UUID
    user_id: uuid.UUID
    s3_key: str
    file_size: int
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class DocumentListResponse(BaseModel):
    """Schema for document list response."""

    total: int
    page: int
    limit: int
    items: List[DocumentResponse]


class DocumentChunkBase(BaseModel):
    """Base document chunk schema."""

    chunk_index: int
    content: str
    start_page: Optional[int] = None
    end_page: Optional[int] = None


class DocumentChunkCreate(DocumentChunkBase):
    """Schema for document chunk creation."""

    document_id: uuid.UUID


class DocumentChunkResponse(DocumentChunkBase):
    """Schema for document chunk response."""

    id: uuid.UUID
    document_id: uuid.UUID
    created_at: datetime

    class Config:
        from_attributes = True
