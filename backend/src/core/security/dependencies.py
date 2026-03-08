"""
Security dependencies for FastAPI.
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from ..db import get_db
from .jwt import verify_token

security = HTTPBearer()


async def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> str:
    """
    Get current user ID from JWT token.
    
    Args:
        credentials: HTTP Bearer token
        db: Database session
        
    Returns:
        User ID
        
    Raises:
        HTTPException: If token is invalid
    """
    token = credentials.credentials
    payload = verify_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user_id: str = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        )
    return user_id


async def get_current_user(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """
    Get current user object.
    
    Args:
        user_id: User ID from token
        db: Database session
        
    Returns:
        User object
    """
    from uuid import UUID
    from ...modules.users.repository import UserRepository
    
    repository = UserRepository(db)
    user = await repository.get_by_id(UUID(user_id))
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


async def require_admin_user(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """
    Require admin user (ADMIN or SUPER_ADMIN role).
    
    Args:
        user_id: User ID from token
        db: Database session
        
    Returns:
        User object with admin role
        
    Raises:
        HTTPException: If user is not admin (403)
    """
    from uuid import UUID
    from ...modules.users.repository import UserRepository
    from ...modules.users.enums import UserRole
    
    repository = UserRepository(db)
    user = await repository.get_by_id(UUID(user_id))
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    if user.role not in (UserRole.ADMIN, UserRole.SUPER_ADMIN):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions. Admin access required.",
        )
    
    return user
