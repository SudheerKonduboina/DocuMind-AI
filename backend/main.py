from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from config.settings import settings
from database import Base, engine
from core.redis_client import redis_client
from core.logging import get_logger
from database.init_db import init_db

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logger.info("Starting up AI Document Q&A API")
    try:
        # Test database connection
        with engine.connect() as conn:
            logger.info("Database connection successful")
        
        # Initialize tables
        init_db()
        logger.info("Database tables initialized")
        
        # Test Redis connection
        try:
            redis_client.ping()
            logger.info("Redis connection successful")
        except Exception as e:
            logger.warning(f"Redis connection failed: {e}. Rate limiting and caching will be disabled.")
        
    except Exception as e:
        logger.error(f"Startup error: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down AI Document Q&A API")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI-Powered Document & Multimedia Q&A API",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request ID middleware
from backend.core.middleware import RequestIDMiddleware
app.add_middleware(RequestIDMiddleware)

# Exception handlers
from backend.core.exception_handlers import (
    http_exception_handler,
    validation_exception_handler,
    generic_exception_handler
)
from fastapi.exceptions import RequestValidationError

app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    try:
        # Check database
        with engine.connect() as conn:
            db_status = "connected"
        
        # Check Redis
        try:
            redis_client.ping()
            redis_status = "connected"
        except Exception:
            redis_status = "disconnected"
        
        return {
            "status": "healthy",
            "database": db_status,
            "redis": redis_status,
            "version": settings.APP_VERSION
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }


# Include routers
from backend.core.health import router as health_router
from backend.core.metrics import router as metrics_router
from backend.modules.auth import auth_router
from backend.modules.document import document_router
from backend.modules.media import media_router
from backend.modules.chatbot import chatbot_router
from backend.modules.summarization import summarization_router
from backend.modules.playback import playback_router
from backend.modules.vector_search import vector_search_router

app.include_router(health_router, tags=["health"])
app.include_router(metrics_router, tags=["metrics"])
app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(document_router, prefix="/documents", tags=["documents"])
app.include_router(media_router, prefix="/media", tags=["media"])
app.include_router(chatbot_router, prefix="/chats", tags=["chats"])
app.include_router(summarization_router, prefix="/summaries", tags=["summaries"])
app.include_router(playback_router, prefix="/playback", tags=["playback"])
app.include_router(vector_search_router, prefix="/vector-search", tags=["vector-search"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
