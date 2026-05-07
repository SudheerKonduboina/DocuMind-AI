from fastapi import HTTPException, status
from typing import Optional


class BaseApplicationException(Exception):
    """Base exception for application-specific errors."""

    def __init__(
        self,
        message: str,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        details: Optional[dict] = None,
    ):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(message)


class NotFoundException(BaseApplicationException):
    """Exception raised when a resource is not found."""

    def __init__(self, resource: str, identifier: Optional[str] = None):
        message = f"{resource} not found"
        if identifier:
            message += f": {identifier}"
        super().__init__(
            message=message,
            status_code=status.HTTP_404_NOT_FOUND,
            details={"resource": resource, "identifier": identifier},
        )


class UnauthorizedException(BaseApplicationException):
    """Exception raised for authentication failures."""

    def __init__(self, message: str = "Unauthorized access"):
        super().__init__(message=message, status_code=status.HTTP_401_UNAUTHORIZED)


class ForbiddenException(BaseApplicationException):
    """Exception raised for authorization failures."""

    def __init__(self, message: str = "Forbidden access"):
        super().__init__(message=message, status_code=status.HTTP_403_FORBIDDEN)


class ValidationException(BaseApplicationException):
    """Exception raised for validation errors."""

    def __init__(self, message: str, field: Optional[str] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            details={"field": field} if field else None,
        )


class ConflictException(BaseApplicationException):
    """Exception raised for conflict errors (e.g., duplicate resources)."""

    def __init__(self, message: str, resource: Optional[str] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_409_CONFLICT,
            details={"resource": resource} if resource else None,
        )


class RateLimitExceededException(BaseApplicationException):
    """Exception raised when rate limit is exceeded."""

    def __init__(self, message: str = "Rate limit exceeded"):
        super().__init__(message=message, status_code=status.HTTP_429_TOO_MANY_REQUESTS)


class ExternalServiceException(BaseApplicationException):
    """Exception raised when external services fail."""

    def __init__(self, service: str, message: str):
        super().__init__(
            message=f"{service} error: {message}",
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            details={"service": service},
        )


class DatabaseException(BaseApplicationException):
    """Exception raised for database-related errors."""

    def __init__(self, message: str = "Database error occurred"):
        super().__init__(
            message=message, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


def handle_application_exception(exc: BaseApplicationException) -> HTTPException:
    """Convert application exception to HTTP exception."""
    return HTTPException(
        status_code=exc.status_code, detail={"message": exc.message, **exc.details}
    )
