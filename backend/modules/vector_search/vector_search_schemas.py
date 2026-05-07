from pydantic import BaseModel, Field
from typing import List, Optional


class SearchRequest(BaseModel):
    """Schema for search request."""

    query: str = Field(..., description="Search query text")
    top_k: int = Field(
        default=5, ge=1, le=100, description="Number of results to return"
    )


class SearchResult(BaseModel):
    """Schema for a single search result."""

    chunk_id: str
    score: float
    content: Optional[str] = None
    document_id: Optional[str] = None


class SearchResponse(BaseModel):
    """Schema for search response."""

    results: List[SearchResult]
    total: int


class IndexStatsResponse(BaseModel):
    """Schema for index statistics."""

    total_vectors: int
    dimension: int
    index_type: str
