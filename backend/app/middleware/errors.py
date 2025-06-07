"""
Error handling middleware and exception handlers.
"""
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import logging
from typing import Any, Dict
import traceback

logger = logging.getLogger(__name__)

class PurviewAPIException(Exception):
    """Custom exception for Purview API errors."""
    
    def __init__(
        self,
        message: str,
        status_code: int = 500,
        error_code: str = "INTERNAL_ERROR",
        details: Dict[str, Any] = None
    ):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)

async def purview_exception_handler(request: Request, exc: PurviewAPIException):
    """
    Handle custom PurviewAPIException.
    
    Args:
        request: FastAPI request object
        exc: PurviewAPIException instance
    
    Returns:
        JSONResponse with error details
    """
    logger.error(f"PurviewAPIException: {exc.message} - {exc.details}")
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.error_code,
                "message": exc.message,
                "details": exc.details,
                "path": request.url.path,
                "method": request.method
            }
        }
    )

async def http_exception_handler(request: Request, exc: HTTPException):
    """
    Handle standard HTTP exceptions.
    
    Args:
        request: FastAPI request object
        exc: HTTPException instance
    
    Returns:
        JSONResponse with error details
    """
    logger.warning(f"HTTPException: {exc.status_code} - {exc.detail}")
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": f"HTTP_{exc.status_code}",
                "message": exc.detail,
                "path": request.url.path,
                "method": request.method
            }
        }
    )

async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Handle request validation errors.
    
    Args:
        request: FastAPI request object
        exc: RequestValidationError instance
    
    Returns:
        JSONResponse with validation error details
    """
    logger.warning(f"Validation error: {exc.errors()}")
    
    return JSONResponse(
        status_code=422,
        content={
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Request validation failed",
                "details": exc.errors(),
                "path": request.url.path,
                "method": request.method
            }
        }
    )

async def general_exception_handler(request: Request, exc: Exception):
    """
    Handle unexpected exceptions.
    
    Args:
        request: FastAPI request object
        exc: Exception instance
    
    Returns:
        JSONResponse with generic error message
    """
    logger.error(f"Unexpected error: {str(exc)}")
    logger.error(f"Traceback: {traceback.format_exc()}")
    
    # Don't expose internal error details in production
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred",
                "path": request.url.path,
                "method": request.method
            }
        }
    )

# Common error responses for reuse
def not_found_error(resource: str, identifier: str = None):
    """Create a not found error."""
    message = f"{resource} not found"
    if identifier:
        message += f": {identifier}"
    
    raise PurviewAPIException(
        message=message,
        status_code=404,
        error_code="RESOURCE_NOT_FOUND",
        details={"resource": resource, "identifier": identifier}
    )

def unauthorized_error(message: str = "Authentication required"):
    """Create an unauthorized error."""
    raise PurviewAPIException(
        message=message,
        status_code=401,
        error_code="UNAUTHORIZED",
        details={"authentication_required": True}
    )

def forbidden_error(message: str = "Insufficient permissions"):
    """Create a forbidden error."""
    raise PurviewAPIException(
        message=message,
        status_code=403,
        error_code="FORBIDDEN",
        details={"permission_required": True}
    )

def validation_error(message: str, field: str = None):
    """Create a validation error."""
    details = {"validation_failed": True}
    if field:
        details["field"] = field
    
    raise PurviewAPIException(
        message=message,
        status_code=400,
        error_code="VALIDATION_ERROR",
        details=details
    )

def conflict_error(message: str, resource: str = None):
    """Create a conflict error."""
    details = {"conflict": True}
    if resource:
        details["resource"] = resource
    
    raise PurviewAPIException(
        message=message,
        status_code=409,
        error_code="CONFLICT",
        details=details
    )

def rate_limit_error(message: str = "Rate limit exceeded"):
    """Create a rate limit error."""
    raise PurviewAPIException(
        message=message,
        status_code=429,
        error_code="RATE_LIMIT_EXCEEDED",
        details={"retry_after": 60}
    )

def service_unavailable_error(message: str = "Service temporarily unavailable"):
    """Create a service unavailable error."""
    raise PurviewAPIException(
        message=message,
        status_code=503,
        error_code="SERVICE_UNAVAILABLE",
        details={"temporary": True}
    )
