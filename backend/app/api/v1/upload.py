"""
File Upload API endpoints for processing data files.
Supports CSV, JSON, and Excel files for data import operations.
"""
import os
import uuid
import mimetypes
from typing import List, Optional, Dict, Any
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import structlog
import pandas as pd
import aiofiles

from app.core.config import settings
from app.core.logging import get_logger
from app.middleware.auth import get_current_user
from app.services.file_processing_service import FileProcessingService

logger = get_logger(__name__)
router = APIRouter()

class FileUploadResponse(BaseModel):
    """Response model for file upload."""
    file_id: str
    filename: str
    original_filename: str
    size: int
    mime_type: str
    upload_time: str
    status: str
    processing_job_id: Optional[str] = None

class FileListResponse(BaseModel):
    """Response model for file listing."""
    files: List[FileUploadResponse]
    total_count: int
    page: int
    page_size: int

class FileProcessingRequest(BaseModel):
    """Request model for file processing."""
    operation_type: str  # 'import_entities', 'bulk_classification', 'data_quality_check'
    target_entity_type: Optional[str] = None
    options: Optional[Dict[str, Any]] = {}

# Allowed file types and their MIME types
ALLOWED_EXTENSIONS = {
    '.csv': 'text/csv',
    '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    '.xls': 'application/vnd.ms-excel',
    '.json': 'application/json',
    '.txt': 'text/plain'
}

# Maximum file sizes (in bytes)
MAX_FILE_SIZES = {
    '.csv': 100 * 1024 * 1024,  # 100MB
    '.xlsx': 50 * 1024 * 1024,   # 50MB
    '.xls': 50 * 1024 * 1024,    # 50MB
    '.json': 25 * 1024 * 1024,   # 25MB
    '.txt': 10 * 1024 * 1024     # 10MB
}

def validate_file(file: UploadFile) -> tuple[bool, str]:
    """Validate uploaded file."""
    if not file.filename:
        return False, "Filename is required"
    
    # Check file extension
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        return False, f"File type {file_ext} not supported. Allowed types: {', '.join(ALLOWED_EXTENSIONS.keys())}"
    
    # Check file size
    if file.size and file.size > MAX_FILE_SIZES.get(file_ext, settings.MAX_UPLOAD_SIZE):
        max_size_mb = MAX_FILE_SIZES.get(file_ext, settings.MAX_UPLOAD_SIZE) / (1024 * 1024)
        return False, f"File size exceeds limit of {max_size_mb:.1f}MB"
    
    return True, ""

async def save_uploaded_file(file: UploadFile, file_id: str) -> Path:
    """Save uploaded file to disk."""
    file_ext = Path(file.filename).suffix.lower()
    file_path = settings.UPLOAD_DIR / f"{file_id}{file_ext}"
    
    # Ensure upload directory exists
    settings.UPLOAD_DIR.mkdir(exist_ok=True)
    
    # Save file
    async with aiofiles.open(file_path, 'wb') as f:
        content = await file.read()
        await f.write(content)
    
    return file_path

@router.post("/", response_model=FileUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_file(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    auto_process: bool = Form(False),
    operation_type: Optional[str] = Form(None),
    target_entity_type: Optional[str] = Form(None),
    current_user: Dict[str, Any] = Depends(get_current_user),
    file_service: FileProcessingService = Depends()
):
    """
    Upload a file for processing.
    
    Supports CSV, Excel, JSON, and text files for data import operations.
    """
    try:
        # Validate file
        is_valid, error_message = validate_file(file)
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_message
            )
        
        # Generate unique file ID
        file_id = str(uuid.uuid4())
        
        # Save file
        file_path = await save_uploaded_file(file, file_id)
        
        # Get file info
        file_ext = Path(file.filename).suffix.lower()
        mime_type = ALLOWED_EXTENSIONS.get(file_ext, 'application/octet-stream')
        file_size = file_path.stat().st_size
        
        # Create file record
        file_record = await file_service.create_file_record(
            file_id=file_id,
            filename=file_path.name,
            original_filename=file.filename,
            file_path=str(file_path),
            size=file_size,
            mime_type=mime_type,
            uploaded_by=current_user["id"]
        )
        
        processing_job_id = None
        
        # Auto-process if requested
        if auto_process and operation_type:
            processing_job_id = await file_service.queue_file_processing(
                file_id=file_id,
                operation_type=operation_type,
                target_entity_type=target_entity_type,
                user_id=current_user["id"]
            )
            
            # Start background processing
            background_tasks.add_task(
                file_service.process_file_background,
                file_id,
                processing_job_id
            )
        
        logger.info(
            "File uploaded successfully",
            file_id=file_id,
            filename=file.filename,
            size=file_size,
            user=current_user["id"],
            auto_process=auto_process
        )
        
        return FileUploadResponse(
            file_id=file_id,
            filename=file_path.name,
            original_filename=file.filename,
            size=file_size,
            mime_type=mime_type,
            upload_time=file_record["upload_time"],
            status="uploaded" if not auto_process else "processing",
            processing_job_id=processing_job_id
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to upload file", error=str(e), filename=file.filename)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload file: {str(e)}"
        )

@router.get("/", response_model=FileListResponse)
async def list_files(
    page: int = 1,
    page_size: int = 25,
    status_filter: Optional[str] = None,
    current_user: Dict[str, Any] = Depends(get_current_user),
    file_service: FileProcessingService = Depends()
):
    """Get list of uploaded files."""
    try:
        files_data = await file_service.get_user_files(
            user_id=current_user["id"],
            page=page,
            page_size=page_size,
            status_filter=status_filter
        )
        
        return FileListResponse(
            files=[
                FileUploadResponse(
                    file_id=f["file_id"],
                    filename=f["filename"],
                    original_filename=f["original_filename"],
                    size=f["size"],
                    mime_type=f["mime_type"],
                    upload_time=f["upload_time"],
                    status=f["status"],
                    processing_job_id=f.get("processing_job_id")
                )
                for f in files_data["files"]
            ],
            total_count=files_data["total_count"],
            page=page,
            page_size=page_size
        )
        
    except Exception as e:
        logger.error("Failed to list files", error=str(e), user=current_user["id"])
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list files: {str(e)}"
        )

@router.get("/{file_id}")
async def get_file_info(
    file_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
    file_service: FileProcessingService = Depends()
):
    """Get information about a specific file."""
    try:
        file_info = await file_service.get_file_info(file_id, current_user["id"])
        
        if not file_info:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File not found"
            )
        
        return file_info
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get file info", error=str(e), file_id=file_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get file info: {str(e)}"
        )

@router.post("/{file_id}/process")
async def process_file(
    file_id: str,
    processing_request: FileProcessingRequest,
    background_tasks: BackgroundTasks,
    current_user: Dict[str, Any] = Depends(get_current_user),
    file_service: FileProcessingService = Depends()
):
    """Process an uploaded file."""
    try:
        # Verify file exists and belongs to user
        file_info = await file_service.get_file_info(file_id, current_user["id"])
        if not file_info:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File not found"
            )
        
        # Queue processing job
        job_id = await file_service.queue_file_processing(
            file_id=file_id,
            operation_type=processing_request.operation_type,
            target_entity_type=processing_request.target_entity_type,
            options=processing_request.options,
            user_id=current_user["id"]
        )
        
        # Start background processing
        background_tasks.add_task(
            file_service.process_file_background,
            file_id,
            job_id
        )
        
        logger.info(
            "File processing started",
            file_id=file_id,
            job_id=job_id,
            operation_type=processing_request.operation_type,
            user=current_user["id"]
        )
        
        return {
            "message": "File processing started",
            "job_id": job_id,
            "file_id": file_id,
            "operation_type": processing_request.operation_type
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to process file", error=str(e), file_id=file_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process file: {str(e)}"
        )

@router.get("/{file_id}/preview")
async def preview_file(
    file_id: str,
    rows: int = 10,
    current_user: Dict[str, Any] = Depends(get_current_user),
    file_service: FileProcessingService = Depends()
):
    """Preview the contents of an uploaded file."""
    try:
        preview_data = await file_service.preview_file(
            file_id=file_id,
            user_id=current_user["id"],
            rows=rows
        )
        
        return preview_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to preview file", error=str(e), file_id=file_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to preview file: {str(e)}"
        )

@router.delete("/{file_id}")
async def delete_file(
    file_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
    file_service: FileProcessingService = Depends()
):
    """Delete an uploaded file."""
    try:
        success = await file_service.delete_file(file_id, current_user["id"])
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File not found"
            )
        
        logger.info("File deleted", file_id=file_id, user=current_user["id"])
        
        return {"message": "File deleted successfully", "file_id": file_id}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to delete file", error=str(e), file_id=file_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete file: {str(e)}"
        )

@router.get("/{file_id}/download")
async def download_file(
    file_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
    file_service: FileProcessingService = Depends()
):
    """Download an uploaded file."""
    try:
        file_info = await file_service.get_file_info(file_id, current_user["id"])
        
        if not file_info:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File not found"
            )
        
        file_path = Path(file_info["file_path"])
        
        if not file_path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File not found on disk"
            )
        
        # Return file for download
        from fastapi.responses import FileResponse
        
        return FileResponse(
            path=str(file_path),
            filename=file_info["original_filename"],
            media_type=file_info["mime_type"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to download file", error=str(e), file_id=file_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to download file: {str(e)}"
        )

@router.get("/{file_id}/status")
async def get_processing_status(
    file_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
    file_service: FileProcessingService = Depends()
):
    """Get the processing status of a file."""
    try:
        status_info = await file_service.get_processing_status(
            file_id=file_id,
            user_id=current_user["id"]
        )
        
        if not status_info:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File or processing job not found"
            )
        
        return status_info
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get processing status", error=str(e), file_id=file_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get processing status: {str(e)}"
        )
