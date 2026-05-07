from fastapi import Request, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from typing import Union
from backend.core.logger import logger


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """
    Handle HTTP exceptions with standardized JSON response.

    Args:
        request: FastAPI request object
        exc: HTTPException instance

    Returns:
        JSONResponse with standardized error format
    """
    request_id = getattr(request.state, "request_id", "unknown")

    logger.warning(
        f"HTTP exception | status: {exc.status_code} | detail: {exc.detail} | request_id: {request_id}"
    )

    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail, "detail": exc.detail, "request_id": request_id},
    )


async def validation_exception_handler(
    request: Request, exc: Union[RequestValidationError, ValidationError]
) -> JSONResponse:
    """
    Handle request validation errors with standardized JSON response.

    Args:
        request: FastAPI request object
        exc: Validation error instance

    Returns:
        JSONResponse with standardized error format
    """
    request_id = getattr(request.state, "request_id", "unknown")

    logger.warning(
        f"Validation error | errors: {exc.errors()} | request_id: {request_id}"
    )

    return JSONResponse(
        status_code=422,
        content={
            "error": "Validation error",
            "detail": exc.errors(),
            "request_id": request_id,
        },
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Handle generic exceptions with standardized JSON response.

    Args:
        request: FastAPI request object
        exc: Generic exception instance

    Returns:
        JSONResponse with standardized error format
    """
    request_id = getattr(request.state, "request_id", "unknown")

    logger.error(
        f"Unhandled exception | type: {type(exc).__name__} | message: {str(exc)} | request_id: {request_id}"
    )

    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": "An unexpected error occurred",
            "request_id": request_id,
        },
    )
