from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
import uuid
from backend.core.logger import logger


class RequestIDMiddleware(BaseHTTPMiddleware):
    """
    Middleware to generate and attach a unique request ID to each request.

    This middleware:
    - Generates a UUID for each incoming request
    - Attaches it to request.state.request_id
    - Includes it in response headers as X-Request-ID
    - Enables request tracing across logs
    """

    async def dispatch(self, request: Request, call_next):
        # Generate unique request ID
        request_id = str(uuid.uuid4())

        # Attach to request state for use in handlers
        request.state.request_id = request_id

        # Log incoming request with request ID
        logger.info(
            f"Request started | method: {request.method} | path: {request.url.path} | request_id: {request_id}"
        )

        # Process request
        response = await call_next(request)

        # Add request ID to response headers
        response.headers["X-Request-ID"] = request_id

        # Log request completion
        logger.info(
            f"Request completed | status: {response.status_code} | request_id: {request_id}"
        )

        return response
