from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
import structlog
from datetime import datetime

from app.core.logging import get_logger
from app.models.entity import Entity, EntitySearchRequest, EntityResponse
from app.services.purview_service import PurviewService

logger = get_logger(__name__)
router = APIRouter()

class EntityCreateRequest(BaseModel):
    name: str
    type: str
    qualified_name: str
    attributes: Optional[Dict[str, Any]] = {}
    classifications: Optional[List[str]] = []
    
class EntityUpdateRequest(BaseModel):
    name: Optional[str] = None
    attributes: Optional[Dict[str, Any]] = None
    classifications: Optional[List[str]] = None

class EntitySearchResponse(BaseModel):
    entities: List[EntityResponse]
    total_count: int
    page: int
    page_size: int

@router.get("/", response_model=EntitySearchResponse)
async def search_entities(
    query: Optional[str] = Query(None, description="Search query"),
    entity_type: Optional[str] = Query(None, description="Filter by entity type"),
    classification: Optional[str] = Query(None, description="Filter by classification"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(25, ge=1, le=100, description="Page size"),
    purview_service: PurviewService = Depends()
):
    """Search entities with filters"""
    try:
        search_request = EntitySearchRequest(
            query=query,
            entity_type=entity_type,
            classification=classification,
            page=page,
            page_size=page_size
        )
        
        result = await purview_service.search_entities(search_request)
        
        return EntitySearchResponse(
            entities=result["entities"],
            total_count=result["total_count"],
            page=page,
            page_size=page_size
        )
        
    except Exception as e:
        logger.error("Failed to search entities", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to search entities: {str(e)}"
        )

@router.get("/{entity_id}", response_model=EntityResponse)
async def get_entity(
    entity_id: str,
    purview_service: PurviewService = Depends()
):
    """Get entity by ID"""
    try:
        entity = await purview_service.get_entity(entity_id)
        if not entity:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Entity {entity_id} not found"
            )
        return entity
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get entity", entity_id=entity_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get entity: {str(e)}"
        )

@router.post("/", response_model=EntityResponse, status_code=status.HTTP_201_CREATED)
async def create_entity(
    entity_request: EntityCreateRequest,
    purview_service: PurviewService = Depends()
):
    """Create a new entity"""
    try:
        entity = await purview_service.create_entity(
            name=entity_request.name,
            entity_type=entity_request.type,
            qualified_name=entity_request.qualified_name,
            attributes=entity_request.attributes,
            classifications=entity_request.classifications
        )
        
        logger.info("Entity created", entity_id=entity.id, name=entity.name)
        return entity
        
    except Exception as e:
        logger.error("Failed to create entity", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create entity: {str(e)}"
        )

@router.put("/{entity_id}", response_model=EntityResponse)
async def update_entity(
    entity_id: str,
    entity_request: EntityUpdateRequest,
    purview_service: PurviewService = Depends()
):
    """Update an existing entity"""
    try:
        entity = await purview_service.update_entity(
            entity_id=entity_id,
            name=entity_request.name,
            attributes=entity_request.attributes,
            classifications=entity_request.classifications
        )
        
        if not entity:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Entity {entity_id} not found"
            )
            
        logger.info("Entity updated", entity_id=entity_id)
        return entity
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to update entity", entity_id=entity_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update entity: {str(e)}"
        )

@router.delete("/{entity_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_entity(
    entity_id: str,
    purview_service: PurviewService = Depends()
):
    """Delete an entity"""
    try:
        success = await purview_service.delete_entity(entity_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Entity {entity_id} not found"
            )
            
        logger.info("Entity deleted", entity_id=entity_id)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to delete entity", entity_id=entity_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete entity: {str(e)}"
        )

@router.get("/{entity_id}/classifications")
async def get_entity_classifications(
    entity_id: str,
    purview_service: PurviewService = Depends()
):
    """Get classifications for an entity"""
    try:
        classifications = await purview_service.get_entity_classifications(entity_id)
        return {"entity_id": entity_id, "classifications": classifications}
        
    except Exception as e:
        logger.error("Failed to get entity classifications", entity_id=entity_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get entity classifications: {str(e)}"
        )

@router.post("/{entity_id}/classifications")
async def add_entity_classification(
    entity_id: str,
    classification: str,
    purview_service: PurviewService = Depends()
):
    """Add a classification to an entity"""
    try:
        success = await purview_service.add_entity_classification(entity_id, classification)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Entity {entity_id} not found"
            )
            
        logger.info("Classification added", entity_id=entity_id, classification=classification)
        return {"message": "Classification added successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to add classification", entity_id=entity_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add classification: {str(e)}"
        )

@router.delete("/{entity_id}/classifications/{classification}")
async def remove_entity_classification(
    entity_id: str,
    classification: str,
    purview_service: PurviewService = Depends()
):
    """Remove a classification from an entity"""
    try:
        success = await purview_service.remove_entity_classification(entity_id, classification)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Entity {entity_id} or classification not found"
            )
            
        logger.info("Classification removed", entity_id=entity_id, classification=classification)
        return {"message": "Classification removed successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to remove classification", entity_id=entity_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to remove classification: {str(e)}"
        )

@router.get("/types/", response_model=List[str])
async def get_entity_types(
    purview_service: PurviewService = Depends()
):
    """Get all available entity types"""
    try:
        types = await purview_service.get_entity_types()
        return types
        
    except Exception as e:
        logger.error("Failed to get entity types", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get entity types: {str(e)}"
        )
