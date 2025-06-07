"""
SQLAlchemy database models for the Purview CLI application.
"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, JSON, ForeignKey, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class User(Base):
    """User model for authentication and authorization."""
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, nullable=False, default="analyst")
    department = Column(String)
    permissions = Column(JSON)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime)
    
    # Relationships
    created_policies = relationship("GovernancePolicy", back_populates="creator")
    steward_assignments = relationship("StewardAssignment", back_populates="steward")
    audit_logs = relationship("AuditLog", back_populates="user")

class Entity(Base):
    """Entity model for data assets."""
    __tablename__ = "entities"
    
    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    qualified_name = Column(String, unique=True, nullable=False)
    entity_type = Column(String, nullable=False, index=True)
    description = Column(Text)
    properties = Column(JSON)
    classifications = Column(JSON)
    status = Column(String, default="active")
    source_system = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_scanned = Column(DateTime)
    
    # Relationships
    scan_results = relationship("ScanResult", back_populates="entity")
    steward_assignments = relationship("StewardAssignment", back_populates="entity")

class DataSource(Base):
    """Data source model for scan configurations."""
    __tablename__ = "data_sources"
    
    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    type = Column(String, nullable=False)
    connection_string = Column(String)
    configuration = Column(JSON)
    credentials = Column(JSON)  # Encrypted
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_scan_time = Column(DateTime)
    
    # Relationships
    scans = relationship("Scan", back_populates="data_source")

class Scan(Base):
    """Scan model for data discovery operations."""
    __tablename__ = "scans"
    
    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    data_source_id = Column(String, ForeignKey("data_sources.id"), nullable=False)
    scan_type = Column(String, nullable=False)
    status = Column(String, default="pending")
    progress = Column(Float, default=0.0)
    configuration = Column(JSON)
    scheduled_time = Column(DateTime)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    error_message = Column(Text)
    created_by = Column(String, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    data_source = relationship("DataSource", back_populates="scans")
    scan_results = relationship("ScanResult", back_populates="scan")

class ScanResult(Base):
    """Scan result model for discovered assets."""
    __tablename__ = "scan_results"
    
    id = Column(String, primary_key=True, index=True)
    scan_id = Column(String, ForeignKey("scans.id"), nullable=False)
    entity_id = Column(String, ForeignKey("entities.id"))
    result_type = Column(String, nullable=False)
    data = Column(JSON)
    status = Column(String, default="discovered")
    confidence_score = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    scan = relationship("Scan", back_populates="scan_results")
    entity = relationship("Entity", back_populates="scan_results")

class GovernancePolicy(Base):
    """Governance policy model."""
    __tablename__ = "governance_policies"
    
    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    description = Column(Text)
    policy_type = Column(String, nullable=False)
    status = Column(String, default="draft")
    rules = Column(JSON)
    created_by = Column(String, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    creator = relationship("User", back_populates="created_policies")
    compliance_results = relationship("ComplianceResult", back_populates="policy")

class Classification(Base):
    """Classification model for data sensitivity levels."""
    __tablename__ = "classifications"
    
    id = Column(String, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(Text)
    level = Column(Integer, nullable=False)
    color = Column(String, default="#666666")
    rules = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class StewardAssignment(Base):
    """Data steward assignment model."""
    __tablename__ = "steward_assignments"
    
    id = Column(String, primary_key=True, index=True)
    entity_id = Column(String, ForeignKey("entities.id"), nullable=False)
    steward_id = Column(String, ForeignKey("users.id"), nullable=False)
    responsibility_level = Column(String, default="full")
    notes = Column(Text)
    status = Column(String, default="active")
    assigned_by = Column(String, ForeignKey("users.id"))
    assigned_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    entity = relationship("Entity", back_populates="steward_assignments")
    steward = relationship("User", back_populates="steward_assignments")

class ComplianceResult(Base):
    """Compliance check result model."""
    __tablename__ = "compliance_results"
    
    id = Column(String, primary_key=True, index=True)
    entity_id = Column(String, nullable=False)
    policy_id = Column(String, ForeignKey("governance_policies.id"), nullable=False)
    status = Column(String, nullable=False)
    score = Column(Float)
    issues = Column(JSON)
    recommendations = Column(JSON)
    checked_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    policy = relationship("GovernancePolicy", back_populates="compliance_results")

class AuditLog(Base):
    """Audit log model for tracking user actions."""
    __tablename__ = "audit_logs"
    
    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"))
    action = Column(String, nullable=False)
    entity_type = Column(String)
    entity_id = Column(String)
    details = Column(Text)
    ip_address = Column(String)
    user_agent = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="audit_logs")

class LineageRelationship(Base):
    """Data lineage relationship model."""
    __tablename__ = "lineage_relationships"
    
    id = Column(String, primary_key=True, index=True)
    source_entity_id = Column(String, nullable=False)
    target_entity_id = Column(String, nullable=False)
    relationship_type = Column(String, nullable=False)  # input, output, derived_from
    properties = Column(JSON)
    confidence_score = Column(Float, default=1.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class DataQualityMetric(Base):
    """Data quality metrics model."""
    __tablename__ = "data_quality_metrics"
    
    id = Column(String, primary_key=True, index=True)
    entity_id = Column(String, nullable=False)
    metric_type = Column(String, nullable=False)  # completeness, accuracy, consistency, etc.
    score = Column(Float, nullable=False)
    details = Column(JSON)
    measured_at = Column(DateTime, default=datetime.utcnow)

class UserSession(Base):
    """User session model for tracking active sessions."""
    __tablename__ = "user_sessions"
    
    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    session_token = Column(String, unique=True, nullable=False)
    refresh_token = Column(String, unique=True)
    ip_address = Column(String)
    user_agent = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_activity = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime)
    is_active = Column(Boolean, default=True)

class UploadedFile(Base):
    """Model for tracking uploaded files."""
    __tablename__ = "uploaded_files"
    
    file_id = Column(String, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    original_filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    size = Column(Integer, nullable=False)
    mime_type = Column(String, nullable=False)
    uploaded_by = Column(String, ForeignKey("users.id"), nullable=False)
    upload_time = Column(DateTime, default=datetime.utcnow)
    status = Column(String, default="uploaded")  # uploaded, processing, processed, failed, deleted
    
    # Relationships
    uploader = relationship("User", foreign_keys=[uploaded_by])
    processing_jobs = relationship("ProcessingJob", back_populates="file")

class ProcessingJob(Base):
    """Model for tracking file processing jobs."""
    __tablename__ = "processing_jobs"
    
    job_id = Column(String, primary_key=True, index=True)
    file_id = Column(String, ForeignKey("uploaded_files.file_id"), nullable=False)
    operation_type = Column(String, nullable=False)  # import_entities, bulk_classification, etc.
    target_entity_type = Column(String)
    options = Column(JSON)
    status = Column(String, default="queued")  # queued, processing, completed, failed, cancelled
    progress = Column(Integer, default=0)
    result = Column(JSON)
    error = Column(Text)
    celery_task_id = Column(String, index=True)  # Celery task ID for tracking
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    created_by = Column(String, ForeignKey("users.id"))
    
    # Relationships
    file = relationship("UploadedFile", back_populates="processing_jobs")
    creator = relationship("User", foreign_keys=[created_by])
