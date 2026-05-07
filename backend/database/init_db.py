from backend.database import Base, engine
from backend.modules.auth.auth_models import User
from backend.modules.document.document_models import Document, DocumentChunk
from backend.modules.media.media_models import Transcript, TranscriptSegment
from backend.modules.chatbot.chatbot_models import Chat, ChatMessage
from backend.modules.summarization.summarization_models import Summary


def init_db():
    """Initialize database tables."""
    Base.metadata.create_all(bind=engine)


if __name__ == "__main__":
    init_db()
    print("Database tables created successfully!")
