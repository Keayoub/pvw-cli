"""
Celery Task Monitoring and Health Check System for Purview CLI
Provides comprehensive monitoring, health checks, and alerting for Celery tasks.
"""
import asyncio
import json
import time
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
import logging
from pathlib import Path
import sys

# Add backend to path
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))

from app.core.celery_app import celery_app
from app.core.config import settings
from app.database.connection import get_db_session
from app.database.models import ProcessingJob
from app.services.cache_service import CacheService
from sqlalchemy import select, func, and_
import structlog

logger = structlog.get_logger(__name__)

@dataclass
class TaskMetrics:
    """Task execution metrics."""
    task_name: str
    total_executed: int = 0
    successful: int = 0
    failed: int = 0
    retried: int = 0
    avg_execution_time: float = 0.0
    min_execution_time: float = 0.0
    max_execution_time: float = 0.0
    last_execution: Optional[datetime] = None
    failure_rate: float = 0.0

@dataclass
class WorkerMetrics:
    """Worker performance metrics."""
    worker_name: str
    is_active: bool = False
    tasks_processed: int = 0
    current_load: int = 0
    memory_usage: float = 0.0
    cpu_usage: float = 0.0
    last_heartbeat: Optional[datetime] = None
    queues: List[str] = None

@dataclass
class QueueMetrics:
    """Queue performance metrics."""
    queue_name: str
    pending_tasks: int = 0
    processing_tasks: int = 0
    completed_tasks: int = 0
    failed_tasks: int = 0
    avg_wait_time: float = 0.0
    throughput: float = 0.0  # tasks per minute

@dataclass
class SystemHealth:
    """Overall system health status."""
    status: str  # healthy, degraded, critical
    total_workers: int = 0
    active_workers: int = 0
    total_tasks: int = 0
    failed_tasks: int = 0
    queue_backlog: int = 0
    avg_response_time: float = 0.0
    uptime: timedelta = None
    last_check: datetime = None

class CeleryMonitor:
    """Comprehensive Celery monitoring system."""
    
    def __init__(self):
        self.cache_service = CacheService()
        self.start_time = datetime.utcnow()
        self.metrics_history: List[Dict[str, Any]] = []
        self.alert_thresholds = {
            'max_queue_size': 1000,
            'max_failure_rate': 0.10,  # 10%
            'max_response_time': 300.0,  # 5 minutes
            'min_active_workers': 1
        }
    
    async def get_task_metrics(self, time_range: timedelta = None) -> Dict[str, TaskMetrics]:
        """Get comprehensive task metrics."""
        if time_range is None:
            time_range = timedelta(hours=24)
        
        since_time = datetime.utcnow() - time_range
        
        try:
            # Get task statistics from Celery
            inspect = celery_app.control.inspect()
            stats = inspect.stats()
            
            task_metrics = {}
            
            if stats:
                for worker_name, worker_stats in stats.items():
                    total_tasks = worker_stats.get('total', {})
                    
                    for task_name, task_stats in total_tasks.items():
                        if task_name not in task_metrics:
                            task_metrics[task_name] = TaskMetrics(task_name=task_name)
                        
                        metrics = task_metrics[task_name]
                        if isinstance(task_stats, dict):
                            metrics.total_executed += task_stats.get('total', 0)
                            metrics.successful += task_stats.get('success', 0)
                            metrics.failed += task_stats.get('failure', 0)
                        else:
                            metrics.total_executed += task_stats
            
            # Get additional metrics from database
            async with get_db_session() as session:
                # Get processing job statistics
                result = await session.execute(
                    select(
                        ProcessingJob.operation_type,
                        func.count().label('total'),
                        func.sum(func.case([(ProcessingJob.status == 'completed', 1)], else_=0)).label('completed'),
                        func.sum(func.case([(ProcessingJob.status == 'failed', 1)], else_=0)).label('failed'),
                        func.avg(
                            func.extract('epoch', ProcessingJob.completed_at - ProcessingJob.created_at)
                        ).label('avg_duration')
                    )
                    .where(ProcessingJob.created_at >= since_time)
                    .group_by(ProcessingJob.operation_type)
                )
                
                for row in result:
                    operation_type = row.operation_type
                    if operation_type not in task_metrics:
                        task_metrics[operation_type] = TaskMetrics(task_name=operation_type)
                    
                    metrics = task_metrics[operation_type]
                    metrics.total_executed += row.total or 0
                    metrics.successful += row.completed or 0
                    metrics.failed += row.failed or 0
                    metrics.avg_execution_time = row.avg_duration or 0.0
                    
                    if metrics.total_executed > 0:
                        metrics.failure_rate = metrics.failed / metrics.total_executed
            
            return task_metrics
            
        except Exception as e:
            logger.error("Failed to get task metrics", error=str(e))
            return {}
    
    async def get_worker_metrics(self) -> Dict[str, WorkerMetrics]:
        """Get worker performance metrics."""
        try:
            inspect = celery_app.control.inspect()
            
            # Get active workers
            active_workers = inspect.active()
            stats = inspect.stats()
            registered_tasks = inspect.registered()
            
            worker_metrics = {}
            
            if stats:
                for worker_name, worker_stats in stats.items():
                    metrics = WorkerMetrics(worker_name=worker_name)
                    
                    # Basic stats
                    metrics.is_active = worker_name in (active_workers or {})
                    metrics.tasks_processed = sum(
                        task_count if isinstance(task_count, int) else task_count.get('total', 0)
                        for task_count in worker_stats.get('total', {}).values()
                    )
                    
                    # Current load
                    if active_workers and worker_name in active_workers:
                        metrics.current_load = len(active_workers[worker_name])
                    
                    # Queue information
                    if registered_tasks and worker_name in registered_tasks:
                        # Extract queue names from registered tasks (simplified)
                        metrics.queues = list(set(
                            task.split('.')[-1] for task in registered_tasks[worker_name]
                            if '.' in task
                        ))
                    
                    metrics.last_heartbeat = datetime.utcnow()
                    worker_metrics[worker_name] = metrics
            
            return worker_metrics
            
        except Exception as e:
            logger.error("Failed to get worker metrics", error=str(e))
            return {}
    
    async def get_queue_metrics(self) -> Dict[str, QueueMetrics]:
        """Get queue performance metrics."""
        try:
            inspect = celery_app.control.inspect()
            
            # Get active queues
            active_queues = inspect.active_queues()
            active_tasks = inspect.active()
            
            queue_metrics = {}
            
            if active_queues:
                for worker_name, queues in active_queues.items():
                    for queue_info in queues:
                        queue_name = queue_info['name']
                        
                        if queue_name not in queue_metrics:
                            queue_metrics[queue_name] = QueueMetrics(queue_name=queue_name)
                        
                        metrics = queue_metrics[queue_name]
                        
                        # Current processing tasks
                        if active_tasks and worker_name in active_tasks:
                            for task in active_tasks[worker_name]:
                                if task.get('queue') == queue_name:
                                    metrics.processing_tasks += 1
            
            # Get additional metrics from database
            async with get_db_session() as session:
                # Get queue statistics from processing jobs
                result = await session.execute(
                    select(
                        ProcessingJob.status,
                        func.count().label('count')
                    )
                    .where(ProcessingJob.created_at >= datetime.utcnow() - timedelta(hours=24))
                    .group_by(ProcessingJob.status)
                )
                
                status_counts = {row.status: row.count for row in result}
                
                # Update queue metrics with database info
                for queue_name, metrics in queue_metrics.items():
                    metrics.pending_tasks = status_counts.get('queued', 0)
                    metrics.completed_tasks = status_counts.get('completed', 0)
                    metrics.failed_tasks = status_counts.get('failed', 0)
            
            return queue_metrics
            
        except Exception as e:
            logger.error("Failed to get queue metrics", error=str(e))
            return {}
    
    async def get_system_health(self) -> SystemHealth:
        """Get overall system health status."""
        try:
            worker_metrics = await self.get_worker_metrics()
            queue_metrics = await self.get_queue_metrics()
            task_metrics = await self.get_task_metrics()
            
            # Calculate health metrics
            total_workers = len(worker_metrics)
            active_workers = sum(1 for w in worker_metrics.values() if w.is_active)
            
            total_tasks = sum(m.total_executed for m in task_metrics.values())
            failed_tasks = sum(m.failed for m in task_metrics.values())
            
            queue_backlog = sum(q.pending_tasks for q in queue_metrics.values())
            
            avg_response_time = sum(m.avg_execution_time for m in task_metrics.values()) / len(task_metrics) if task_metrics else 0.0
            
            uptime = datetime.utcnow() - self.start_time
            
            # Determine health status
            status = "healthy"
            
            if (queue_backlog > self.alert_thresholds['max_queue_size'] or
                active_workers < self.alert_thresholds['min_active_workers'] or
                avg_response_time > self.alert_thresholds['max_response_time']):
                status = "degraded"
            
            if active_workers == 0 or (total_tasks > 0 and failed_tasks / total_tasks > self.alert_thresholds['max_failure_rate']):
                status = "critical"
            
            return SystemHealth(
                status=status,
                total_workers=total_workers,
                active_workers=active_workers,
                total_tasks=total_tasks,
                failed_tasks=failed_tasks,
                queue_backlog=queue_backlog,
                avg_response_time=avg_response_time,
                uptime=uptime,
                last_check=datetime.utcnow()
            )
            
        except Exception as e:
            logger.error("Failed to get system health", error=str(e))
            return SystemHealth(
                status="critical",
                last_check=datetime.utcnow()
            )
    
    async def generate_health_report(self) -> Dict[str, Any]:
        """Generate comprehensive health report."""
        try:
            system_health = await self.get_system_health()
            task_metrics = await self.get_task_metrics()
            worker_metrics = await self.get_worker_metrics()
            queue_metrics = await self.get_queue_metrics()
            
            return {
                "timestamp": datetime.utcnow().isoformat(),
                "system_health": asdict(system_health),
                "task_metrics": {name: asdict(metrics) for name, metrics in task_metrics.items()},
                "worker_metrics": {name: asdict(metrics) for name, metrics in worker_metrics.items()},
                "queue_metrics": {name: asdict(metrics) for name, metrics in queue_metrics.items()},
                "alerts": await self.check_alerts(),
                "recommendations": await self.generate_recommendations()
            }
            
        except Exception as e:
            logger.error("Failed to generate health report", error=str(e))
            return {
                "timestamp": datetime.utcnow().isoformat(),
                "error": str(e)
            }
    
    async def check_alerts(self) -> List[Dict[str, Any]]:
        """Check for system alerts."""
        alerts = []
        
        try:
            system_health = await self.get_system_health()
            task_metrics = await self.get_task_metrics()
            queue_metrics = await self.get_queue_metrics()
            
            # Check worker availability
            if system_health.active_workers < self.alert_thresholds['min_active_workers']:
                alerts.append({
                    "type": "critical",
                    "message": f"Low worker count: {system_health.active_workers} active workers",
                    "recommendation": "Start additional workers to handle the load"
                })
            
            # Check queue backlog
            if system_health.queue_backlog > self.alert_thresholds['max_queue_size']:
                alerts.append({
                    "type": "warning",
                    "message": f"High queue backlog: {system_health.queue_backlog} pending tasks",
                    "recommendation": "Scale up workers or investigate slow tasks"
                })
            
            # Check failure rates
            for task_name, metrics in task_metrics.items():
                if metrics.failure_rate > self.alert_thresholds['max_failure_rate']:
                    alerts.append({
                        "type": "warning",
                        "message": f"High failure rate for {task_name}: {metrics.failure_rate:.2%}",
                        "recommendation": "Investigate task failures and fix underlying issues"
                    })
            
            # Check response times
            if system_health.avg_response_time > self.alert_thresholds['max_response_time']:
                alerts.append({
                    "type": "warning",
                    "message": f"High average response time: {system_health.avg_response_time:.2f}s",
                    "recommendation": "Optimize task performance or increase concurrency"
                })
            
            return alerts
            
        except Exception as e:
            logger.error("Failed to check alerts", error=str(e))
            return [{
                "type": "error",
                "message": f"Failed to check alerts: {str(e)}",
                "recommendation": "Check monitoring system configuration"
            }]
    
    async def generate_recommendations(self) -> List[str]:
        """Generate system optimization recommendations."""
        recommendations = []
        
        try:
            system_health = await self.get_system_health()
            task_metrics = await self.get_task_metrics()
            worker_metrics = await self.get_worker_metrics()
            
            # Worker scaling recommendations
            if system_health.queue_backlog > 100:
                recommendations.append(
                    f"Consider scaling up workers. Current backlog: {system_health.queue_backlog} tasks"
                )
            
            # Task optimization recommendations
            slow_tasks = [
                name for name, metrics in task_metrics.items()
                if metrics.avg_execution_time > 60.0
            ]
            
            if slow_tasks:
                recommendations.append(
                    f"Optimize slow tasks: {', '.join(slow_tasks)}"
                )
            
            # Memory recommendations
            high_memory_workers = [
                name for name, metrics in worker_metrics.items()
                if metrics.memory_usage > 80.0
            ]
            
            if high_memory_workers:
                recommendations.append(
                    f"Monitor memory usage for workers: {', '.join(high_memory_workers)}"
                )
            
            # Queue balancing recommendations
            if len(worker_metrics) > 1:
                loads = [w.current_load for w in worker_metrics.values()]
                if max(loads) - min(loads) > 10:
                    recommendations.append(
                        "Consider rebalancing task distribution across workers"
                    )
            
            return recommendations
            
        except Exception as e:
            logger.error("Failed to generate recommendations", error=str(e))
            return [f"Error generating recommendations: {str(e)}"]
    
    async def save_metrics_snapshot(self):
        """Save current metrics snapshot for historical analysis."""
        try:
            report = await self.generate_health_report()
            
            # Save to cache with timestamp
            cache_key = f"metrics_snapshot:{int(time.time())}"
            await self.cache_service.set(cache_key, report, ttl=86400 * 7)  # Keep for 7 days
            
            # Maintain metrics history
            self.metrics_history.append(report)
            
            # Keep only last 24 hours of snapshots
            cutoff_time = datetime.utcnow() - timedelta(hours=24)
            self.metrics_history = [
                snapshot for snapshot in self.metrics_history
                if datetime.fromisoformat(snapshot['timestamp']) > cutoff_time
            ]
            
            logger.info("Metrics snapshot saved", snapshot_count=len(self.metrics_history))
            
        except Exception as e:
            logger.error("Failed to save metrics snapshot", error=str(e))
    
    async def get_historical_metrics(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Get historical metrics for the specified time range."""
        try:
            # Get snapshots from cache
            snapshots = []
            
            # Get recent snapshots from memory
            cutoff_time = datetime.utcnow() - timedelta(hours=hours)
            for snapshot in self.metrics_history:
                if datetime.fromisoformat(snapshot['timestamp']) > cutoff_time:
                    snapshots.append(snapshot)
            
            # Try to get additional snapshots from cache
            current_time = int(time.time())
            for i in range(0, hours * 60, 15):  # Every 15 minutes
                timestamp = current_time - (i * 60)
                cache_key = f"metrics_snapshot:{timestamp}"
                
                try:
                    cached_snapshot = await self.cache_service.get(cache_key)
                    if cached_snapshot:
                        snapshots.append(cached_snapshot)
                except:
                    continue
            
            # Sort by timestamp
            snapshots.sort(key=lambda x: x['timestamp'])
            
            return snapshots
            
        except Exception as e:
            logger.error("Failed to get historical metrics", error=str(e))
            return []
    
    async def start_monitoring(self, interval: int = 60):
        """Start continuous monitoring."""
        logger.info("Starting Celery monitoring", interval=interval)
        
        while True:
            try:
                # Generate and save metrics snapshot
                await self.save_metrics_snapshot()
                
                # Check for alerts
                alerts = await self.check_alerts()
                
                if alerts:
                    for alert in alerts:
                        if alert['type'] == 'critical':
                            logger.error("Critical alert", **alert)
                        else:
                            logger.warning("System alert", **alert)
                
                # Wait for next interval
                await asyncio.sleep(interval)
                
            except KeyboardInterrupt:
                logger.info("Monitoring stopped by user")
                break
            except Exception as e:
                logger.error("Error in monitoring loop", error=str(e))
                await asyncio.sleep(interval)

async def main():
    """Main monitoring entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Celery Monitoring System")
    parser.add_argument("--interval", type=int, default=60,
                       help="Monitoring interval in seconds")
    parser.add_argument("--report", action="store_true",
                       help="Generate single health report")
    parser.add_argument("--history", type=int, default=24,
                       help="Hours of historical data to show")
    
    args = parser.parse_args()
    
    monitor = CeleryMonitor()
    
    try:
        if args.report:
            # Generate single report
            report = await monitor.generate_health_report()
            print(json.dumps(report, indent=2, default=str))
        else:
            # Start continuous monitoring
            await monitor.start_monitoring(args.interval)
    
    except KeyboardInterrupt:
        logger.info("Monitoring stopped")
    except Exception as e:
        logger.error("Monitoring failed", error=str(e))

if __name__ == "__main__":
    asyncio.run(main())
