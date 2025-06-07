"""
Authentication middleware for JWT token validation.
"""
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional, Dict, Any
import logging

from ..services.auth_service import AuthService
from ..core.config import settings

logger = logging.getLogger(__name__)

security = HTTPBearer()
auth_service = AuthService(secret_key=settings.SECRET_KEY)

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Dict[str, Any]:
    """
    Dependency to get current authenticated user from JWT token.
    
    Args:
        credentials: HTTP Bearer token credentials
    
    Returns:
        Dictionary containing user information
    
    Raises:
        HTTPException: If token is invalid or user not found
    """
    try:
        token = credentials.credentials
        user = await auth_service.get_current_user(token)
        return user
    except ValueError as e:
        logger.warning(f"Authentication failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

async def get_current_active_user(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Dependency to get current active user.
    
    Args:
        current_user: Current user from JWT token
    
    Returns:
        Dictionary containing active user information
    
    Raises:
        HTTPException: If user is inactive
    """
    if not current_user.get("is_active"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user

def require_permission(permission: str):
    """
    Dependency factory to require specific permission.
    
    Args:
        permission: Required permission string
    
    Returns:
        Dependency function that checks permission
    """
    async def permission_checker(
        current_user: Dict[str, Any] = Depends(get_current_active_user)
    ) -> Dict[str, Any]:
        user_permissions = current_user.get("permissions", [])
        
        if permission not in user_permissions and "admin_all" not in user_permissions:
            logger.warning(f"Permission denied for user {current_user.get('email')}: {permission}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission denied: {permission} required"
            )
        
        return current_user
    
    return permission_checker

def require_role(role: str):
    """
    Dependency factory to require specific role.
    
    Args:
        role: Required role string
    
    Returns:
        Dependency function that checks role
    """
    async def role_checker(
        current_user: Dict[str, Any] = Depends(get_current_active_user)
    ) -> Dict[str, Any]:
        user_role = current_user.get("role")
        
        if user_role != role and user_role != "admin":
            logger.warning(f"Role denied for user {current_user.get('email')}: {role}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role required: {role}"
            )
        
        return current_user
    
    return role_checker

# Optional authentication for public endpoints that benefit from user context
async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(
        HTTPBearer(auto_error=False)
    )
) -> Optional[Dict[str, Any]]:
    """
    Optional dependency to get current user if token is provided.
    
    Args:
        credentials: Optional HTTP Bearer token credentials
    
    Returns:
        Dictionary containing user information or None
    """
    if not credentials:
        return None
    
    try:
        token = credentials.credentials
        user = await auth_service.get_current_user(token)
        return user if user.get("is_active") else None
    except Exception as e:
        logger.debug(f"Optional authentication failed: {str(e)}")
        return None
