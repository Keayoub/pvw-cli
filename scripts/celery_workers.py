#!/usr/bin/env python3
"""
Celery Worker Startup Script for Purview CLI Backend
Provides worker management, monitoring, and configuration capabilities.
"""
import os
import sys
import time
import signal
import subprocess
import argparse
from typing import List, Dict, Any, Optional
from pathlib import Path
import psutil
import logging
from dataclasses import dataclass

# Add backend app to path
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))

from app.core.config import settings
from app.core.celery_app import celery_app

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/purview/celery_workers.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class WorkerConfig:
    """Worker configuration."""
    name: str
    concurrency: int
    queues: List[str]
    loglevel: str = "INFO"
    autoscale: Optional[str] = None
    max_memory_per_child: int = 200000  # KB
    prefetch_multiplier: int = 1

class CeleryWorkerManager:
    """Manages Celery workers for different queues and operations."""
    
    def __init__(self):
        self.workers: Dict[str, subprocess.Popen] = {}
        self.worker_configs = self._get_worker_configurations()
        self.pid_file_dir = Path("/var/run/purview")
        self.log_dir = Path("/var/log/purview")
        
        # Ensure directories exist
        self.pid_file_dir.mkdir(parents=True, exist_ok=True)
        self.log_dir.mkdir(parents=True, exist_ok=True)
    
    def _get_worker_configurations(self) -> List[WorkerConfig]:
        """Get worker configurations for different operations."""
        return [
            WorkerConfig(
                name="file_processing_worker",
                concurrency=4,
                queues=["file_processing", "high_priority"],
                autoscale="8,2",
                max_memory_per_child=500000
            ),
            WorkerConfig(
                name="data_operations_worker", 
                concurrency=2,
                queues=["data_operations", "analytics"],
                autoscale="4,1"
            ),
            WorkerConfig(
                name="maintenance_worker",
                concurrency=1,
                queues=["maintenance", "low_priority"],
                prefetch_multiplier=1
            ),
            WorkerConfig(
                name="bulk_operations_worker",
                concurrency=6,
                queues=["bulk_operations"],
                autoscale="10,2",
                max_memory_per_child=300000
            )
        ]
    
    def start_worker(self, config: WorkerConfig) -> bool:
        """Start a Celery worker with the given configuration."""
        try:
            cmd = [
                "celery",
                "-A", "app.core.celery_app:celery_app",
                "worker",
                "--hostname", f"{config.name}@%h",
                "--concurrency", str(config.concurrency),
                "--queues", ",".join(config.queues),
                "--loglevel", config.loglevel,
                "--prefetch-multiplier", str(config.prefetch_multiplier),
                "--max-memory-per-child", str(config.max_memory_per_child),
                "--logfile", str(self.log_dir / f"{config.name}.log"),
                "--pidfile", str(self.pid_file_dir / f"{config.name}.pid")
            ]
            
            if config.autoscale:
                cmd.extend(["--autoscale", config.autoscale])
            
            # Set environment variables
            env = os.environ.copy()
            env.update({
                "CELERY_WORKER_NAME": config.name,
                "PYTHONPATH": str(backend_path)
            })
            
            # Start the worker process
            process = subprocess.Popen(
                cmd,
                env=env,
                cwd=str(backend_path),
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT
            )
            
            self.workers[config.name] = process
            logger.info(f"Started worker {config.name} with PID {process.pid}")
            
            # Wait a moment to check if worker started successfully
            time.sleep(2)
            if process.poll() is not None:
                logger.error(f"Worker {config.name} failed to start")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to start worker {config.name}: {e}")
            return False
    
    def stop_worker(self, worker_name: str, timeout: int = 30) -> bool:
        """Stop a specific worker."""
        try:
            if worker_name in self.workers:
                process = self.workers[worker_name]
                
                # Send SIGTERM first
                process.terminate()
                
                try:
                    process.wait(timeout=timeout)
                    logger.info(f"Worker {worker_name} stopped gracefully")
                except subprocess.TimeoutExpired:
                    # Force kill if graceful shutdown failed
                    process.kill()
                    process.wait()
                    logger.warning(f"Worker {worker_name} was force killed")
                
                del self.workers[worker_name]
                return True
            
            # Try to stop by PID file
            pid_file = self.pid_file_dir / f"{worker_name}.pid"
            if pid_file.exists():
                try:
                    with open(pid_file) as f:
                        pid = int(f.read().strip())
                    
                    process = psutil.Process(pid)
                    process.terminate()
                    process.wait(timeout=timeout)
                    pid_file.unlink()
                    logger.info(f"Worker {worker_name} stopped via PID file")
                    return True
                    
                except (ProcessLookupError, psutil.NoSuchProcess):
                    pid_file.unlink()  # Clean up stale PID file
                    return True
                except psutil.TimeoutExpired:
                    process.kill()
                    pid_file.unlink()
                    logger.warning(f"Worker {worker_name} was force killed via PID")
                    return True
            
            logger.warning(f"Worker {worker_name} not found")
            return False
            
        except Exception as e:
            logger.error(f"Failed to stop worker {worker_name}: {e}")
            return False
    
    def start_all_workers(self) -> bool:
        """Start all configured workers."""
        success = True
        for config in self.worker_configs:
            if not self.start_worker(config):
                success = False
        return success
    
    def stop_all_workers(self, timeout: int = 30) -> bool:
        """Stop all workers."""
        success = True
        worker_names = list(self.workers.keys())
        
        # Also check for workers running via PID files
        for pid_file in self.pid_file_dir.glob("*.pid"):
            worker_name = pid_file.stem
            if worker_name not in worker_names:
                worker_names.append(worker_name)
        
        for worker_name in worker_names:
            if not self.stop_worker(worker_name, timeout):
                success = False
        
        return success
    
    def restart_worker(self, worker_name: str) -> bool:
        """Restart a specific worker."""
        config = next((c for c in self.worker_configs if c.name == worker_name), None)
        if not config:
            logger.error(f"No configuration found for worker {worker_name}")
            return False
        
        self.stop_worker(worker_name)
        return self.start_worker(config)
    
    def restart_all_workers(self) -> bool:
        """Restart all workers."""
        self.stop_all_workers()
        time.sleep(5)  # Give time for cleanup
        return self.start_all_workers()
    
    def get_worker_status(self) -> Dict[str, Any]:
        """Get status of all workers."""
        status = {
            "workers": {},
            "queues": {},
            "active_tasks": 0,
            "processed_tasks": 0
        }
        
        # Check running workers
        for worker_name, process in self.workers.items():
            try:
                ps_process = psutil.Process(process.pid)
                status["workers"][worker_name] = {
                    "pid": process.pid,
                    "status": "running" if process.poll() is None else "stopped",
                    "cpu_percent": ps_process.cpu_percent(),
                    "memory_mb": ps_process.memory_info().rss / 1024 / 1024,
                    "create_time": ps_process.create_time()
                }
            except (psutil.NoSuchProcess, ProcessLookupError):
                status["workers"][worker_name] = {
                    "status": "not_found"
                }
        
        # Check workers via PID files
        for pid_file in self.pid_file_dir.glob("*.pid"):
            worker_name = pid_file.stem
            if worker_name not in status["workers"]:
                try:
                    with open(pid_file) as f:
                        pid = int(f.read().strip())
                    
                    ps_process = psutil.Process(pid)
                    status["workers"][worker_name] = {
                        "pid": pid,
                        "status": "running",
                        "cpu_percent": ps_process.cpu_percent(),
                        "memory_mb": ps_process.memory_info().rss / 1024 / 1024,
                        "create_time": ps_process.create_time()
                    }
                except (FileNotFoundError, ProcessLookupError, psutil.NoSuchProcess):
                    status["workers"][worker_name] = {
                        "status": "stale_pid"
                    }
        
        # Get Celery inspect information if available
        try:
            inspect = celery_app.control.inspect()
            
            # Active tasks
            active = inspect.active()
            if active:
                status["active_tasks"] = sum(len(tasks) for tasks in active.values())
            
            # Queue lengths
            active_queues = inspect.active_queues()
            if active_queues:
                for worker, queues in active_queues.items():
                    for queue in queues:
                        queue_name = queue["name"]
                        if queue_name not in status["queues"]:
                            status["queues"][queue_name] = []
                        status["queues"][queue_name].append(worker)
            
        except Exception as e:
            logger.warning(f"Could not get Celery inspect data: {e}")
        
        return status
    
    def cleanup_stale_files(self):
        """Clean up stale PID files and logs."""
        for pid_file in self.pid_file_dir.glob("*.pid"):
            try:
                with open(pid_file) as f:
                    pid = int(f.read().strip())
                
                if not psutil.pid_exists(pid):
                    pid_file.unlink()
                    logger.info(f"Cleaned up stale PID file: {pid_file}")
                    
            except (FileNotFoundError, ValueError):
                pid_file.unlink()
                logger.info(f"Cleaned up invalid PID file: {pid_file}")
    
    def monitor_workers(self, interval: int = 60):
        """Monitor workers and restart if needed."""
        logger.info("Starting worker monitoring...")
        
        while True:
            try:
                status = self.get_worker_status()
                
                # Check for failed workers
                for worker_name, worker_status in status["workers"].items():
                    if worker_status.get("status") == "stopped":
                        logger.warning(f"Worker {worker_name} is stopped, restarting...")
                        self.restart_worker(worker_name)
                    elif worker_status.get("status") == "stale_pid":
                        logger.warning(f"Cleaning up stale PID for {worker_name}")
                        pid_file = self.pid_file_dir / f"{worker_name}.pid"
                        if pid_file.exists():
                            pid_file.unlink()
                
                # Log status
                active_workers = sum(1 for s in status["workers"].values() 
                                   if s.get("status") == "running")
                logger.info(f"Monitoring: {active_workers} workers running, "
                           f"{status['active_tasks']} active tasks")
                
                time.sleep(interval)
                
            except KeyboardInterrupt:
                logger.info("Monitoring interrupted")
                break
            except Exception as e:
                logger.error(f"Error in worker monitoring: {e}")
                time.sleep(interval)

def setup_signal_handlers(worker_manager: CeleryWorkerManager):
    """Set up signal handlers for graceful shutdown."""
    def signal_handler(signum, frame):
        logger.info(f"Received signal {signum}, shutting down workers...")
        worker_manager.stop_all_workers()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

def main():
    """Main entry point for worker management."""
    parser = argparse.ArgumentParser(description="Celery Worker Manager for Purview CLI")
    parser.add_argument("action", choices=[
        "start", "stop", "restart", "status", "monitor", "cleanup"
    ], help="Action to perform")
    parser.add_argument("--worker", help="Specific worker name (optional)")
    parser.add_argument("--monitor-interval", type=int, default=60,
                       help="Monitoring interval in seconds")
    
    args = parser.parse_args()
    
    worker_manager = CeleryWorkerManager()
    setup_signal_handlers(worker_manager)
    
    try:
        if args.action == "start":
            if args.worker:
                config = next((c for c in worker_manager.worker_configs 
                             if c.name == args.worker), None)
                if config:
                    success = worker_manager.start_worker(config)
                    sys.exit(0 if success else 1)
                else:
                    logger.error(f"Worker {args.worker} not found")
                    sys.exit(1)
            else:
                success = worker_manager.start_all_workers()
                sys.exit(0 if success else 1)
        
        elif args.action == "stop":
            if args.worker:
                success = worker_manager.stop_worker(args.worker)
                sys.exit(0 if success else 1)
            else:
                success = worker_manager.stop_all_workers()
                sys.exit(0 if success else 1)
        
        elif args.action == "restart":
            if args.worker:
                success = worker_manager.restart_worker(args.worker)
                sys.exit(0 if success else 1)
            else:
                success = worker_manager.restart_all_workers()
                sys.exit(0 if success else 1)
        
        elif args.action == "status":
            status = worker_manager.get_worker_status()
            print(f"\nWorker Status:")
            print(f"{'=' * 50}")
            
            for worker_name, worker_status in status["workers"].items():
                print(f"Worker: {worker_name}")
                print(f"  Status: {worker_status.get('status', 'unknown')}")
                if "pid" in worker_status:
                    print(f"  PID: {worker_status['pid']}")
                    print(f"  CPU: {worker_status.get('cpu_percent', 0):.1f}%")
                    print(f"  Memory: {worker_status.get('memory_mb', 0):.1f} MB")
                print()
            
            print(f"Active Tasks: {status['active_tasks']}")
            print(f"Queues: {list(status['queues'].keys())}")
        
        elif args.action == "monitor":
            worker_manager.monitor_workers(args.monitor_interval)
        
        elif args.action == "cleanup":
            worker_manager.cleanup_stale_files()
            logger.info("Cleanup completed")
    
    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
