from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
import structlog

from app.core.logging import get_logger
from app.services.governance_service import GovernanceService

logger = get_logger(__name__)
router = APIRouter()

class Policy(BaseModel):
    id: str
    name: str
    description: str
    policy_type: str
    rules: List[Dict[str, Any]]
    status: str
    created_at: str
    updated_at: str

class PolicyCreateRequest(BaseModel):
    name: str
    description: str
    policy_type: str
    rules: List[Dict[str, Any]]

class ClassificationRule(BaseModel):
    id: str
    name: str
    description: str
    pattern: str
    classification: str
    confidence_threshold: float
    enabled: bool

@router.get("/policies", response_model=List[Policy])
async def get_policies(
    policy_type: Optional[str] = None,
    status: Optional[str] = None,
    governance_service: GovernanceService = Depends()
):
    """Get governance policies"""
    try:
        policies = await governance_service.get_policies(
            policy_type=policy_type,
            status=status
        )
        return policies
        
    except Exception as e:
        logger.error("Failed to get policies", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get policies: {str(e)}"
        )

@router.post("/policies", response_model=Policy)
async def create_policy(
    policy_request: PolicyCreateRequest,
    governance_service: GovernanceService = Depends()
):
    """Create a new governance policy"""
    try:
        policy = await governance_service.create_policy(policy_request)
        logger.info("Policy created", policy_id=policy.id, name=policy.name)
        return policy
        
    except Exception as e:
        logger.error("Failed to create policy", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create policy: {str(e)}"
        )

@router.get("/classifications")
async def get_classifications(
    governance_service: GovernanceService = Depends()
):
    """Get available data classifications"""
    try:
        classifications = await governance_service.get_classifications()
        return {"classifications": classifications}
        
    except Exception as e:
        logger.error("Failed to get classifications", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get classifications: {str(e)}"
        )

@router.get("/compliance/status")
async def get_compliance_status(
    governance_service: GovernanceService = Depends()
):
    """Get overall compliance status"""
    try:
        status = await governance_service.get_compliance_status()
        return status
        
    except Exception as e:
        logger.error("Failed to get compliance status", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get compliance status: {str(e)}"
        )
