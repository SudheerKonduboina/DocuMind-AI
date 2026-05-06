from fastapi import APIRouter
import os
from dotenv import load_dotenv

load_dotenv()

router = APIRouter()


@router.get("/health")
async def health_check():
    """
    Health check endpoint for Kubernetes, Docker, and load balancer probes.
    
    Returns a simple status response indicating the service is operational.
    This endpoint is lightweight and loads instantly, making it suitable for
    health checks in production environments.
    
    Returns:
        dict: Status indicator with LLM provider information
    """
    # Check if xAI API key is configured
    api_key_exists = bool(os.getenv("XAI_API_KEY"))
    
    return {
        "status": "ok",
        "llm": "grok" if api_key_exists else "not_configured"
    }
