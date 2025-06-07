from fastapi import APIRouter, Depends
from typing import Dict, Any
import structlog
import psutil
import asyncio
from datetime import datetime

from app.core.logging import get_logger
from app.core.config import settings
from app.services.health_check import HealthCheckService

logger = get_logger(__name__)
router = APIRouter()

@router.get("/info")
async def get_system_info():
    """Get system information"""
    try:
        # Get system metrics
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        return {
            "name": settings.APP_NAME,
            "version": settings.VERSION,
            "environment": "development" if settings.DEBUG else "production",
            "timestamp": datetime.utcnow().isoformat(),
            "system": {
                "cpu_percent": cpu_percent,
                "memory": {
                    "total": memory.total,
                    "available": memory.available,
                    "percent": memory.percent
                },
                "disk": {
                    "total": disk.total,
                    "free": disk.free,
                    "percent": (disk.used / disk.total) * 100
                }
            }
        }
        
    except Exception as e:
        logger.error("Failed to get system info", error=str(e))
        return {"error": str(e)}

@router.get("/health/detailed")
async def get_detailed_health(
    health_service: HealthCheckService = Depends()
):
    """Get detailed health check"""
    try:
        return await health_service.get_detailed_status()
        
    except Exception as e:
        logger.error("Failed to get detailed health", error=str(e))
        return {"status": "unhealthy", "error": str(e)}

@router.get("/metrics/performance")
async def get_performance_metrics():
    """Get performance metrics"""
    try:
        return {
            "cpu_usage": psutil.cpu_percent(interval=1),
            "memory_usage": psutil.virtual_memory().percent,
            "disk_usage": psutil.disk_usage('/').percent,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error("Failed to get performance metrics", error=str(e))
        return {"error": str(e)}

@router.get("/config")
async def get_configuration():
    """Get non-sensitive configuration"""
    try:
        return {
            "app_name": settings.APP_NAME,
            "version": settings.VERSION,
            "debug": settings.DEBUG,
            "host": settings.HOST,
            "port": settings.PORT,
            "allowed_origins": settings.ALLOWED_ORIGINS,
            "log_level": settings.LOG_LEVEL,
            "max_upload_size": settings.MAX_UPLOAD_SIZE,
            "rate_limit_per_minute": settings.RATE_LIMIT_PER_MINUTE
        }
        
    except Exception as e:
        logger.error("Failed to get configuration", error=str(e))
        return {"error": str(e)}
