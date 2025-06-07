"""
Enhanced Purview CLI Backend API v2.0
Main FastAPI application with comprehensive data governance capabilities.
"""
import asyncio
import logging
import time
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

# Import API routers
from app.api.v1 import entities, scanning, lineage, analytics, governance, auth, system, upload

# Import core components
from app.core.config import settings
from app.core.logging import setup_logging
from app.core.websocket import WebSocketManager

# Import services
from app.services.health_check import HealthCheckService

# Import middleware
from app.middleware.errors import (
    PurviewAPIException,
    purview_exception_handler,
    http_exception_handler,
    validation_exception_handler,
    general_exception_handler
)
from app.middleware.rate_limit import RateLimitMiddleware

# Import database
from app.database.connection import create_tables

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

# Initialize WebSocket manager
websocket_manager = WebSocketManager()

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan context manager"""
    # Startup
    logger.info("Starting Enhanced Purview CLI API Server v2.0")
    
    try:
        # Initialize database
        logger.info("Creating database tables...")
        create_tables()
        
        # Initialize services
        logger.info("Initializing services...")
        health_service = HealthCheckService()
        await health_service.initialize()
        
        # Start background tasks
        logger.info("Starting background tasks...")
        asyncio.create_task(websocket_manager.cleanup_connections())
        
        logger.info("API startup completed successfully")
        yield
        
    except Exception as e:
        logger.error(f"Startup failed: {str(e)}")
        raise
    
    finally:
        # Shutdown
        logger.info("Shutting down Enhanced Purview CLI API Server")
        await websocket_manager.disconnect_all()

# Create FastAPI app
app = FastAPI(
    title="Enhanced Purview CLI API",
    description="Comprehensive Azure Purview data governance and management API",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(RateLimitMiddleware)

# Add error handlers
app.add_exception_handler(PurviewAPIException, purview_exception_handler)
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

# Include routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["authentication"])
app.include_router(entities.router, prefix="/api/v1/entities", tags=["entities"])
app.include_router(scanning.router, prefix="/api/v1/scanning", tags=["scanning"])
app.include_router(lineage.router, prefix="/api/v1/lineage", tags=["lineage"])
app.include_router(analytics.router, prefix="/api/v1/analytics", tags=["analytics"])
app.include_router(governance.router, prefix="/api/v1/governance", tags=["governance"])
app.include_router(upload.router, prefix="/api/v1/upload", tags=["file-upload"])
app.include_router(system.router, prefix="/api/v1/system", tags=["system"])

# WebSocket endpoint
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time communication"""
    await websocket_manager.connect(websocket)

# Health check endpoints
@app.get("/health", tags=["health"])
async def health_check():
    """Basic health check endpoint"""
    return {"status": "healthy", "version": "2.0.0"}

@app.get("/health/detailed", tags=["health"])
async def detailed_health_check():
    """Detailed health check with service status"""
    health_service = HealthCheckService()
    return await health_service.get_detailed_status()

# Root endpoint
@app.get("/", tags=["root"])
async def root():
    """Root endpoint with API information"""
    return {
        "name": "Enhanced Purview CLI API",
        "version": "2.0.0",
        "description": "REST API for Enhanced Purview CLI Web UI",
        "docs_url": "/docs",
        "status": "running"
    }

# Middleware for request logging
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log requests and measure response time"""
    start_time = time.time()
    
    # Process request
    response = await call_next(request)
    
    # Calculate duration
    duration = time.time() - start_time
    
    # Log request
    logger.info(
        f"HTTP {request.method} {request.url.path} - "
        f"Status: {response.status_code} - "
        f"Duration: {duration:.3f}s"
    )
    
    return response

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        access_log=False,  # We handle logging ourselves
    )
