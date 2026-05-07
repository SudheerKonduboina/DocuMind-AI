from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Optional
from pydantic import BaseModel
from backend.modules.vector_search.vector_search_service import VectorSearchService
from backend.database import get_db
from backend.core.dependencies import get_current_user_id


class SearchRequest(BaseModel):
    """Schema for search request."""
    query: str
    top_k: int = 5


class SearchResponse(BaseModel):
    """Schema for search response."""
    results: list[dict]
    total: int


class VectorSearchController:
    """Controller for vector search endpoints."""
    
    def __init__(self):
        self.router = APIRouter()
        self._register_routes()
    
    def _register_routes(self):
        """Register all vector search routes."""
        self.router.post("/search", response_model=SearchResponse)(self.search)
        self.router.get("/stats")(self.get_stats)
    
    async def search(
        self,
        request: SearchRequest,
        user_id: str = Depends(get_current_user_id),
        db: Session = Depends(get_db)
    ) -> SearchResponse:
        """Search for similar document chunks."""
        service = VectorSearchService(db)
        results = await service.search(request.query, request.top_k, user_id)
        
        return SearchResponse(
            results=[
                {"chunk_id": chunk_id, "score": score}
                for chunk_id, score in results
            ],
            total=len(results)
        )
    
    def get_stats(
        self,
        user_id: str = Depends(get_current_user_id),
        db: Session = Depends(get_db)
    ) -> dict:
        """Get vector index statistics."""
        service = VectorSearchService(db)
        return service.get_index_stats()


vector_search_controller = VectorSearchController()
router = vector_search_controller.router
