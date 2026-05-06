import redis
from typing import Optional
from config.settings import settings

redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)


async def get_redis():
    """Dependency to get Redis client."""
    return redis_client


class CacheService:
    """Service for caching operations."""
    
    def __init__(self, redis_client):
        self.redis = redis_client
    
    async def get(self, key: str) -> Optional[str]:
        """Get value from cache."""
        return self.redis.get(key)
    
    async def set(self, key: str, value: str, expire: int = 3600) -> bool:
        """Set value in cache with expiration."""
        return self.redis.setex(key, expire, value)
    
    async def delete(self, key: str) -> bool:
        """Delete value from cache."""
        return self.redis.delete(key) > 0
    
    async def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        return self.redis.exists(key) > 0


class RateLimiter:
    """Service for rate limiting using Redis."""
    
    def __init__(self, redis_client):
        self.redis = redis_client
    
    async def is_allowed(self, identifier: str, limit: int, period: int) -> bool:
        """
        Check if request is allowed based on rate limit.
        
        Args:
            identifier: Unique identifier (e.g., user_id)
            limit: Maximum requests allowed
            period: Time period in seconds
        
        Returns:
            True if allowed, False otherwise
        """
        key = f"rate_limit:{identifier}"
        current = self.redis.incr(key)
        
        if current == 1:
            self.redis.expire(key, period)
        
        return current <= limit
    
    async def get_remaining(self, identifier: str, limit: int) -> int:
        """Get remaining requests for rate limit."""
        key = f"rate_limit:{identifier}"
        current = int(self.redis.get(key) or 0)
        return max(0, limit - current)
