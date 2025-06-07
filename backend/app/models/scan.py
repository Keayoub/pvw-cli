from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum

class ScanStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class DataSourceType(str, Enum):
    SQL_SERVER = "sql_server"
    ORACLE = "oracle"
    MYSQL = "mysql"
    POSTGRESQL = "postgresql"
    AZURE_SQL = "azure_sql"
    AZURE_BLOB = "azure_blob"
    AZURE_DATA_LAKE = "azure_data_lake"
    AWS_S3 = "aws_s3"
    POWER_BI = "power_bi"
    TABLEAU = "tableau"

class Scan(BaseModel):
    id: str
    name: str
    data_source_type: DataSourceType
    connection_details: Dict[str, Any]
    scan_rule_set: Optional[str] = None
    schedule: Optional[Dict[str, Any]] = None
    status: ScanStatus = ScanStatus.PENDING
    created_at: datetime
    updated_at: datetime
    last_run_at: Optional[datetime] = None
    next_run_at: Optional[datetime] = None
    created_by: str
    
    class Config:
        use_enum_values = True

class ScanCreateRequest(BaseModel):
    name: str
    data_source_type: str
    connection_details: Dict[str, Any]
    scan_rule_set: Optional[str] = None
    schedule: Optional[Dict[str, Any]] = None

class ScanResponse(BaseModel):
    id: str
    name: str
    data_source_type: str
    status: str
    created_at: datetime
    updated_at: datetime
    last_run_at: Optional[datetime] = None
    next_run_at: Optional[datetime] = None
    progress: Optional[float] = None
    entities_discovered: Optional[int] = None
    entities_processed: Optional[int] = None
    error_message: Optional[str] = None

class ScanExecution(BaseModel):
    id: str
    scan_id: str
    status: ScanStatus
    started_at: datetime
    completed_at: Optional[datetime] = None
    progress: float = 0.0
    entities_discovered: int = 0
    entities_processed: int = 0
    errors_count: int = 0
    log_messages: List[str] = Field(default_factory=list)
    
    class Config:
        use_enum_values = True
