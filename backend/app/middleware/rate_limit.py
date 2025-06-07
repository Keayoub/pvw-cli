"""
Rate limiting middleware for API endpoints.
"""
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
import time
import logging
from typing import Dict, List
import asyncio

logger = logging.getLogger(__name__)

class RateLimiter:
    """Simple in-memory rate limiter."""
    
    def __init__(self):
        self.requests: Dict[str, List[float]] = {}
        self.lock = asyncio.Lock()
    
    async def is_allowed(
        self,
        key: str,
        max_requests: int = 100,
        window_seconds: int = 60
    ) -> bool:
        """
        Check if request is allowed based on rate limit.
        
        Args:
            key: Unique identifier for rate limiting (e.g., IP address)
            max_requests: Maximum requests allowed in time window
            window_seconds: Time window in seconds
        
        Returns:
            True if request is allowed, False otherwise
        """
        async with self.lock:
            current_time = time.time()
            window_start = current_time - window_seconds
            
            # Clean up old requests
            if key in self.requests:
                self.requests[key] = [
                    req_time for req_time in self.requests[key]
                    if req_time > window_start
                ]
            else:
                self.requests[key] = []
            
            # Check if limit exceeded
            if len(self.requests[key]) >= max_requests:
                return False
            
            # Add current request
            self.requests[key].append(current_time)
            return True
    
    async def get_remaining(
        self,
        key: str,
        max_requests: int = 100,
        window_seconds: int = 60
    ) -> int:
        """
        Get remaining requests for the current window.
        
        Args:
            key: Unique identifier for rate limiting
            max_requests: Maximum requests allowed in time window
            window_seconds: Time window in seconds
        
        Returns:
            Number of remaining requests
        """
        async with self.lock:
            current_time = time.time()
            window_start = current_time - window_seconds
            
            if key not in self.requests:
                return max_requests
            
            # Count recent requests
            recent_requests = [
                req_time for req_time in self.requests[key]
                if req_time > window_start
            ]
            
            return max(0, max_requests - len(recent_requests))

# Global rate limiter instance
rate_limiter = RateLimiter()

class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware."""
    
    def __init__(
        self,
        app,
        calls: int = 100,
        period: int = 60,
        exclude_paths: List[str] = None
    ):
        super().__init__(app)
        self.calls = calls
        self.period = period
        self.exclude_paths = exclude_paths or ["/health", "/docs", "/openapi.json"]
    
    async def dispatch(self, request: Request, call_next):
        """
        Process request with rate limiting.
        
        Args:
            request: Incoming request
            call_next: Next middleware in chain
        
        Returns:
            Response or HTTP 429 if rate limited
        """
        # Skip rate limiting for excluded paths
        if request.url.path in self.exclude_paths:
            return await call_next(request)
        
        # Get client identifier (IP address)
        client_host = request.client.host if request.client else "unknown"
        
        # Check if request is allowed
        is_allowed = await rate_limiter.is_allowed(
            key=client_host,
            max_requests=self.calls,
            window_seconds=self.period
        )
        
        if not is_allowed:
            logger.warning(f"Rate limit exceeded for {client_host}")
            return Response(
                content='{"error": {"code": "RATE_LIMIT_EXCEEDED", "message": "Too many requests"}}',
                status_code=429,
                headers={
                    "Content-Type": "application/json",
                    "Retry-After": str(self.period)
                }
            )
        
        # Add rate limit headers
        remaining = await rate_limiter.get_remaining(
            key=client_host,
            max_requests=self.calls,
            window_seconds=self.period
        )
        
        response = await call_next(request)
        
        # Add rate limit headers to response
        response.headers["X-RateLimit-Limit"] = str(self.calls)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(int(time.time() + self.period))
        
        return response

# Decorator for route-specific rate limiting
def rate_limit(calls: int = 10, period: int = 60):
    """
    Decorator for route-specific rate limiting.
    
    Args:
        calls: Maximum number of calls allowed
        period: Time period in seconds
    
    Returns:
        Decorator function
    """
    def decorator(func):
        async def wrapper(request: Request, *args, **kwargs):
            client_host = request.client.host if request.client else "unknown"
            
            is_allowed = await rate_limiter.is_allowed(
                key=f"{client_host}:{func.__name__}",
                max_requests=calls,
                window_seconds=period
            )
            
            if not is_allowed:
                raise HTTPException(
                    status_code=429,
                    detail="Rate limit exceeded for this endpoint",
                    headers={"Retry-After": str(period)}
                )
            
            return await func(request, *args, **kwargs)
        
        return wrapper
    return decorator
