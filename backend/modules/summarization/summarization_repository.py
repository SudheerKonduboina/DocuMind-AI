from sqlalchemy.orm import Session
from typing import Optional
from backend.modules.summarization.summarization_models import Summary
from backend.modules.summarization.summarization_schemas import (
    SummaryCreate,
    SummaryUpdate,
)


class SummaryRepository:
    """Repository for summary data access."""

    def __init__(self, db: Session):
        self.db = db

    def create(self, summary_data: SummaryCreate) -> Summary:
        """Create a new summary."""
        db_summary = Summary(
            document_id=summary_data.document_id,
            user_id=summary_data.user_id,
            content=summary_data.content,
            summary_type=summary_data.summary_type,
        )
        self.db.add(db_summary)
        self.db.commit()
        self.db.refresh(db_summary)
        return db_summary

    def get_by_document(self, document_id: str, user_id: str) -> Optional[Summary]:
        """Get summary by document ID with user isolation."""
        return (
            self.db.query(Summary)
            .filter(Summary.document_id == document_id, Summary.user_id == user_id)
            .first()
        )

    def get_by_id(self, summary_id: str, user_id: str) -> Optional[Summary]:
        """Get summary by ID with user isolation."""
        return (
            self.db.query(Summary)
            .filter(Summary.id == summary_id, Summary.user_id == user_id)
            .first()
        )

    def update(self, summary: Summary, update_data: SummaryUpdate) -> Summary:
        """Update summary."""
        summary.content = update_data.content
        summary.summary_type = "on_demand"
        self.db.commit()
        self.db.refresh(summary)
        return summary

    def delete(self, summary: Summary) -> None:
        """Delete summary."""
        self.db.delete(summary)
        self.db.commit()
