from fastapi import Request, HTTPException, status
from backend.core.redis_client import RateLimiter
from backend.core.redis_client import redis_client
from backend.config.settings import settings


async def rate_limit_middleware(request: Request, call_next):
    """
    Rate limiting middleware using Redis.
    """
    if not settings.RATE_LIMIT_ENABLED:
        return await call_next(request)
    
    # Get user ID from header or use IP
    user_id = request.headers.get("X-User-ID")
    if not user_id:
        user_id = request.client.host if request.client else "unknown"
    
    # Check rate limit
    rate_limiter = RateLimiter(redis_client)
    allowed = await rate_limiter.is_allowed(
        user_id,
        settings.RATE_LIMIT_REQUESTS,
        settings.RATE_LIMIT_PERIOD
    )
    
    if not allowed:
        remaining = await rate_limiter.get_remaining(user_id, settings.RATE_LIMIT_REQUESTS)
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Rate limit exceeded. {remaining} requests remaining.",
            headers={
                "X-RateLimit-Limit": str(settings.RATE_LIMIT_REQUESTS),
                "X-RateLimit-Remaining": str(remaining),
                "X-RateLimit-Reset": str(settings.RATE_LIMIT_PERIOD)
            }
        )
    
    response = await call_next(request)
    
    # Add rate limit headers
    remaining = await rate_limiter.get_remaining(user_id, settings.RATE_LIMIT_REQUESTS)
    response.headers["X-RateLimit-Limit"] = str(settings.RATE_LIMIT_REQUESTS)
    response.headers["X-RateLimit-Remaining"] = str(remaining)
    
    return response
