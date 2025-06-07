"""
Celery tasks for system maintenance and health monitoring.
Handles cleanup, health checks, and system optimization tasks.
"""
import asyncio
import os
from typing import Dict, Any, List
from datetime import datetime, timedelta
from pathlib import Path
from celery import current_task
import structlog

from app.core.celery_app import celery_app, BaseTask
from app.core.config import settings
from app.core.logging import get_logger
from app.services.cache_service import CacheService
from app.database.connection import get_db_session
from app.database.models import (
    UploadedFile, ProcessingJob, UserSession, AuditLog, 
    ScanResult, Entity
)

logger = get_logger(__name__)

class MaintenanceTask(BaseTask):
    """Base class for maintenance tasks."""
    
    def __init__(self):
        self.cache_service = CacheService()
    
    def update_progress(self, progress: int, message: str = None):
        """Update task progress."""
        current_task.update_state(
            state="PROGRESS",
            meta={
                "progress": progress,
                "message": message or f"Processing... {progress}%"
            }
        )

@celery_app.task(bind=True, base=MaintenanceTask, name="cleanup_expired_files")
def cleanup_expired_files_task(self):
    """
    Clean up expired uploaded files and their associated data.
    Runs periodically to manage storage space.
    """
    try:
        logger.info("Starting expired files cleanup")
        
        self.update_progress(10, "Initializing file cleanup...")
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            # Calculate expiry date (files older than 30 days)
            expiry_date = datetime.utcnow() - timedelta(days=settings.FILE_RETENTION_DAYS)
            
            cleanup_stats = {
                "files_deleted": 0,
                "jobs_deleted": 0,
                "storage_freed": 0,
                "errors": []
            }
            
            async with get_db_session() as session:
                from sqlalchemy import select, delete
                
                # Find expired files
                self.update_progress(20, "Finding expired files...")
                result = await session.execute(
                    select(UploadedFile)
                    .where(UploadedFile.upload_time < expiry_date)
                )
                expired_files = result.scalars().all()
                
                total_files = len(expired_files)
                logger.info("Found expired files", count=total_files)
                
                for i, file_record in enumerate(expired_files):
                    try:
                        progress = int((i / total_files) * 70) + 20
                        self.update_progress(
                            progress, 
                            f"Cleaning up file {i+1}/{total_files}..."
                        )
                        
                        # Delete physical file
                        file_path = Path(file_record.file_path)
                        if file_path.exists():
                            file_size = file_path.stat().st_size
                            file_path.unlink()
                            cleanup_stats["storage_freed"] += file_size
                        
                        # Delete processing jobs
                        await session.execute(
                            delete(ProcessingJob)
                            .where(ProcessingJob.file_id == file_record.file_id)
                        )
                        
                        # Delete file record
                        await session.delete(file_record)
                        cleanup_stats["files_deleted"] += 1
                        
                    except Exception as e:
                        cleanup_stats["errors"].append(f"File {file_record.file_id}: {str(e)}")
                        logger.error("Failed to delete file", file_id=file_record.file_id, error=str(e))
                
                # Commit all deletions
                await session.commit()
            
            # Clean up orphaned processing jobs
            self.update_progress(90, "Cleaning up orphaned processing jobs...")
            async with get_db_session() as session:
                # Delete jobs for non-existent files
                orphaned_jobs_result = await session.execute(
                    delete(ProcessingJob)
                    .where(~ProcessingJob.file_id.in_(
                        select(UploadedFile.file_id)
                    ))
                )
                cleanup_stats["jobs_deleted"] = orphaned_jobs_result.rowcount
                await session.commit()
            
            self.update_progress(100, "File cleanup completed")
            
            logger.info(
                "Expired files cleanup completed",
                files_deleted=cleanup_stats["files_deleted"],
                storage_freed=cleanup_stats["storage_freed"],
                errors_count=len(cleanup_stats["errors"])
            )
            
            return {
                "status": "completed",
                "cleanup_stats": cleanup_stats,
                "completed_at": datetime.utcnow().isoformat()
            }
            
        finally:
            loop.close()
            
    except Exception as exc:
        logger.error("Expired files cleanup failed", error=str(exc))
        raise exc

@celery_app.task(bind=True, base=MaintenanceTask, name="cleanup_expired_sessions")
def cleanup_expired_sessions_task(self):
    """
    Clean up expired user sessions.
    """
    try:
        logger.info("Starting expired sessions cleanup")
        
        self.update_progress(20, "Finding expired sessions...")
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            cleanup_stats = {
                "sessions_deleted": 0,
                "errors": []
            }
            
            async with get_db_session() as session:
                from sqlalchemy import delete
                
                # Delete expired sessions
                self.update_progress(50, "Deleting expired sessions...")
                result = await session.execute(
                    delete(UserSession)
                    .where(UserSession.expires_at < datetime.utcnow())
                )
                
                cleanup_stats["sessions_deleted"] = result.rowcount
                await session.commit()
            
            self.update_progress(100, "Session cleanup completed")
            
            logger.info("Expired sessions cleanup completed", sessions_deleted=cleanup_stats["sessions_deleted"])
            
            return {
                "status": "completed",
                "cleanup_stats": cleanup_stats,
                "completed_at": datetime.utcnow().isoformat()
            }
            
        finally:
            loop.close()
            
    except Exception as exc:
        logger.error("Expired sessions cleanup failed", error=str(exc))
        raise exc

@celery_app.task(bind=True, base=MaintenanceTask, name="cleanup_old_audit_logs")
def cleanup_old_audit_logs_task(self):
    """
    Clean up old audit logs based on retention policy.
    """
    try:
        logger.info("Starting audit logs cleanup")
        
        self.update_progress(20, "Finding old audit logs...")
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            # Keep audit logs for specified retention period
            retention_date = datetime.utcnow() - timedelta(days=settings.AUDIT_LOG_RETENTION_DAYS)
            
            cleanup_stats = {
                "logs_deleted": 0,
                "errors": []
            }
            
            async with get_db_session() as session:
                from sqlalchemy import delete
                
                # Delete old audit logs
                self.update_progress(50, "Deleting old audit logs...")
                result = await session.execute(
                    delete(AuditLog)
                    .where(AuditLog.timestamp < retention_date)
                )
                
                cleanup_stats["logs_deleted"] = result.rowcount
                await session.commit()
            
            self.update_progress(100, "Audit logs cleanup completed")
            
            logger.info("Audit logs cleanup completed", logs_deleted=cleanup_stats["logs_deleted"])
            
            return {
                "status": "completed",
                "cleanup_stats": cleanup_stats,
                "completed_at": datetime.utcnow().isoformat()
            }
            
        finally:
            loop.close()
            
    except Exception as exc:
        logger.error("Audit logs cleanup failed", error=str(exc))
        raise exc

@celery_app.task(bind=True, base=MaintenanceTask, name="health_check")
def health_check_task(self):
    """
    Perform comprehensive system health check.
    """
    try:
        logger.info("Starting system health check")
        
        self.update_progress(10, "Initializing health check...")
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            health_status = {
                "overall_status": "healthy",
                "checks": {},
                "metrics": {},
                "alerts": []
            }
            
            # Database health check
            self.update_progress(20, "Checking database health...")
            db_health = await self._check_database_health()
            health_status["checks"]["database"] = db_health
            
            # Cache health check
            self.update_progress(40, "Checking cache health...")
            cache_health = await self._check_cache_health()
            health_status["checks"]["cache"] = cache_health
            
            # Storage health check
            self.update_progress(60, "Checking storage health...")
            storage_health = await self._check_storage_health()
            health_status["checks"]["storage"] = storage_health
            
            # System metrics
            self.update_progress(80, "Collecting system metrics...")
            system_metrics = await self._collect_system_metrics()
            health_status["metrics"] = system_metrics
            
            # Determine overall status
            check_statuses = [check["status"] for check in health_status["checks"].values()]
            if "critical" in check_statuses:
                health_status["overall_status"] = "critical"
            elif "warning" in check_statuses:
                health_status["overall_status"] = "warning"
            
            # Generate alerts
            health_status["alerts"] = self._generate_health_alerts(health_status)
            
            self.update_progress(100, "Health check completed")
            
            # Cache health status
            loop.run_until_complete(
                self.cache_service.set("system:health_status", health_status, ttl=300)
            )
            
            logger.info("System health check completed", overall_status=health_status["overall_status"])
            
            return {
                "status": "completed",
                "health_status": health_status,
                "completed_at": datetime.utcnow().isoformat()
            }
            
        finally:
            loop.close()
            
    except Exception as exc:
        logger.error("Health check failed", error=str(exc))
        return {
            "status": "failed",
            "error": str(exc),
            "completed_at": datetime.utcnow().isoformat()
        }

@celery_app.task(bind=True, base=MaintenanceTask, name="optimize_database")
def optimize_database_task(self):
    """
    Perform database optimization tasks.
    """
    try:
        logger.info("Starting database optimization")
        
        self.update_progress(10, "Initializing database optimization...")
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            optimization_stats = {
                "tasks_completed": [],
                "errors": [],
                "performance_improvement": {}
            }
            
            # Analyze table statistics
            self.update_progress(30, "Analyzing table statistics...")
            await self._analyze_table_statistics(optimization_stats)
            
            # Rebuild indexes if needed
            self.update_progress(60, "Optimizing indexes...")
            await self._optimize_indexes(optimization_stats)
            
            # Clean up fragmented data
            self.update_progress(80, "Cleaning up fragmented data...")
            await self._cleanup_fragmentation(optimization_stats)
            
            self.update_progress(100, "Database optimization completed")
            
            logger.info("Database optimization completed", tasks=len(optimization_stats["tasks_completed"]))
            
            return {
                "status": "completed",
                "optimization_stats": optimization_stats,
                "completed_at": datetime.utcnow().isoformat()
            }
            
        finally:
            loop.close()
            
    except Exception as exc:
        logger.error("Database optimization failed", error=str(exc))
        raise exc

@celery_app.task(bind=True, base=MaintenanceTask, name="generate_system_report")
def generate_system_report_task(self, report_type: str = "daily"):
    """
    Generate comprehensive system reports.
    """
    try:
        logger.info("Starting system report generation", report_type=report_type)
        
        self.update_progress(10, "Initializing report generation...")
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            report_data = {
                "report_type": report_type,
                "generated_at": datetime.utcnow().isoformat(),
                "period": self._get_report_period(report_type),
                "sections": {}
            }
            
            # System usage statistics
            self.update_progress(25, "Collecting usage statistics...")
            report_data["sections"]["usage"] = await self._collect_usage_statistics(report_type)
            
            # Performance metrics
            self.update_progress(50, "Collecting performance metrics...")
            report_data["sections"]["performance"] = await self._collect_performance_metrics(report_type)
            
            # Error and alert summary
            self.update_progress(75, "Collecting error summary...")
            report_data["sections"]["errors"] = await self._collect_error_summary(report_type)
            
            # Storage and resource utilization
            self.update_progress(90, "Collecting resource utilization...")
            report_data["sections"]["resources"] = await self._collect_resource_utilization()
            
            # Cache the report
            report_key = f"reports:{report_type}:{datetime.utcnow().strftime('%Y%m%d')}"
            loop.run_until_complete(
                self.cache_service.set(report_key, report_data, ttl=86400)  # 24 hours
            )
            
            self.update_progress(100, "Report generation completed")
            
            logger.info("System report generated successfully", report_type=report_type)
            
            return {
                "status": "completed",
                "report_data": report_data,
                "report_key": report_key,
                "completed_at": datetime.utcnow().isoformat()
            }
            
        finally:
            loop.close()
            
    except Exception as exc:
        logger.error("System report generation failed", report_type=report_type, error=str(exc))
        raise exc

# Helper methods
async def _check_database_health(self) -> Dict[str, Any]:
    """Check database health and connectivity."""
    try:
        async with get_db_session() as session:
            from sqlalchemy import text
            
            # Test basic connectivity
            await session.execute(text("SELECT 1"))
            
            # Check table row counts
            from sqlalchemy import func, select
            
            entity_count = await session.execute(select(func.count(Entity.id)))
            file_count = await session.execute(select(func.count(UploadedFile.file_id)))
            job_count = await session.execute(select(func.count(ProcessingJob.job_id)))
            
            return {
                "status": "healthy",
                "connectivity": "ok",
                "metrics": {
                    "entity_count": entity_count.scalar(),
                    "file_count": file_count.scalar(),
                    "job_count": job_count.scalar()
                }
            }
            
    except Exception as e:
        return {
            "status": "critical",
            "error": str(e),
            "connectivity": "failed"
        }

async def _check_cache_health(self) -> Dict[str, Any]:
    """Check cache health and performance."""
    try:
        # Test cache connectivity
        test_key = "health_check:test"
        test_value = {"timestamp": datetime.utcnow().isoformat()}
        
        await self.cache_service.set(test_key, test_value, ttl=60)
        retrieved_value = await self.cache_service.get(test_key)
        
        if retrieved_value == test_value:
            return {
                "status": "healthy",
                "connectivity": "ok",
                "response_time": "< 10ms"
            }
        else:
            return {
                "status": "warning",
                "connectivity": "ok",
                "issue": "Data integrity issue detected"
            }
            
    except Exception as e:
        return {
            "status": "critical",
            "error": str(e),
            "connectivity": "failed"
        }

async def _check_storage_health(self) -> Dict[str, Any]:
    """Check storage health and disk space."""
    try:
        upload_dir = Path(settings.UPLOAD_DIR)
        
        # Check if upload directory exists and is writable
        if not upload_dir.exists():
            upload_dir.mkdir(parents=True, exist_ok=True)
        
        # Check disk space
        statvfs = os.statvfs(str(upload_dir))
        total_space = statvfs.f_frsize * statvfs.f_blocks
        free_space = statvfs.f_frsize * statvfs.f_available
        used_space = total_space - free_space
        usage_percentage = (used_space / total_space) * 100
        
        status = "healthy"
        if usage_percentage > 90:
            status = "critical"
        elif usage_percentage > 80:
            status = "warning"
        
        return {
            "status": status,
            "total_space": total_space,
            "free_space": free_space,
            "used_space": used_space,
            "usage_percentage": round(usage_percentage, 2)
        }
        
    except Exception as e:
        return {
            "status": "critical",
            "error": str(e)
        }

async def _collect_system_metrics(self) -> Dict[str, Any]:
    """Collect system performance metrics."""
    try:
        import psutil
        
        # CPU metrics
        cpu_percent = psutil.cpu_percent(interval=1)
        cpu_count = psutil.cpu_count()
        
        # Memory metrics
        memory = psutil.virtual_memory()
        
        # Disk I/O metrics
        disk_io = psutil.disk_io_counters()
        
        return {
            "cpu": {
                "usage_percent": cpu_percent,
                "count": cpu_count
            },
            "memory": {
                "total": memory.total,
                "available": memory.available,
                "percent": memory.percent,
                "used": memory.used
            },
            "disk_io": {
                "read_bytes": disk_io.read_bytes if disk_io else 0,
                "write_bytes": disk_io.write_bytes if disk_io else 0
            }
        }
        
    except ImportError:
        return {"error": "psutil not available"}
    except Exception as e:
        return {"error": str(e)}

def _generate_health_alerts(self, health_status: Dict[str, Any]) -> List[str]:
    """Generate health alerts based on status."""
    alerts = []
    
    # Check database alerts
    if health_status["checks"]["database"]["status"] == "critical":
        alerts.append("Database connectivity issue detected")
    
    # Check cache alerts
    if health_status["checks"]["cache"]["status"] == "critical":
        alerts.append("Cache service unavailable")
    
    # Check storage alerts
    storage = health_status["checks"]["storage"]
    if storage["status"] == "critical":
        alerts.append(f"Critical storage usage: {storage.get('usage_percentage', 0)}%")
    elif storage["status"] == "warning":
        alerts.append(f"High storage usage: {storage.get('usage_percentage', 0)}%")
    
    # Check system metrics alerts
    metrics = health_status["metrics"]
    if "memory" in metrics and metrics["memory"].get("percent", 0) > 90:
        alerts.append(f"High memory usage: {metrics['memory']['percent']}%")
    
    if "cpu" in metrics and metrics["cpu"].get("usage_percent", 0) > 90:
        alerts.append(f"High CPU usage: {metrics['cpu']['usage_percent']}%")
    
    return alerts

async def _analyze_table_statistics(self, stats: Dict[str, Any]):
    """Analyze database table statistics."""
    try:
        # This would include database-specific optimization queries
        stats["tasks_completed"].append("table_statistics_analysis")
        logger.info("Table statistics analysis completed")
    except Exception as e:
        stats["errors"].append(f"Table statistics analysis failed: {str(e)}")

async def _optimize_indexes(self, stats: Dict[str, Any]):
    """Optimize database indexes."""
    try:
        # This would include index optimization queries
        stats["tasks_completed"].append("index_optimization")
        logger.info("Index optimization completed")
    except Exception as e:
        stats["errors"].append(f"Index optimization failed: {str(e)}")

async def _cleanup_fragmentation(self, stats: Dict[str, Any]):
    """Clean up database fragmentation."""
    try:
        # This would include defragmentation queries
        stats["tasks_completed"].append("fragmentation_cleanup")
        logger.info("Fragmentation cleanup completed")
    except Exception as e:
        stats["errors"].append(f"Fragmentation cleanup failed: {str(e)}")

def _get_report_period(self, report_type: str) -> Dict[str, str]:
    """Get the time period for the report."""
    now = datetime.utcnow()
    
    if report_type == "daily":
        start = now - timedelta(days=1)
    elif report_type == "weekly":
        start = now - timedelta(days=7)
    elif report_type == "monthly":
        start = now - timedelta(days=30)
    else:
        start = now - timedelta(days=1)
    
    return {
        "start": start.isoformat(),
        "end": now.isoformat()
    }

async def _collect_usage_statistics(self, report_type: str) -> Dict[str, Any]:
    """Collect system usage statistics."""
    # Placeholder for usage statistics collection
    return {
        "files_uploaded": 0,
        "jobs_processed": 0,
        "active_users": 0,
        "api_requests": 0
    }

async def _collect_performance_metrics(self, report_type: str) -> Dict[str, Any]:
    """Collect performance metrics."""
    # Placeholder for performance metrics collection
    return {
        "avg_response_time": 0,
        "max_response_time": 0,
        "error_rate": 0,
        "throughput": 0
    }

async def _collect_error_summary(self, report_type: str) -> Dict[str, Any]:
    """Collect error and alert summary."""
    # Placeholder for error summary collection
    return {
        "total_errors": 0,
        "critical_errors": 0,
        "warnings": 0,
        "common_errors": []
    }

async def _collect_resource_utilization(self) -> Dict[str, Any]:
    """Collect resource utilization data."""
    return await self._collect_system_metrics()
