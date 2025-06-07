from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
import structlog
from datetime import datetime

from app.core.logging import get_logger
from app.models.scan import Scan, ScanCreateRequest, ScanResponse, ScanStatus
from app.services.scanning_service import ScanningService
from app.core.websocket import WebSocketManager

logger = get_logger(__name__)
router = APIRouter()

class ScanCreateRequestAPI(BaseModel):
    name: str
    data_source_type: str
    connection_details: Dict[str, Any]
    scan_rule_set: Optional[str] = None
    schedule: Optional[Dict[str, Any]] = None
    
class ScanUpdateRequest(BaseModel):
    name: Optional[str] = None
    connection_details: Optional[Dict[str, Any]] = None
    scan_rule_set: Optional[str] = None
    schedule: Optional[Dict[str, Any]] = None

class ScanListResponse(BaseModel):
    scans: List[ScanResponse]
    total_count: int
    page: int
    page_size: int

# Global WebSocket manager instance
websocket_manager = WebSocketManager()

@router.get("/", response_model=ScanListResponse)
async def get_scans(
    page: int = 1,
    page_size: int = 25,
    status: Optional[ScanStatus] = None,
    scanning_service: ScanningService = Depends()
):
    """Get list of scans with pagination"""
    try:
        result = await scanning_service.get_scans(
            page=page,
            page_size=page_size,
            status_filter=status
        )
        
        return ScanListResponse(
            scans=result["scans"],
            total_count=result["total_count"],
            page=page,
            page_size=page_size
        )
        
    except Exception as e:
        logger.error("Failed to get scans", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get scans: {str(e)}"
        )

@router.get("/{scan_id}", response_model=ScanResponse)
async def get_scan(
    scan_id: str,
    scanning_service: ScanningService = Depends()
):
    """Get scan by ID"""
    try:
        scan = await scanning_service.get_scan(scan_id)
        if not scan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Scan {scan_id} not found"
            )
        return scan
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get scan", scan_id=scan_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get scan: {str(e)}"
        )

@router.post("/", response_model=ScanResponse, status_code=status.HTTP_201_CREATED)
async def create_scan(
    scan_request: ScanCreateRequestAPI,
    scanning_service: ScanningService = Depends()
):
    """Create a new scan"""
    try:
        create_request = ScanCreateRequest(
            name=scan_request.name,
            data_source_type=scan_request.data_source_type,
            connection_details=scan_request.connection_details,
            scan_rule_set=scan_request.scan_rule_set,
            schedule=scan_request.schedule
        )
        
        scan = await scanning_service.create_scan(create_request)
        
        logger.info("Scan created", scan_id=scan.id, name=scan.name)
        
        # Notify WebSocket subscribers
        await websocket_manager.broadcast_to_topic("scans", {
            "event": "scan_created",
            "scan": scan.dict()
        })
        
        return scan
        
    except Exception as e:
        logger.error("Failed to create scan", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create scan: {str(e)}"
        )

@router.put("/{scan_id}", response_model=ScanResponse)
async def update_scan(
    scan_id: str,
    scan_request: ScanUpdateRequest,
    scanning_service: ScanningService = Depends()
):
    """Update an existing scan"""
    try:
        scan = await scanning_service.update_scan(
            scan_id=scan_id,
            name=scan_request.name,
            connection_details=scan_request.connection_details,
            scan_rule_set=scan_request.scan_rule_set,
            schedule=scan_request.schedule
        )
        
        if not scan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Scan {scan_id} not found"
            )
            
        logger.info("Scan updated", scan_id=scan_id)
        
        # Notify WebSocket subscribers
        await websocket_manager.broadcast_to_topic("scans", {
            "event": "scan_updated",
            "scan": scan.dict()
        })
        
        return scan
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to update scan", scan_id=scan_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update scan: {str(e)}"
        )

@router.delete("/{scan_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_scan(
    scan_id: str,
    scanning_service: ScanningService = Depends()
):
    """Delete a scan"""
    try:
        success = await scanning_service.delete_scan(scan_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Scan {scan_id} not found"
            )
            
        logger.info("Scan deleted", scan_id=scan_id)
        
        # Notify WebSocket subscribers
        await websocket_manager.broadcast_to_topic("scans", {
            "event": "scan_deleted",
            "scan_id": scan_id
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to delete scan", scan_id=scan_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete scan: {str(e)}"
        )

@router.post("/{scan_id}/start")
async def start_scan(
    scan_id: str,
    background_tasks: BackgroundTasks,
    scanning_service: ScanningService = Depends()
):
    """Start a scan"""
    try:
        # Start scan in background
        background_tasks.add_task(_start_scan_background, scan_id, scanning_service)
        
        logger.info("Scan start requested", scan_id=scan_id)
        return {"message": "Scan start initiated", "scan_id": scan_id}
        
    except Exception as e:
        logger.error("Failed to start scan", scan_id=scan_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start scan: {str(e)}"
        )

async def _start_scan_background(scan_id: str, scanning_service: ScanningService):
    """Background task to start scan"""
    try:
        success = await scanning_service.start_scan(scan_id)
        if success:
            # Notify WebSocket subscribers
            await websocket_manager.broadcast_to_topic("scans", {
                "event": "scan_started",
                "scan_id": scan_id
            })
    except Exception as e:
        logger.error("Failed to start scan in background", scan_id=scan_id, error=str(e))

@router.post("/{scan_id}/stop")
async def stop_scan(
    scan_id: str,
    scanning_service: ScanningService = Depends()
):
    """Stop a running scan"""
    try:
        success = await scanning_service.stop_scan(scan_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Scan {scan_id} not found or not running"
            )
            
        logger.info("Scan stopped", scan_id=scan_id)
        
        # Notify WebSocket subscribers
        await websocket_manager.broadcast_to_topic("scans", {
            "event": "scan_stopped",
            "scan_id": scan_id
        })
        
        return {"message": "Scan stopped successfully", "scan_id": scan_id}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to stop scan", scan_id=scan_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to stop scan: {str(e)}"
        )

@router.get("/{scan_id}/status")
async def get_scan_status(
    scan_id: str,
    scanning_service: ScanningService = Depends()
):
    """Get scan status and progress"""
    try:
        status_info = await scanning_service.get_scan_status(scan_id)
        if not status_info:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Scan {scan_id} not found"
            )
        return status_info
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get scan status", scan_id=scan_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get scan status: {str(e)}"
        )

@router.get("/{scan_id}/logs")
async def get_scan_logs(
    scan_id: str,
    page: int = 1,
    page_size: int = 100,
    scanning_service: ScanningService = Depends()
):
    """Get scan execution logs"""
    try:
        logs = await scanning_service.get_scan_logs(
            scan_id=scan_id,
            page=page,
            page_size=page_size
        )
        return logs
        
    except Exception as e:
        logger.error("Failed to get scan logs", scan_id=scan_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get scan logs: {str(e)}"
        )

@router.get("/templates/")
async def get_scan_templates(
    data_source_type: Optional[str] = None,
    scanning_service: ScanningService = Depends()
):
    """Get available scan templates"""
    try:
        templates = await scanning_service.get_scan_templates(data_source_type)
        return {"templates": templates}
        
    except Exception as e:
        logger.error("Failed to get scan templates", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get scan templates: {str(e)}"
        )

@router.get("/data-sources/")
async def get_supported_data_sources(
    scanning_service: ScanningService = Depends()
):
    """Get supported data source types"""
    try:
        data_sources = await scanning_service.get_supported_data_sources()
        return {"data_sources": data_sources}
        
    except Exception as e:
        logger.error("Failed to get data sources", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get data sources: {str(e)}"
        )
