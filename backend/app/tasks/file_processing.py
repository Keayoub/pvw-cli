"""
Celery tasks for file processing operations.
Handles background processing of uploaded files with various operations.
"""
import asyncio
from typing import Dict, Any, Optional
from celery import current_task
from celery.exceptions import Retry
import structlog

from app.core.celery_app import celery_app, BaseTask
from app.core.logging import get_logger
from app.services.file_processing_service import FileProcessingService
from app.database.connection import get_db_session
from app.database.models import ProcessingJob, UploadedFile

logger = get_logger(__name__)

class FileProcessingTask(BaseTask):
    """Base class for file processing tasks."""
    
    def __init__(self):
        self.file_service = FileProcessingService()
    
    def update_progress(self, job_id: str, progress: int, message: str = None):
        """Update task progress."""
        current_task.update_state(
            state="PROGRESS",
            meta={
                "job_id": job_id,
                "progress": progress,
                "message": message or f"Processing... {progress}%"
            }
        )

@celery_app.task(bind=True, base=FileProcessingTask, name="process_file")
def process_file_task(self, file_id: str, job_id: str):
    """
    Process a file with the specified operation.
    This is the main task that handles file processing.
    """
    try:
        logger.info("Starting file processing task", job_id=job_id, file_id=file_id)
        
        # Update task state
        self.update_progress(job_id, 0, "Initializing file processing...")
        
        # Create event loop for async operations
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            # Run the async file processing
            result = loop.run_until_complete(
                self.file_service.process_file_background(file_id, job_id)
            )
            
            logger.info("File processing completed", job_id=job_id, file_id=file_id)
            return {"job_id": job_id, "file_id": file_id, "status": "completed", "result": result}
            
        finally:
            loop.close()
            
    except Exception as exc:
        logger.error("File processing task failed", job_id=job_id, file_id=file_id, error=str(exc))
        
        # Update job status to failed
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(
                self.file_service._update_job_status(job_id, "failed", error=str(exc))
            )
        finally:
            loop.close()
        
        # Retry logic
        if self.request.retries < 3:
            logger.info("Retrying file processing task", job_id=job_id, retry_count=self.request.retries)
            raise self.retry(countdown=60 * (self.request.retries + 1), exc=exc)
        
        raise exc

@celery_app.task(bind=True, base=FileProcessingTask, name="process_large_file")
def process_large_file_task(self, file_id: str, job_id: str, chunk_size: int = 1000):
    """
    Process large files in chunks to avoid memory issues.
    """
    try:
        logger.info("Starting large file processing task", job_id=job_id, file_id=file_id)
        
        self.update_progress(job_id, 0, "Initializing large file processing...")
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            # Custom processing for large files with chunking
            result = loop.run_until_complete(
                process_large_file_async(self, file_id, job_id, chunk_size)
            )
            
            logger.info("Large file processing completed", job_id=job_id, file_id=file_id)
            return {"job_id": job_id, "file_id": file_id, "status": "completed", "result": result}
            
        finally:
            loop.close()
            
    except Exception as exc:
        logger.error("Large file processing task failed", job_id=job_id, file_id=file_id, error=str(exc))
        
        # Update job status
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(
                self.file_service._update_job_status(job_id, "failed", error=str(exc))
            )
        finally:
            loop.close()
        
        raise exc

@celery_app.task(bind=True, base=FileProcessingTask, name="batch_entity_import")
def batch_entity_import_task(self, file_id: str, job_id: str, batch_size: int = 100):
    """
    Import entities in batches for better performance.
    """
    try:
        logger.info("Starting batch entity import task", job_id=job_id, file_id=file_id)
        
        self.update_progress(job_id, 0, "Starting batch entity import...")
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            result = loop.run_until_complete(
                batch_entity_import_async(self, file_id, job_id, batch_size)
            )
            
            logger.info("Batch entity import completed", job_id=job_id, file_id=file_id)
            return {"job_id": job_id, "file_id": file_id, "status": "completed", "result": result}
            
        finally:
            loop.close()
            
    except Exception as exc:
        logger.error("Batch entity import task failed", job_id=job_id, file_id=file_id, error=str(exc))
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(
                self.file_service._update_job_status(job_id, "failed", error=str(exc))
            )
        finally:
            loop.close()
        
        raise exc

@celery_app.task(bind=True, base=FileProcessingTask, name="data_quality_analysis")
def data_quality_analysis_task(self, file_id: str, job_id: str):
    """
    Perform comprehensive data quality analysis.
    """
    try:
        logger.info("Starting data quality analysis task", job_id=job_id, file_id=file_id)
        
        self.update_progress(job_id, 0, "Starting data quality analysis...")
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            result = loop.run_until_complete(
                data_quality_analysis_async(self, file_id, job_id)
            )
            
            logger.info("Data quality analysis completed", job_id=job_id, file_id=file_id)
            return {"job_id": job_id, "file_id": file_id, "status": "completed", "result": result}
            
        finally:
            loop.close()
            
    except Exception as exc:
        logger.error("Data quality analysis task failed", job_id=job_id, file_id=file_id, error=str(exc))
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(
                self.file_service._update_job_status(job_id, "failed", error=str(exc))
            )
        finally:
            loop.close()
        
        raise exc

@celery_app.task(bind=True, base=FileProcessingTask, name="compliance_scan")
def compliance_scan_task(self, file_id: str, job_id: str):
    """
    Perform compliance scanning on uploaded files.
    """
    try:
        logger.info("Starting compliance scan task", job_id=job_id, file_id=file_id)
        
        self.update_progress(job_id, 0, "Starting compliance scan...")
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            result = loop.run_until_complete(
                compliance_scan_async(self, file_id, job_id)
            )
            
            logger.info("Compliance scan completed", job_id=job_id, file_id=file_id)
            return {"job_id": job_id, "file_id": file_id, "status": "completed", "result": result}
            
        finally:
            loop.close()
            
    except Exception as exc:
        logger.error("Compliance scan task failed", job_id=job_id, file_id=file_id, error=str(exc))
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(
                self.file_service._update_job_status(job_id, "failed", error=str(exc))
            )
        finally:
            loop.close()
        
        raise exc

# Async helper functions
async def process_large_file_async(task_instance, file_id: str, job_id: str, chunk_size: int):
    """Process large files asynchronously with progress updates."""
    try:
        # Get file info
        async with get_db_session() as session:
            from sqlalchemy import select
            result = await session.execute(
                select(UploadedFile).where(UploadedFile.file_id == file_id)
            )
            file_record = result.scalar_one_or_none()
            
            if not file_record:
                raise ValueError("File not found")
        
        # Update progress
        task_instance.update_progress(job_id, 10, "Loading file data...")
        
        # Process file in chunks
        file_service = task_instance.file_service
        
        # Get file data
        from pathlib import Path
        file_path = Path(file_record.file_path)
        file_ext = file_path.suffix.lower()
        
        if file_ext == '.csv':
            import pandas as pd
            
            # Read file in chunks
            chunk_iter = pd.read_csv(file_path, chunksize=chunk_size)
            total_chunks = sum(1 for _ in pd.read_csv(file_path, chunksize=chunk_size))
            
            processed_chunks = 0
            results = []
            
            for chunk in chunk_iter:
                # Process chunk
                chunk_result = await process_chunk_async(chunk, file_service)
                results.append(chunk_result)
                
                processed_chunks += 1
                progress = int((processed_chunks / total_chunks) * 90) + 10
                task_instance.update_progress(job_id, progress, f"Processed {processed_chunks}/{total_chunks} chunks")
            
            # Combine results
            final_result = combine_chunk_results(results)
            
        else:
            # For non-CSV files, use regular processing
            file_data = await file_service.supported_formats[file_ext](file_path)
            final_result = await file_service.supported_operations["metadata_extraction"](
                file_data, None, {}, lambda p: task_instance.update_progress(job_id, p + 10)
            )
        
        task_instance.update_progress(job_id, 100, "Processing completed")
        return final_result
        
    except Exception as e:
        logger.error("Large file processing failed", error=str(e), job_id=job_id)
        raise

async def batch_entity_import_async(task_instance, file_id: str, job_id: str, batch_size: int):
    """Import entities in batches asynchronously."""
    try:
        file_service = task_instance.file_service
        
        # Get file data
        async with get_db_session() as session:
            from sqlalchemy import select
            result = await session.execute(
                select(UploadedFile).where(UploadedFile.file_id == file_id)
            )
            file_record = result.scalar_one_or_none()
            
            if not file_record:
                raise ValueError("File not found")
        
        task_instance.update_progress(job_id, 5, "Loading file for batch import...")
        
        from pathlib import Path
        file_path = Path(file_record.file_path)
        file_ext = file_path.suffix.lower()
        
        if file_ext not in ['.csv', '.xlsx', '.xls']:
            raise ValueError("Batch entity import only supports CSV and Excel files")
        
        # Load file data
        file_data = await file_service.supported_formats[file_ext](file_path)
        df = file_data["data"]
        
        task_instance.update_progress(job_id, 10, "Processing entities in batches...")
        
        # Process in batches
        total_rows = len(df)
        processed_rows = 0
        batch_results = []
        
        for start_idx in range(0, total_rows, batch_size):
            end_idx = min(start_idx + batch_size, total_rows)
            batch_df = df.iloc[start_idx:end_idx]
            
            # Process batch
            batch_data = {**file_data, "data": batch_df}
            batch_result = await file_service._import_entities_operation(
                batch_data, "DataSet", {},
                lambda p: None  # Don't update progress for individual batches
            )
            
            batch_results.append(batch_result)
            processed_rows += len(batch_df)
            
            progress = int((processed_rows / total_rows) * 85) + 10
            task_instance.update_progress(
                job_id, progress, 
                f"Processed {processed_rows}/{total_rows} entities"
            )
        
        # Combine batch results
        final_result = {
            "operation": "batch_entity_import",
            "total_processed": total_rows,
            "entities_created": sum(r["entities_created"] for r in batch_results),
            "errors": [error for r in batch_results for error in r["errors"]],
            "batches_processed": len(batch_results),
            "success": True
        }
        
        task_instance.update_progress(job_id, 100, "Batch import completed")
        return final_result
        
    except Exception as e:
        logger.error("Batch entity import failed", error=str(e), job_id=job_id)
        raise

async def data_quality_analysis_async(task_instance, file_id: str, job_id: str):
    """Perform data quality analysis asynchronously."""
    try:
        file_service = task_instance.file_service
        
        # Get file data
        async with get_db_session() as session:
            from sqlalchemy import select
            result = await session.execute(
                select(UploadedFile).where(UploadedFile.file_id == file_id)
            )
            file_record = result.scalar_one_or_none()
            
            if not file_record:
                raise ValueError("File not found")
        
        task_instance.update_progress(job_id, 10, "Starting comprehensive data quality analysis...")
        
        from pathlib import Path
        file_path = Path(file_record.file_path)
        file_ext = file_path.suffix.lower()
        
        # Load file data
        file_data = await file_service.supported_formats[file_ext](file_path)
        
        # Perform multiple quality checks
        quality_result = await file_service._data_quality_check_operation(
            file_data, None, {},
            lambda p: task_instance.update_progress(job_id, 10 + int(p * 0.4))
        )
        
        task_instance.update_progress(job_id, 50, "Performing data profiling...")
        
        # Add profiling if supported
        if file_ext in ['.csv', '.xlsx', '.xls']:
            profiling_result = await file_service._data_profiling_operation(
                file_data, None, {},
                lambda p: task_instance.update_progress(job_id, 50 + int(p * 0.4))
            )
            
            # Combine results
            combined_result = {
                "operation": "comprehensive_data_quality_analysis",
                "quality_check": quality_result,
                "data_profiling": profiling_result,
                "success": True
            }
        else:
            combined_result = quality_result
        
        task_instance.update_progress(job_id, 100, "Data quality analysis completed")
        return combined_result
        
    except Exception as e:
        logger.error("Data quality analysis failed", error=str(e), job_id=job_id)
        raise

async def compliance_scan_async(task_instance, file_id: str, job_id: str):
    """Perform compliance scanning asynchronously."""
    try:
        file_service = task_instance.file_service
        
        # Get file data
        async with get_db_session() as session:
            from sqlalchemy import select
            result = await session.execute(
                select(UploadedFile).where(UploadedFile.file_id == file_id)
            )
            file_record = result.scalar_one_or_none()
            
            if not file_record:
                raise ValueError("File not found")
        
        task_instance.update_progress(job_id, 10, "Starting compliance scan...")
        
        from pathlib import Path
        file_path = Path(file_record.file_path)
        file_ext = file_path.suffix.lower()
        
        # Load file data
        file_data = await file_service.supported_formats[file_ext](file_path)
        
        # Perform compliance scan
        compliance_result = await file_service._compliance_scan_operation(
            file_data, None, {},
            lambda p: task_instance.update_progress(job_id, 10 + int(p * 0.8))
        )
        
        task_instance.update_progress(job_id, 100, "Compliance scan completed")
        return compliance_result
        
    except Exception as e:
        logger.error("Compliance scan failed", error=str(e), job_id=job_id)
        raise

# Helper functions
async def process_chunk_async(chunk_df, file_service):
    """Process a data chunk asynchronously."""
    try:
        # Convert chunk to file_data format
        file_data = {
            "format": "csv",
            "columns": chunk_df.columns.tolist(),
            "rows": len(chunk_df),
            "data": chunk_df
        }
        
        # Process chunk (example: metadata extraction)
        result = await file_service._metadata_extraction_operation(
            file_data, None, {}, lambda p: None
        )
        
        return result
        
    except Exception as e:
        logger.error("Chunk processing failed", error=str(e))
        raise

def combine_chunk_results(results):
    """Combine results from multiple chunks."""
    if not results:
        return {"operation": "large_file_processing", "success": False, "error": "No results"}
    
    # Combine metadata from all chunks
    combined_metadata = {
        "operation": "large_file_processing",
        "total_chunks": len(results),
        "combined_metadata": {
            "total_rows": sum(r["metadata"]["file_metadata"]["size"] for r in results),
            "total_columns": results[0]["metadata"]["schema_metadata"]["columns"],
            "chunks_processed": len(results)
        },
        "success": True
    }
    
    return combined_metadata
