from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
import structlog

from app.core.logging import get_logger
from app.services.lineage_service import LineageService

logger = get_logger(__name__)
router = APIRouter()

class LineageNode(BaseModel):
    id: str
    name: str
    type: str
    qualified_name: str
    attributes: Optional[Dict[str, Any]] = {}

class LineageEdge(BaseModel):
    from_node: str
    to_node: str
    relationship_type: str
    attributes: Optional[Dict[str, Any]] = {}

class LineageGraph(BaseModel):
    nodes: List[LineageNode]
    edges: List[LineageEdge]
    center_node: str

class ImpactAnalysisResult(BaseModel):
    entity_id: str
    downstream_entities: List[LineageNode]
    upstream_entities: List[LineageNode]
    impact_count: int
    dependency_count: int

@router.get("/{entity_id}/graph", response_model=LineageGraph)
async def get_lineage_graph(
    entity_id: str,
    depth: int = 3,
    direction: str = "both",  # upstream, downstream, both
    lineage_service: LineageService = Depends()
):
    """Get lineage graph for an entity"""
    try:
        if direction not in ["upstream", "downstream", "both"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Direction must be 'upstream', 'downstream', or 'both'"
            )
            
        graph = await lineage_service.get_lineage_graph(
            entity_id=entity_id,
            depth=depth,
            direction=direction
        )
        
        if not graph:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Entity {entity_id} not found"
            )
            
        return graph
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get lineage graph", entity_id=entity_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get lineage graph: {str(e)}"
        )

@router.get("/{entity_id}/upstream", response_model=List[LineageNode])
async def get_upstream_lineage(
    entity_id: str,
    depth: int = 3,
    lineage_service: LineageService = Depends()
):
    """Get upstream lineage for an entity"""
    try:
        upstream = await lineage_service.get_upstream_lineage(
            entity_id=entity_id,
            depth=depth
        )
        return upstream
        
    except Exception as e:
        logger.error("Failed to get upstream lineage", entity_id=entity_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get upstream lineage: {str(e)}"
        )

@router.get("/{entity_id}/downstream", response_model=List[LineageNode])
async def get_downstream_lineage(
    entity_id: str,
    depth: int = 3,
    lineage_service: LineageService = Depends()
):
    """Get downstream lineage for an entity"""
    try:
        downstream = await lineage_service.get_downstream_lineage(
            entity_id=entity_id,
            depth=depth
        )
        return downstream
        
    except Exception as e:
        logger.error("Failed to get downstream lineage", entity_id=entity_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get downstream lineage: {str(e)}"
        )

@router.get("/{entity_id}/impact-analysis", response_model=ImpactAnalysisResult)
async def get_impact_analysis(
    entity_id: str,
    lineage_service: LineageService = Depends()
):
    """Get impact analysis for an entity"""
    try:
        impact_analysis = await lineage_service.get_impact_analysis(entity_id)
        if not impact_analysis:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Entity {entity_id} not found"
            )
        return impact_analysis
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get impact analysis", entity_id=entity_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get impact analysis: {str(e)}"
        )

@router.post("/{from_entity_id}/relationships/{to_entity_id}")
async def create_lineage_relationship(
    from_entity_id: str,
    to_entity_id: str,
    relationship_type: str,
    attributes: Optional[Dict[str, Any]] = None,
    lineage_service: LineageService = Depends()
):
    """Create a lineage relationship between entities"""
    try:
        success = await lineage_service.create_relationship(
            from_entity_id=from_entity_id,
            to_entity_id=to_entity_id,
            relationship_type=relationship_type,
            attributes=attributes or {}
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create relationship"
            )
            
        logger.info(
            "Lineage relationship created",
            from_entity=from_entity_id,
            to_entity=to_entity_id,
            relationship_type=relationship_type
        )
        
        return {"message": "Relationship created successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to create relationship", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create relationship: {str(e)}"
        )

@router.delete("/{from_entity_id}/relationships/{to_entity_id}")
async def delete_lineage_relationship(
    from_entity_id: str,
    to_entity_id: str,
    relationship_type: Optional[str] = None,
    lineage_service: LineageService = Depends()
):
    """Delete a lineage relationship between entities"""
    try:
        success = await lineage_service.delete_relationship(
            from_entity_id=from_entity_id,
            to_entity_id=to_entity_id,
            relationship_type=relationship_type
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Relationship not found"
            )
            
        logger.info(
            "Lineage relationship deleted",
            from_entity=from_entity_id,
            to_entity=to_entity_id,
            relationship_type=relationship_type
        )
        
        return {"message": "Relationship deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to delete relationship", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete relationship: {str(e)}"
        )

@router.get("/search/path")
async def find_lineage_path(
    from_entity_id: str,
    to_entity_id: str,
    max_depth: int = 10,
    lineage_service: LineageService = Depends()
):
    """Find lineage path between two entities"""
    try:
        path = await lineage_service.find_lineage_path(
            from_entity_id=from_entity_id,
            to_entity_id=to_entity_id,
            max_depth=max_depth
        )
        
        return {
            "from_entity": from_entity_id,
            "to_entity": to_entity_id,
            "path": path,
            "path_length": len(path) if path else 0,
            "connected": bool(path)
        }
        
    except Exception as e:
        logger.error("Failed to find lineage path", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to find lineage path: {str(e)}"
        )

@router.get("/{entity_id}/visualization-data")
async def get_lineage_visualization_data(
    entity_id: str,
    depth: int = 3,
    include_attributes: bool = False,
    lineage_service: LineageService = Depends()
):
    """Get lineage data optimized for visualization (D3.js format)"""
    try:
        viz_data = await lineage_service.get_visualization_data(
            entity_id=entity_id,
            depth=depth,
            include_attributes=include_attributes
        )
        
        if not viz_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Entity {entity_id} not found"
            )
            
        return viz_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get visualization data", entity_id=entity_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get visualization data: {str(e)}"
        )
