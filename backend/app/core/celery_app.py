"""
Celery configuration and task definitions for background processing.
Handles file processing, data operations, and long-running tasks.
"""
import os
from celery import Celery
from celery.signals import task_prerun, task_postrun, task_failure
from kombu import Queue
import structlog

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

# Create Celery app
celery_app = Celery(
    "purview_tasks",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=[
        "app.tasks.file_processing",
        "app.tasks.data_operations", 
        "app.tasks.maintenance"
    ]
)

# Configure Celery
celery_app.conf.update(
    # Task routing
    task_routes={
        "app.tasks.file_processing.*": {"queue": "file_processing"},
        "app.tasks.data_operations.*": {"queue": "data_operations"},
        "app.tasks.maintenance.*": {"queue": "maintenance"},
    },
    
    # Queue configuration
    task_queues=(
        Queue("file_processing", routing_key="file_processing"),
        Queue("data_operations", routing_key="data_operations"),
        Queue("maintenance", routing_key="maintenance"),
        Queue("default", routing_key="default"),
    ),
    
    # Task settings
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    
    # Result backend settings
    result_expires=3600,  # 1 hour
    result_persistent=True,
    
    # Worker settings
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    worker_max_tasks_per_child=1000,
    
    # Retry settings
    task_annotations={
        "*": {
            "rate_limit": "100/m",
            "time_limit": 300,  # 5 minutes
            "soft_time_limit": 240,  # 4 minutes
        },
        "app.tasks.file_processing.process_large_file": {
            "time_limit": 1800,  # 30 minutes
            "soft_time_limit": 1500,  # 25 minutes
        },
    },
    
    # Monitoring
    worker_send_task_events=True,
    task_send_sent_event=True,
    
    # Beat schedule for periodic tasks
    beat_schedule={
        "cleanup-expired-files": {
            "task": "app.tasks.maintenance.cleanup_expired_files",
            "schedule": 3600.0,  # Every hour
        },
        "update-analytics": {
            "task": "app.tasks.data_operations.update_analytics_cache",
            "schedule": 900.0,  # Every 15 minutes
        },
        "health-check": {
            "task": "app.tasks.maintenance.health_check",
            "schedule": 300.0,  # Every 5 minutes
        },
    },
)

# Task event handlers
@task_prerun.connect
def task_prerun_handler(sender=None, task_id=None, task=None, args=None, kwargs=None, **kwds):
    """Handle task prerun events."""
    logger.info("Task starting", task_id=task_id, task_name=task.name)

@task_postrun.connect
def task_postrun_handler(sender=None, task_id=None, task=None, args=None, kwargs=None, retval=None, state=None, **kwds):
    """Handle task postrun events."""
    logger.info("Task completed", task_id=task_id, task_name=task.name, state=state)

@task_failure.connect
def task_failure_handler(sender=None, task_id=None, exception=None, traceback=None, einfo=None, **kwds):
    """Handle task failure events."""
    logger.error("Task failed", task_id=task_id, error=str(exception), traceback=traceback)

# Utility functions
def get_celery_app():
    """Get the Celery app instance."""
    return celery_app

def is_worker_available():
    """Check if Celery workers are available."""
    try:
        inspect = celery_app.control.inspect()
        stats = inspect.stats()
        return stats is not None and len(stats) > 0
    except Exception:
        return False

def get_worker_status():
    """Get worker status information."""
    try:
        inspect = celery_app.control.inspect()
        return {
            "active": inspect.active(),
            "scheduled": inspect.scheduled(),
            "stats": inspect.stats(),
            "registered": inspect.registered(),
        }
    except Exception as e:
        logger.error("Failed to get worker status", error=str(e))
        return None

def get_queue_length(queue_name: str = "default"):
    """Get the length of a specific queue."""
    try:
        inspect = celery_app.control.inspect()
        stats = inspect.stats()
        if stats:
            for worker, worker_stats in stats.items():
                if queue_name in worker_stats.get("pool", {}).get("queues", {}):
                    return worker_stats["pool"]["queues"][queue_name]
        return 0
    except Exception:
        return 0

# Task decorators
def retry_on_failure(max_retries=3, countdown=60):
    """Decorator to retry tasks on failure."""
    def decorator(func):
        func.retry_kwargs = {"max_retries": max_retries, "countdown": countdown}
        return func
    return decorator

def monitor_task_progress(func):
    """Decorator to monitor task progress."""
    def wrapper(self, *args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        except Exception as exc:
            logger.error("Task failed with exception", task_id=self.request.id, error=str(exc))
            raise
    return wrapper

# Custom task base class
class BaseTask(celery_app.Task):
    """Base task class with common functionality."""
    
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """Handle task failure."""
        logger.error(
            "Task failed",
            task_id=task_id,
            task_name=self.name,
            error=str(exc),
            args=args,
            kwargs=kwargs
        )
    
    def on_retry(self, exc, task_id, args, kwargs, einfo):
        """Handle task retry."""
        logger.warning(
            "Task retrying",
            task_id=task_id,
            task_name=self.name,
            error=str(exc),
            retry_count=self.request.retries
        )
    
    def on_success(self, retval, task_id, args, kwargs):
        """Handle task success."""
        logger.info(
            "Task succeeded",
            task_id=task_id,
            task_name=self.name
        )

# Set the base task class
celery_app.Task = BaseTask
