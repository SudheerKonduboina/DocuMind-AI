from sqlalchemy.orm import Session
from typing import List, Optional
from backend.modules.playback.playback_models import PlaybackSession


class PlaybackRepository:
    """Repository for playback operations."""

    def __init__(self, db: Session):
        self.db = db

    def create_playback_session(
        self, user_id: str, document_id: str, start_time: float, end_time: float
    ) -> PlaybackSession:
        """Create a new playback session."""
        session = PlaybackSession(
            user_id=user_id,
            document_id=document_id,
            start_time=start_time,
            end_time=end_time,
        )
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        return session

    def get_playback_session(self, session_id: str) -> Optional[PlaybackSession]:
        """Get a playback session by ID."""
        return (
            self.db.query(PlaybackSession)
            .filter(PlaybackSession.id == session_id)
            .first()
        )

    def get_user_playback_sessions(self, user_id: str) -> List[PlaybackSession]:
        """Get all playback sessions for a user."""
        return (
            self.db.query(PlaybackSession)
            .filter(PlaybackSession.user_id == user_id)
            .order_by(PlaybackSession.created_at.desc())
            .all()
        )

    def update_playback_session(
        self, session_id: str, end_time: Optional[float] = None
    ) -> Optional[PlaybackSession]:
        """Update a playback session."""
        session = self.get_playback_session(session_id)
        if session and end_time:
            session.end_time = end_time
            self.db.commit()
            self.db.refresh(session)
        return session

    def delete_playback_session(self, session_id: str) -> bool:
        """Delete a playback session."""
        session = self.get_playback_session(session_id)
        if session:
            self.db.delete(session)
            self.db.commit()
            return True
        return False
