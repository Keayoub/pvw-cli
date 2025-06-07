"""
File Processing Service for handling uploaded files and data processing operations.
Supports CSV, Excel, JSON, and text files with background processing capabilities.
"""
import os
import json
import uuid
import asyncio
from typing import Dict, List, Optional, Any, Callable
from pathlib import Path
from datetime import datetime, timedelta
import pandas as pd
import openpyxl
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func, and_

from app.core.config import settings
from app.core.logging import get_logger
from app.database.connection import get_db_session
from app.database.models import (
    ProcessingJob, UploadedFile, User, Entity, DataSource, 
    Classification, GovernancePolicy
)
from app.services.cache_service import CacheService, cache_result
# Note: EntitiesService imported dynamically to avoid circular imports
from app.services.analytics_service import AnalyticsService
from app.services.governance_service import GovernanceService
from app.tasks.file_processing import (
    process_file_async,
    import_entities_task,
    bulk_classification_task,
    data_quality_check_task,
    lineage_discovery_task,
    metadata_extraction_task,
    compliance_scan_task,
    data_profiling_task
)

logger = get_logger(__name__)

class FileProcessingService:
    """Service for processing uploaded files with various data operations."""
    
    def __init__(self):
        self.cache_service = CacheService()
        self._entities_service = None  # Lazy loaded to avoid circular imports
        self.analytics_service = AnalyticsService()
        self.governance_service = GovernanceService()
        
        # Supported file formats
        self.supported_formats = {
            '.csv': self._process_csv_file,
            '.xlsx': self._process_excel_file,
            '.xls': self._process_excel_file,
            '.json': self._process_json_file,
            '.txt': self._process_text_file
        }
        
        # Supported operations
        self.supported_operations = {
            'import_entities': self._import_entities_operation,
            'bulk_classification': self._bulk_classification_operation,
            'data_quality_check': self._data_quality_check_operation,
            'lineage_discovery': self._lineage_discovery_operation,
            'metadata_extraction': self._metadata_extraction_operation,
            'compliance_scan': self._compliance_scan_operation,
            'data_profiling': self._data_profiling_operation
        }
    
    @property
    def entities_service(self):
        """Lazy load entities service to avoid circular imports."""
        if self._entities_service is None:
            from app.services.entities_service import EntitiesService
            self._entities_service = EntitiesService()
        return self._entities_service
    
    async def create_file_record(
        self,
        file_id: str,
        filename: str,
        original_filename: str,
        file_path: str,
        size: int,
        mime_type: str,
        uploaded_by: str
    ) -> Dict[str, Any]:
        """Create a file record in the database."""
        try:
            async with get_db_session() as session:
                file_record = UploadedFile(
                    file_id=file_id,
                    filename=filename,
                    original_filename=original_filename,
                    file_path=file_path,
                    size=size,
                    mime_type=mime_type,
                    uploaded_by=uploaded_by,
                    upload_time=datetime.utcnow(),
                    status="uploaded"
                )
                
                session.add(file_record)
                await session.commit()
                await session.refresh(file_record)
                
                return {
                    "file_id": file_record.file_id,
                    "filename": file_record.filename,
                    "original_filename": file_record.original_filename,
                    "upload_time": file_record.upload_time.isoformat(),
                    "status": file_record.status
                }
                
        except Exception as e:
            logger.error("Failed to create file record", error=str(e), file_id=file_id)
            raise
    
    async def get_file_info(self, file_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        """Get file information."""
        try:
            async with get_db_session() as session:
                result = await session.execute(
                    select(UploadedFile)
                    .where(
                        and_(
                            UploadedFile.file_id == file_id,
                            UploadedFile.uploaded_by == user_id
                        )
                    )
                )
                file_record = result.scalar_one_or_none()
                
                if not file_record:
                    return None
                
                # Get processing jobs for this file
                jobs_result = await session.execute(
                    select(ProcessingJob)
                    .where(ProcessingJob.file_id == file_id)
                    .order_by(ProcessingJob.created_at.desc())
                )
                jobs = jobs_result.scalars().all()
                
                return {
                    "file_id": file_record.file_id,
                    "filename": file_record.filename,
                    "original_filename": file_record.original_filename,
                    "file_path": file_record.file_path,
                    "size": file_record.size,
                    "mime_type": file_record.mime_type,
                    "upload_time": file_record.upload_time.isoformat(),
                    "status": file_record.status,
                    "processing_jobs": [
                        {
                            "job_id": job.job_id,
                            "operation_type": job.operation_type,
                            "status": job.status,
                            "created_at": job.created_at.isoformat(),
                            "completed_at": job.completed_at.isoformat() if job.completed_at else None,
                            "progress": job.progress,
                            "result": job.result
                        }
                        for job in jobs
                    ]
                }
                
        except Exception as e:
            logger.error("Failed to get file info", error=str(e), file_id=file_id)
            raise
    
    async def get_user_files(
        self,
        user_id: str,
        page: int = 1,
        page_size: int = 25,
        status_filter: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get files uploaded by a user."""
        try:
            async with get_db_session() as session:
                # Build query
                query = select(UploadedFile).where(UploadedFile.uploaded_by == user_id)
                
                if status_filter:
                    query = query.where(UploadedFile.status == status_filter)
                
                # Get total count
                count_result = await session.execute(
                    select(func.count()).select_from(query.subquery())
                )
                total_count = count_result.scalar()
                
                # Apply pagination
                offset = (page - 1) * page_size
                query = query.offset(offset).limit(page_size).order_by(UploadedFile.upload_time.desc())
                
                result = await session.execute(query)
                files = result.scalars().all()
                
                return {
                    "files": [
                        {
                            "file_id": file.file_id,
                            "filename": file.filename,
                            "original_filename": file.original_filename,
                            "size": file.size,
                            "mime_type": file.mime_type,
                            "upload_time": file.upload_time.isoformat(),
                            "status": file.status,
                            "processing_job_id": None  # Will be populated if needed
                        }
                        for file in files
                    ],
                    "total_count": total_count,
                    "page": page,
                    "page_size": page_size
                }
                
        except Exception as e:
            logger.error("Failed to get user files", error=str(e), user_id=user_id)
            raise
    
    async def preview_file(
        self,
        file_id: str,
        user_id: str,
        rows: int = 10
    ) -> Dict[str, Any]:
        """Preview file contents."""
        try:
            file_info = await self.get_file_info(file_id, user_id)
            if not file_info:
                raise ValueError("File not found")
            
            file_path = Path(file_info["file_path"])
            if not file_path.exists():
                raise ValueError("File not found on disk")
            
            file_ext = file_path.suffix.lower()
            
            if file_ext == '.csv':
                df = pd.read_csv(file_path, nrows=rows)
                return {
                    "columns": df.columns.tolist(),
                    "data": df.to_dict('records'),
                    "total_rows": len(df),
                    "preview_rows": min(rows, len(df))
                }
            
            elif file_ext in ['.xlsx', '.xls']:
                df = pd.read_excel(file_path, nrows=rows)
                return {
                    "columns": df.columns.tolist(),
                    "data": df.to_dict('records'),
                    "total_rows": len(df),
                    "preview_rows": min(rows, len(df))
                }
            
            elif file_ext == '.json':
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                if isinstance(data, list):
                    preview_data = data[:rows]
                    return {
                        "type": "array",
                        "data": preview_data,
                        "total_items": len(data),
                        "preview_items": len(preview_data)
                    }
                else:
                    return {
                        "type": "object",
                        "data": data,
                        "keys": list(data.keys()) if isinstance(data, dict) else []
                    }
            
            elif file_ext == '.txt':
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()[:rows]
                
                return {
                    "type": "text",
                    "lines": [line.rstrip('\n\r') for line in lines],
                    "preview_lines": len(lines)
                }
            
            else:
                raise ValueError(f"Unsupported file format: {file_ext}")
                
        except Exception as e:
            logger.error("Failed to preview file", error=str(e), file_id=file_id)
            raise
    
    async def delete_file(self, file_id: str, user_id: str) -> bool:
        """Delete a file and its associated records."""
        try:
            async with get_db_session() as session:
                # Get file record
                result = await session.execute(
                    select(UploadedFile)
                    .where(
                        and_(
                            UploadedFile.file_id == file_id,
                            UploadedFile.uploaded_by == user_id
                        )
                    )
                )
                file_record = result.scalar_one_or_none()
                
                if not file_record:
                    return False
                
                # Delete physical file
                file_path = Path(file_record.file_path)
                if file_path.exists():
                    file_path.unlink()
                
                # Delete processing jobs
                await session.execute(
                    delete(ProcessingJob).where(ProcessingJob.file_id == file_id)
                )
                
                # Delete file record
                await session.delete(file_record)
                await session.commit()
                      # Clear cache
            await self.cache_service.delete_pattern(f"file:{file_id}:*")
            
            return True
            
        except Exception as e:
            logger.error("Failed to delete file", error=str(e), file_id=file_id)
            raise
    
    async def queue_file_processing(
        self,
        file_id: str,
        operation_type: str,
        target_entity_type: Optional[str] = None,
        options: Optional[Dict[str, Any]] = None,
        user_id: str = None
    ) -> str:
        """Queue a file processing job."""
        try:
            if operation_type not in self.supported_operations:
                raise ValueError(f"Unsupported operation: {operation_type}")
            
            job_id = str(uuid.uuid4())
            
            async with get_db_session() as session:
                job = ProcessingJob(
                    job_id=job_id,
                    file_id=file_id,
                    operation_type=operation_type,
                    target_entity_type=target_entity_type,
                    options=options or {},
                    status="queued",
                    progress=0,
                    created_at=datetime.utcnow(),
                    created_by=user_id
                )
                
                session.add(job)
                await session.commit()
            
            # Dispatch appropriate Celery task based on operation type
            task_map = {
                'import_entities': import_entities_task,
                'bulk_classification': bulk_classification_task,
                'data_quality_check': data_quality_check_task,
                'lineage_discovery': lineage_discovery_task,
                'metadata_extraction': metadata_extraction_task,
                'compliance_scan': compliance_scan_task,
                'data_profiling': data_profiling_task
            }
            
            task = task_map.get(operation_type)
            if task:
                # Queue the Celery task
                result = task.delay(
                    file_id=file_id,
                    job_id=job_id,
                    target_entity_type=target_entity_type,
                    options=options or {}
                )
                
                # Update job with Celery task ID
                async with get_db_session() as session:
                    await session.execute(
                        update(ProcessingJob)
                        .where(ProcessingJob.job_id == job_id)
                        .values(celery_task_id=result.id)
                    )
                    await session.commit()
                
                logger.info("Celery task dispatched", 
                           job_id=job_id, 
                           file_id=file_id, 
                           operation=operation_type,
                           celery_task_id=result.id)
            else:
                # Fallback to process_file_async for generic processing
                result = process_file_async.delay(
                    file_id=file_id,
                    job_id=job_id,
                    operation_type=operation_type,
                    target_entity_type=target_entity_type,
                    options=options or {}
                )
                
                async with get_db_session() as session:
                    await session.execute(
                        update(ProcessingJob)
                        .where(ProcessingJob.job_id == job_id)
                        .values(celery_task_id=result.id)
                    )
                    await session.commit()
                
                logger.info("Generic processing task dispatched",
                           job_id=job_id,
                           file_id=file_id,
                           celery_task_id=result.id)
            
            return job_id
            
        except Exception as e:
            logger.error("Failed to queue processing job", error=str(e), file_id=file_id)
            raise
    
    async def process_file_background(self, file_id: str, job_id: str):
        """Process file in background."""
        try:
            await self._update_job_status(job_id, "processing", 0)
            
            # Get job details
            async with get_db_session() as session:
                result = await session.execute(
                    select(ProcessingJob).where(ProcessingJob.job_id == job_id)
                )
                job = result.scalar_one_or_none()
                
                if not job:
                    raise ValueError("Job not found")
                
                # Get file info
                file_result = await session.execute(
                    select(UploadedFile).where(UploadedFile.file_id == file_id)
                )
                file_record = file_result.scalar_one_or_none()
                
                if not file_record:
                    raise ValueError("File not found")
            
            # Process file based on format
            file_path = Path(file_record.file_path)
            file_ext = file_path.suffix.lower()
            
            if file_ext not in self.supported_formats:
                raise ValueError(f"Unsupported file format: {file_ext}")
            
            # Load and process file
            processor = self.supported_formats[file_ext]
            file_data = await processor(file_path)
            
            # Execute operation
            operation = self.supported_operations[job.operation_type]
            result = await operation(
                file_data, 
                job.target_entity_type, 
                job.options,
                lambda progress: asyncio.create_task(self._update_job_progress(job_id, progress))
            )
            
            # Update job completion
            await self._update_job_status(job_id, "completed", 100, result)
            
            logger.info("File processing completed", job_id=job_id, file_id=file_id)
            
        except Exception as e:
            logger.error("File processing failed", error=str(e), job_id=job_id, file_id=file_id)
            await self._update_job_status(job_id, "failed", error=str(e))
    
    async def get_processing_status(self, file_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        """Get processing status for a file."""
        try:
            async with get_db_session() as session:
                # Verify file belongs to user
                file_result = await session.execute(
                    select(UploadedFile)
                    .where(
                        and_(
                            UploadedFile.file_id == file_id,
                            UploadedFile.uploaded_by == user_id
                        )
                    )
                )
                file_record = file_result.scalar_one_or_none()
                
                if not file_record:
                    return None
                
                # Get latest processing job
                job_result = await session.execute(
                    select(ProcessingJob)
                    .where(ProcessingJob.file_id == file_id)
                    .order_by(ProcessingJob.created_at.desc())
                    .limit(1)
                )
                job = job_result.scalar_one_or_none()
                
                if not job:
                    return {
                        "file_id": file_id,
                        "status": "no_processing",
                        "message": "No processing jobs found for this file"
                    }
                
                return {
                    "file_id": file_id,
                    "job_id": job.job_id,
                    "operation_type": job.operation_type,
                    "status": job.status,
                    "progress": job.progress,
                    "created_at": job.created_at.isoformat(),
                    "completed_at": job.completed_at.isoformat() if job.completed_at else None,
                    "result": job.result,
                    "error": job.error
                }
                
        except Exception as e:
            logger.error("Failed to get processing status", error=str(e), file_id=file_id)
            raise
    
    # File format processors
    async def _process_csv_file(self, file_path: Path) -> Dict[str, Any]:
        """Process CSV file."""
        try:
            df = pd.read_csv(file_path)
            return {
                "format": "csv",
                "columns": df.columns.tolist(),
                "rows": len(df),
                "data": df,
                "sample": df.head(5).to_dict('records')
            }
        except Exception as e:
            logger.error("Failed to process CSV file", error=str(e), file_path=str(file_path))
            raise
    
    async def _process_excel_file(self, file_path: Path) -> Dict[str, Any]:
        """Process Excel file."""
        try:
            df = pd.read_excel(file_path)
            return {
                "format": "excel",
                "columns": df.columns.tolist(),
                "rows": len(df),
                "data": df,
                "sample": df.head(5).to_dict('records')
            }
        except Exception as e:
            logger.error("Failed to process Excel file", error=str(e), file_path=str(file_path))
            raise
    
    async def _process_json_file(self, file_path: Path) -> Dict[str, Any]:
        """Process JSON file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            return {
                "format": "json",
                "type": "array" if isinstance(data, list) else "object",
                "size": len(data) if isinstance(data, list) else 1,
                "data": data,
                "sample": data[:5] if isinstance(data, list) else data
            }
        except Exception as e:
            logger.error("Failed to process JSON file", error=str(e), file_path=str(file_path))
            raise
    
    async def _process_text_file(self, file_path: Path) -> Dict[str, Any]:
        """Process text file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
            
            return {
                "format": "text",
                "lines": len(lines),
                "content": content,
                "sample": lines[:10]
            }
        except Exception as e:
            logger.error("Failed to process text file", error=str(e), file_path=str(file_path))
            raise
    
    # Operation processors
    async def _import_entities_operation(
        self, 
        file_data: Dict[str, Any], 
        target_entity_type: str,
        options: Dict[str, Any],
        progress_callback: Callable
    ) -> Dict[str, Any]:
        """Import entities from file data."""
        try:
            if file_data["format"] not in ["csv", "excel"]:
                raise ValueError("Entity import only supports CSV and Excel files")
            
            df = file_data["data"]
            total_rows = len(df)
            
            entities_created = []
            errors = []
            
            for index, row in df.iterrows():
                try:
                    await progress_callback(int((index / total_rows) * 100))
                    
                    # Create entity from row data
                    entity_data = {
                        "type_name": target_entity_type or "DataSet",
                        "attributes": {}
                    }
                    
                    # Map columns to attributes
                    for col in df.columns:
                        if pd.notna(row[col]):
                            entity_data["attributes"][col.lower().replace(' ', '_')] = str(row[col])
                    
                    # Ensure required attributes
                    if "name" not in entity_data["attributes"]:
                        entity_data["attributes"]["name"] = f"Entity_{index}"
                    
                    if "qualified_name" not in entity_data["attributes"]:
                        entity_data["attributes"]["qualified_name"] = f"{entity_data['attributes']['name']}@{settings.PURVIEW_CATALOG_NAME}"
                    
                    # Create entity using entities service
                    entity = await self.entities_service.create_entity(entity_data)
                    entities_created.append(entity)
                    
                except Exception as e:
                    errors.append(f"Row {index + 1}: {str(e)}")
            
            return {
                "operation": "import_entities",
                "total_processed": total_rows,
                "entities_created": len(entities_created),
                "errors": errors,
                "success": len(entities_created) > 0
            }
            
        except Exception as e:
            logger.error("Entity import operation failed", error=str(e))
            raise
    
    async def _bulk_classification_operation(
        self,
        file_data: Dict[str, Any],
        target_entity_type: str,
        options: Dict[str, Any],
        progress_callback: Callable
    ) -> Dict[str, Any]:
        """Bulk classification operation."""
        try:
            if file_data["format"] not in ["csv", "excel"]:
                raise ValueError("Bulk classification only supports CSV and Excel files")
            
            df = file_data["data"]
            total_rows = len(df)
            
            classifications_applied = []
            errors = []
            
            # Validate required columns
            required_columns = ["entity_guid", "classification_name"]
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                raise ValueError(f"Missing required columns: {', '.join(missing_columns)}")
            
            for index, row in df.iterrows():
                try:
                    await progress_callback(int((index / total_rows) * 100))
                    
                    entity_guid = row["entity_guid"]
                    classification_name = row["classification_name"]
                    
                    # Apply classification using governance service
                    classification_data = {
                        "typeName": classification_name,
                        "attributes": {}
                    }
                    
                    # Add optional attributes
                    for col in df.columns:
                        if col not in required_columns and pd.notna(row[col]):
                            classification_data["attributes"][col] = str(row[col])
                    
                    result = await self.governance_service.apply_classification(
                        entity_guid, classification_data
                    )
                    classifications_applied.append(result)
                    
                except Exception as e:
                    errors.append(f"Row {index + 1}: {str(e)}")
            
            return {
                "operation": "bulk_classification",
                "total_processed": total_rows,
                "classifications_applied": len(classifications_applied),
                "errors": errors,
                "success": len(classifications_applied) > 0
            }
            
        except Exception as e:
            logger.error("Bulk classification operation failed", error=str(e))
            raise
    
    async def _data_quality_check_operation(
        self,
        file_data: Dict[str, Any],
        target_entity_type: str,
        options: Dict[str, Any],
        progress_callback: Callable
    ) -> Dict[str, Any]:
        """Data quality check operation."""
        try:
            if file_data["format"] not in ["csv", "excel"]:
                raise ValueError("Data quality check only supports CSV and Excel files")
            
            df = file_data["data"]
            total_columns = len(df.columns)
            
            quality_metrics = {
                "completeness": {},
                "uniqueness": {},
                "validity": {},
                "consistency": {}
            }
            
            for index, col in enumerate(df.columns):
                await progress_callback(int((index / total_columns) * 100))
                
                # Completeness check
                null_count = df[col].isnull().sum()
                completeness = ((len(df) - null_count) / len(df)) * 100
                quality_metrics["completeness"][col] = {
                    "percentage": round(completeness, 2),
                    "null_count": int(null_count),
                    "total_count": len(df)
                }
                
                # Uniqueness check
                unique_count = df[col].nunique()
                uniqueness = (unique_count / len(df)) * 100
                quality_metrics["uniqueness"][col] = {
                    "percentage": round(uniqueness, 2),
                    "unique_count": int(unique_count),
                    "duplicate_count": len(df) - unique_count
                }
                
                # Basic validity checks
                if df[col].dtype in ['int64', 'float64']:
                    # Numeric validity
                    valid_numbers = df[col].dropna().apply(lambda x: isinstance(x, (int, float))).sum()
                    validity = (valid_numbers / len(df.dropna())) * 100 if len(df.dropna()) > 0 else 0
                else:
                    # String validity (non-empty strings)
                    valid_strings = df[col].dropna().apply(lambda x: len(str(x).strip()) > 0).sum()
                    validity = (valid_strings / len(df.dropna())) * 100 if len(df.dropna()) > 0 else 0
                    
                quality_metrics["validity"][col] = {
                    "percentage": round(validity, 2),
                    "data_type": str(df[col].dtype)
                }
            
            # Overall quality score
            avg_completeness = sum(m["percentage"] for m in quality_metrics["completeness"].values()) / len(quality_metrics["completeness"])
            avg_validity = sum(m["percentage"] for m in quality_metrics["validity"].values()) / len(quality_metrics["validity"])
            overall_score = (avg_completeness + avg_validity) / 2
            
            return {
                "operation": "data_quality_check",
                "overall_score": round(overall_score, 2),
                "metrics": quality_metrics,
                "recommendations": self._generate_quality_recommendations(quality_metrics),
                "success": True
            }
            
        except Exception as e:
            logger.error("Data quality check operation failed", error=str(e))
            raise
    
    async def _lineage_discovery_operation(
        self,
        file_data: Dict[str, Any],
        target_entity_type: str,
        options: Dict[str, Any],
        progress_callback: Callable
    ) -> Dict[str, Any]:
        """Lineage discovery operation."""
        try:
            await progress_callback(50)
            
            # Placeholder for lineage discovery logic
            # This would analyze the file structure and content to discover potential lineage relationships
            
            discovered_lineages = []
            
            if file_data["format"] in ["csv", "excel"]:
                df = file_data["data"]
                columns = df.columns.tolist()
                
                # Analyze column relationships (simplified)
                for col in columns:
                    if col.lower().endswith('_id') or col.lower().endswith('_key'):
                        discovered_lineages.append({
                            "source_column": col,
                            "relationship_type": "identifier",
                            "confidence": 0.8
                        })
            
            await progress_callback(100)
            
            return {
                "operation": "lineage_discovery",
                "discovered_lineages": discovered_lineages,
                "total_discovered": len(discovered_lineages),
                "success": True
            }
            
        except Exception as e:
            logger.error("Lineage discovery operation failed", error=str(e))
            raise
    
    async def _metadata_extraction_operation(
        self,
        file_data: Dict[str, Any],
        target_entity_type: str,
        options: Dict[str, Any],
        progress_callback: Callable
    ) -> Dict[str, Any]:
        """Metadata extraction operation."""
        try:
            await progress_callback(25)
            
            metadata = {
                "file_metadata": {
                    "format": file_data["format"],
                    "size": file_data.get("rows", file_data.get("lines", file_data.get("size", 0)))
                },
                "schema_metadata": {},
                "statistical_metadata": {}
            }
            
            if file_data["format"] in ["csv", "excel"]:
                df = file_data["data"]
                
                # Schema metadata
                metadata["schema_metadata"] = {
                    "columns": len(df.columns),
                    "rows": len(df),
                    "column_info": []
                }
                
                await progress_callback(50)
                
                for col in df.columns:
                    col_info = {
                        "name": col,
                        "data_type": str(df[col].dtype),
                        "null_count": int(df[col].isnull().sum()),
                        "unique_count": int(df[col].nunique())
                    }
                    
                    if df[col].dtype in ['int64', 'float64']:
                        col_info.update({
                            "min_value": float(df[col].min()) if pd.notna(df[col].min()) else None,
                            "max_value": float(df[col].max()) if pd.notna(df[col].max()) else None,
                            "mean_value": float(df[col].mean()) if pd.notna(df[col].mean()) else None
                        })
                    
                    metadata["schema_metadata"]["column_info"].append(col_info)
                
                await progress_callback(75)
                
                # Statistical metadata
                metadata["statistical_metadata"] = {
                    "total_cells": len(df) * len(df.columns),
                    "null_cells": int(df.isnull().sum().sum()),
                    "completeness_percentage": round(((len(df) * len(df.columns) - int(df.isnull().sum().sum())) / (len(df) * len(df.columns))) * 100, 2)
                }
            
            await progress_callback(100)
            
            return {
                "operation": "metadata_extraction",
                "metadata": metadata,
                "success": True
            }
            
        except Exception as e:
            logger.error("Metadata extraction operation failed", error=str(e))
            raise
    
    async def _compliance_scan_operation(
        self,
        file_data: Dict[str, Any],
        target_entity_type: str,
        options: Dict[str, Any],
        progress_callback: Callable
    ) -> Dict[str, Any]:
        """Compliance scan operation."""
        try:
            await progress_callback(25)
            
            compliance_results = {
                "pii_detection": [],
                "sensitive_data": [],
                "policy_violations": [],
                "compliance_score": 0
            }
            
            if file_data["format"] in ["csv", "excel"]:
                df = file_data["data"]
                
                # PII detection patterns
                pii_patterns = {
                    "email": r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
                    "phone": r'\b\d{3}-\d{3}-\d{4}\b|\b\(\d{3}\)\s*\d{3}-\d{4}\b',
                    "ssn": r'\b\d{3}-\d{2}-\d{4}\b',
                    "credit_card": r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b'
                }
                
                await progress_callback(50)
                
                for col in df.columns:
                    col_data = df[col].astype(str)
                    
                    # Check for PII patterns
                    for pii_type, pattern in pii_patterns.items():
                        matches = col_data.str.contains(pattern, regex=True, na=False).sum()
                        
                        if matches > 0:
                            compliance_results["pii_detection"].append({
                                "column": col,
                                "pii_type": pii_type,
                                "matches": int(matches),
                                "percentage": round((matches / len(df)) * 100, 2)
                            })
                    
                    # Check for sensitive column names
                    sensitive_keywords = ['password', 'secret', 'key', 'token', 'ssn', 'social']
                    if any(keyword in col.lower() for keyword in sensitive_keywords):
                        compliance_results["sensitive_data"].append({
                            "column": col,
                            "reason": "Sensitive column name detected"  
                        })
                
                await progress_callback(75)
                
                # Calculate compliance score
                total_issues = len(compliance_results["pii_detection"]) + len(compliance_results["sensitive_data"])
                total_columns = len(df.columns)
                compliance_score = max(0, 100 - (total_issues / total_columns * 50))
                compliance_results["compliance_score"] = round(compliance_score, 2)
            
            await progress_callback(100)
            
            return {
                "operation": "compliance_scan",
                "results": compliance_results,
                "success": True
            }
            
        except Exception as e:
            logger.error("Compliance scan operation failed", error=str(e))
            raise
    
    async def _data_profiling_operation(
        self,
        file_data: Dict[str, Any],
        target_entity_type: str,
        options: Dict[str, Any],
        progress_callback: Callable
    ) -> Dict[str, Any]:
        """Data profiling operation."""
        try:
            if file_data["format"] not in ["csv", "excel"]:
                raise ValueError("Data profiling only supports CSV and Excel files")
            
            df = file_data["data"]
            total_columns = len(df.columns)
            
            profile_results = {
                "dataset_profile": {
                    "total_rows": len(df),
                    "total_columns": len(df.columns),
                    "memory_usage": df.memory_usage(deep=True).sum()
                },
                "column_profiles": []
            }
            
            for index, col in enumerate(df.columns):
                await progress_callback(int((index / total_columns) * 100))
                
                col_profile = {
                    "column_name": col,
                    "data_type": str(df[col].dtype),
                    "null_count": int(df[col].isnull().sum()),
                    "null_percentage": round((df[col].isnull().sum() / len(df)) * 100, 2),
                    "unique_count": int(df[col].nunique()),
                    "unique_percentage": round((df[col].nunique() / len(df)) * 100, 2)
                }
                
                # Numeric column profiling
                if df[col].dtype in ['int64', 'float64']:
                    col_profile.update({
                        "min_value": float(df[col].min()) if pd.notna(df[col].min()) else None,
                        "max_value": float(df[col].max()) if pd.notna(df[col].max()) else None,
                        "mean_value": float(df[col].mean()) if pd.notna(df[col].mean()) else None,
                        "median_value": float(df[col].median()) if pd.notna(df[col].median()) else None,
                        "std_deviation": float(df[col].std()) if pd.notna(df[col].std()) else None
                    })
                
                # String column profiling
                elif df[col].dtype == 'object':
                    col_profile.update({
                        "avg_length": round(df[col].astype(str).str.len().mean(), 2) if len(df[col].dropna()) > 0 else 0,
                        "min_length": int(df[col].astype(str).str.len().min()) if len(df[col].dropna()) > 0 else 0,
                        "max_length": int(df[col].astype(str).str.len().max()) if len(df[col].dropna()) > 0 else 0,
                        "most_common": df[col].value_counts().head(5).to_dict() if len(df[col].dropna()) > 0 else {}
                    })
                
                profile_results["column_profiles"].append(col_profile)
            
            return {
                "operation": "data_profiling",
                "profile": profile_results,
                "success": True
            }
            
        except Exception as e:
            logger.error("Data profiling operation failed", error=str(e))
            raise
    
    # Helper methods
    async def _update_job_status(
        self, 
        job_id: str, 
        status: str, 
        progress: int = None,
        result: Dict[str, Any] = None,
        error: str = None
    ):
        """Update job status in database."""
        try:
            async with get_db_session() as session:
                update_data = {"status": status}
                
                if progress is not None:
                    update_data["progress"] = progress
                
                if result is not None:
                    update_data["result"] = result
                
                if error is not None:
                    update_data["error"] = error
                
                if status in ["completed", "failed"]:
                    update_data["completed_at"] = datetime.utcnow()
                
                await session.execute(
                    update(ProcessingJob)
                    .where(ProcessingJob.job_id == job_id)
                    .values(**update_data)
                )
                await session.commit()
                
        except Exception as e:
            logger.error("Failed to update job status", error=str(e), job_id=job_id)
    
    async def _update_job_progress(self, job_id: str, progress: int):
        """Update job progress."""
        await self._update_job_status(job_id, "processing", progress)
    
    def _generate_quality_recommendations(self, quality_metrics: Dict[str, Any]) -> List[str]:
        """Generate data quality recommendations."""
        recommendations = []
        
        # Completeness recommendations
        for col, metrics in quality_metrics["completeness"].items():
            if metrics["percentage"] < 80:
                recommendations.append(f"Column '{col}' has low completeness ({metrics['percentage']}%). Consider data validation rules.")
        
        # Uniqueness recommendations
        for col, metrics in quality_metrics["uniqueness"].items():
            if metrics["percentage"] < 50 and metrics["duplicate_count"] > 0:
                recommendations.append(f"Column '{col}' has many duplicates. Consider data deduplication.")
        
        # Validity recommendations
        for col, metrics in quality_metrics["validity"].items():
            if metrics["percentage"] < 90:
                recommendations.append(f"Column '{col}' has invalid data. Consider data type validation.")
        
        return recommendations
