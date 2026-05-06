from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
import uuid


class SummaryBase(BaseModel):
    """Base summary schema."""
    content: str
    summary_type: str = Field(default="auto", pattern=r"^(auto|on_demand)$")


class SummaryCreate(SummaryBase):
    """Schema for summary creation."""
    document_id: uuid.UUID
    user_id: uuid.UUID


class SummaryUpdate(BaseModel):
    """Schema for summary update."""
    content: str


class SummaryResponse(SummaryBase):
    """Schema for summary response."""
    id: uuid.UUID
    document_id: uuid.UUID
    user_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
