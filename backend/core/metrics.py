from fastapi import APIRouter
import time
from config.settings import settings

router = APIRouter()

# Track application start time
_start_time = time.time()


@router.get("/metrics")
async def get_metrics():
    """
    Metrics endpoint for monitoring and observability.
    
    Returns basic service metrics including uptime, service name, version, and status.
    This endpoint is lightweight and suitable for monitoring systems like Prometheus.
    
    Returns:
        dict: Service metrics
    """
    uptime_seconds = time.time() - _start_time
    
    return {
        "service_name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "healthy",
        "uptime_seconds": round(uptime_seconds, 2)
    }
