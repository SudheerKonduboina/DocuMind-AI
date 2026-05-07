from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from backend.modules.summarization.summarization_schemas import SummaryResponse
from backend.modules.summarization.summarization_service import SummarizationService
from backend.database import get_db
from backend.core.dependencies import get_current_user_id


class SummarizationController:
    """Controller for summarization endpoints."""

    def __init__(self):
        self.router = APIRouter()
        self._register_routes()

    def _register_routes(self):
        """Register all summarization routes."""
        self.router.get("/{document_id}", response_model=SummaryResponse)(
            self.get_summary
        )
        self.router.post(
            "/{document_id}",
            response_model=SummaryResponse,
            status_code=status.HTTP_201_CREATED,
        )(self.generate_summary)
        self.router.post("/{document_id}/regenerate", response_model=SummaryResponse)(
            self.regenerate_summary
        )
        self.router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)(
            self.delete_summary
        )

    def get_summary(
        self,
        document_id: str,
        user_id: str = Depends(get_current_user_id),
        db: Session = Depends(get_db),
    ) -> SummaryResponse:
        """Get summary for a document."""
        service = SummarizationService(db)
        return service.get_summary(document_id, user_id)

    async def generate_summary(
        self,
        document_id: str,
        user_id: str = Depends(get_current_user_id),
        db: Session = Depends(get_db),
    ) -> SummaryResponse:
        """Generate a summary for a document."""
        service = SummarizationService(db)
        return await service.generate_summary(document_id, user_id)

    async def regenerate_summary(
        self,
        document_id: str,
        user_id: str = Depends(get_current_user_id),
        db: Session = Depends(get_db),
    ) -> SummaryResponse:
        """Regenerate summary for a document."""
        service = SummarizationService(db)
        return await service.regenerate_summary(document_id, user_id)

    def delete_summary(
        self,
        document_id: str,
        user_id: str = Depends(get_current_user_id),
        db: Session = Depends(get_db),
    ) -> None:
        """Delete summary for a document."""
        service = SummarizationService(db)
        service.delete_summary(document_id, user_id)


summarization_controller = SummarizationController()
router = summarization_controller.router
