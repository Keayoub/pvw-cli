from typing import Dict, Any, List, Optional
import structlog
from datetime import datetime, timedelta
import asyncio
import uuid

from app.core.config import settings
from app.core.logging import get_logger
from app.models.scan import ScanCreateRequest, ScanResponse, ScanStatus, ScanExecution

logger = get_logger(__name__)

class ScanningService:
    """Service for managing data scans"""
    
    def __init__(self):
        self.scans_db = {}  # Mock database
        self.executions_db = {}  # Mock database
    
    async def get_scans(
        self,
        page: int = 1,
        page_size: int = 25,
        status_filter: Optional[ScanStatus] = None
    ) -> Dict[str, Any]:
        """Get paginated list of scans"""
        try:
            # Mock implementation
            mock_scans = [
                ScanResponse(
                    id=f"scan_{i}",
                    name=f"Sample Scan {i}",
                    data_source_type="sql_server",
                    status="completed" if i % 2 == 0 else "running",
                    created_at=datetime.utcnow() - timedelta(days=i),
                    updated_at=datetime.utcnow(),
                    last_run_at=datetime.utcnow() - timedelta(hours=i),
                    next_run_at=datetime.utcnow() + timedelta(hours=24),
                    progress=100.0 if i % 2 == 0 else 45.0,
                    entities_discovered=150 + i * 10,
                    entities_processed=150 + i * 10 if i % 2 == 0 else 75 + i * 5
                )
                for i in range(1, 11)
            ]
            
            # Apply status filter
            if status_filter:
                mock_scans = [s for s in mock_scans if s.status == status_filter]
            
            # Apply pagination
            start_idx = (page - 1) * page_size
            end_idx = start_idx + page_size
            paginated_scans = mock_scans[start_idx:end_idx]
            
            return {
                "scans": paginated_scans,
                "total_count": len(mock_scans),
                "page": page,
                "page_size": page_size
            }
            
        except Exception as e:
            logger.error("Failed to get scans", error=str(e))
            raise
    
    async def get_scan(self, scan_id: str) -> Optional[ScanResponse]:
        """Get scan by ID"""
        try:
            if scan_id.startswith("scan_"):
                return ScanResponse(
                    id=scan_id,
                    name="Sample Scan",
                    data_source_type="sql_server",
                    status="completed",
                    created_at=datetime.utcnow() - timedelta(days=7),
                    updated_at=datetime.utcnow(),
                    last_run_at=datetime.utcnow() - timedelta(hours=2),
                    next_run_at=datetime.utcnow() + timedelta(hours=22),
                    progress=100.0,
                    entities_discovered=150,
                    entities_processed=150
                )
            return None
            
        except Exception as e:
            logger.error("Failed to get scan", scan_id=scan_id, error=str(e))
            raise
    
    async def create_scan(self, create_request: ScanCreateRequest) -> ScanResponse:
        """Create a new scan"""
        try:
            scan_id = f"scan_{uuid.uuid4().hex[:8]}"
            
            scan = ScanResponse(
                id=scan_id,
                name=create_request.name,
                data_source_type=create_request.data_source_type,
                status="pending",
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
                progress=0.0,
                entities_discovered=0,
                entities_processed=0
            )
            
            # Store in mock database
            self.scans_db[scan_id] = scan
            
            logger.info("Scan created", scan_id=scan_id, name=create_request.name)
            return scan
            
        except Exception as e:
            logger.error("Failed to create scan", error=str(e))
            raise
    
    async def update_scan(
        self,
        scan_id: str,
        name: Optional[str] = None,
        connection_details: Optional[Dict[str, Any]] = None,
        scan_rule_set: Optional[str] = None,
        schedule: Optional[Dict[str, Any]] = None
    ) -> Optional[ScanResponse]:
        """Update an existing scan"""
        try:
            scan = await self.get_scan(scan_id)
            if not scan:
                return None
            
            if name:
                scan.name = name
            
            scan.updated_at = datetime.utcnow()
            
            # Update in mock database
            self.scans_db[scan_id] = scan
            
            return scan
            
        except Exception as e:
            logger.error("Failed to update scan", scan_id=scan_id, error=str(e))
            raise
    
    async def delete_scan(self, scan_id: str) -> bool:
        """Delete a scan"""
        try:
            scan = await self.get_scan(scan_id)
            if not scan:
                return False
            
            # Remove from mock database
            if scan_id in self.scans_db:
                del self.scans_db[scan_id]
            
            return True
            
        except Exception as e:
            logger.error("Failed to delete scan", scan_id=scan_id, error=str(e))
            raise
    
    async def start_scan(self, scan_id: str) -> bool:
        """Start a scan execution"""
        try:
            scan = await self.get_scan(scan_id)
            if not scan:
                return False
            
            # Create execution record
            execution_id = f"exec_{uuid.uuid4().hex[:8]}"
            execution = ScanExecution(
                id=execution_id,
                scan_id=scan_id,
                status=ScanStatus.RUNNING,
                started_at=datetime.utcnow(),
                progress=0.0,
                entities_discovered=0,
                entities_processed=0,
                errors_count=0,
                log_messages=["Scan started"]
            )
            
            self.executions_db[execution_id] = execution
            
            # Update scan status
            scan.status = "running"
            scan.last_run_at = datetime.utcnow()
            scan.progress = 0.0
            
            # Start background task to simulate scan progress
            asyncio.create_task(self._simulate_scan_progress(scan_id, execution_id))
            
            return True
            
        except Exception as e:
            logger.error("Failed to start scan", scan_id=scan_id, error=str(e))
            raise
    
    async def stop_scan(self, scan_id: str) -> bool:
        """Stop a running scan"""
        try:
            scan = await self.get_scan(scan_id)
            if not scan or scan.status != "running":
                return False
            
            scan.status = "cancelled"
            scan.updated_at = datetime.utcnow()
            
            return True
            
        except Exception as e:
            logger.error("Failed to stop scan", scan_id=scan_id, error=str(e))
            raise
    
    async def get_scan_status(self, scan_id: str) -> Optional[Dict[str, Any]]:
        """Get scan status and progress"""
        try:
            scan = await self.get_scan(scan_id)
            if not scan:
                return None
            
            return {
                "scan_id": scan_id,
                "status": scan.status,
                "progress": scan.progress,
                "entities_discovered": scan.entities_discovered,
                "entities_processed": scan.entities_processed,
                "last_updated": scan.updated_at.isoformat()
            }
            
        except Exception as e:
            logger.error("Failed to get scan status", scan_id=scan_id, error=str(e))
            raise
    
    async def get_scan_logs(
        self,
        scan_id: str,
        page: int = 1,
        page_size: int = 100
    ) -> Dict[str, Any]:
        """Get scan execution logs"""
        try:
            # Mock implementation
            logs = [
                {
                    "timestamp": (datetime.utcnow() - timedelta(minutes=i)).isoformat(),
                    "level": "INFO" if i % 3 != 0 else "WARNING",
                    "message": f"Scan log message {i}: Processing entity batch {i}"
                }
                for i in range(1, 51)
            ]
            
            # Apply pagination
            start_idx = (page - 1) * page_size
            end_idx = start_idx + page_size
            paginated_logs = logs[start_idx:end_idx]
            
            return {
                "logs": paginated_logs,
                "total_count": len(logs),
                "page": page,
                "page_size": page_size
            }
            
        except Exception as e:
            logger.error("Failed to get scan logs", scan_id=scan_id, error=str(e))
            raise
    
    async def get_scan_templates(self, data_source_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get available scan templates"""
        try:
            templates = [
                {
                    "id": "sql_server_basic",
                    "name": "SQL Server Basic Scan",
                    "data_source_type": "sql_server",
                    "description": "Basic scan for SQL Server databases",
                    "configuration": {
                        "include_system_databases": False,
                        "scan_stored_procedures": True,
                        "max_depth": 3
                    }
                },
                {
                    "id": "azure_blob_full",
                    "name": "Azure Blob Storage Full Scan",
                    "data_source_type": "azure_blob",
                    "description": "Comprehensive scan for Azure Blob Storage",
                    "configuration": {
                        "include_metadata": True,
                        "scan_file_contents": True,
                        "file_size_limit": "100MB"
                    }
                }
            ]
            
            if data_source_type:
                templates = [t for t in templates if t["data_source_type"] == data_source_type]
            
            return templates
            
        except Exception as e:
            logger.error("Failed to get scan templates", error=str(e))
            raise
    
    async def get_supported_data_sources(self) -> List[Dict[str, Any]]:
        """Get supported data source types"""
        try:
            return [
                {"type": "sql_server", "name": "SQL Server", "category": "database"},
                {"type": "oracle", "name": "Oracle Database", "category": "database"},
                {"type": "mysql", "name": "MySQL", "category": "database"},
                {"type": "postgresql", "name": "PostgreSQL", "category": "database"},
                {"type": "azure_sql", "name": "Azure SQL Database", "category": "cloud_database"},
                {"type": "azure_blob", "name": "Azure Blob Storage", "category": "cloud_storage"},
                {"type": "azure_data_lake", "name": "Azure Data Lake", "category": "cloud_storage"},
                {"type": "aws_s3", "name": "Amazon S3", "category": "cloud_storage"},
                {"type": "power_bi", "name": "Power BI", "category": "bi_tool"},
                {"type": "tableau", "name": "Tableau", "category": "bi_tool"}
            ]
            
        except Exception as e:
            logger.error("Failed to get supported data sources", error=str(e))
            raise
    
    async def _simulate_scan_progress(self, scan_id: str, execution_id: str):
        """Simulate scan progress (for demo purposes)"""
        try:
            scan = await self.get_scan(scan_id)
            if not scan:
                return
            
            execution = self.executions_db.get(execution_id)
            if not execution:
                return
            
            # Simulate progress over 30 seconds
            for progress in range(0, 101, 10):
                await asyncio.sleep(3)  # Wait 3 seconds between updates
                
                # Update execution
                execution.progress = float(progress)
                execution.entities_discovered = int(150 * (progress / 100))
                execution.entities_processed = int(120 * (progress / 100))
                execution.log_messages.append(f"Progress: {progress}% - Processed {execution.entities_processed} entities")
                
                # Update scan
                scan.progress = float(progress)
                scan.entities_discovered = execution.entities_discovered
                scan.entities_processed = execution.entities_processed
                scan.updated_at = datetime.utcnow()
                
                logger.info("Scan progress updated", scan_id=scan_id, progress=progress)
            
            # Complete the scan
            execution.status = ScanStatus.COMPLETED
            execution.completed_at = datetime.utcnow()
            execution.log_messages.append("Scan completed successfully")
            
            scan.status = "completed"
            scan.progress = 100.0
            scan.updated_at = datetime.utcnow()
            
            logger.info("Scan completed", scan_id=scan_id)
            
        except Exception as e:
            logger.error("Error in scan simulation", scan_id=scan_id, error=str(e))
