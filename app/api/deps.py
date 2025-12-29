from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from bson import ObjectId
from app.models.user import User
from app.core.security import decode_token
from app.core.roles import get_permissions_for_role, has_permission
from app.core.exceptions import UnauthorizedError, ForbiddenError

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> User:
    """Get current authenticated user from JWT token"""
    token = credentials.credentials
    payload = decode_token(token)
    
    if not payload:
        raise UnauthorizedError("Invalid authentication token")
    
    if payload.get("type") != "access":
        raise UnauthorizedError("Invalid token type")
    
    user_id = payload.get("sub")
    if not user_id:
        raise UnauthorizedError("Invalid token payload")
    
    user = await User.get(ObjectId(user_id))
    if not user:
        raise UnauthorizedError("User not found")
    
    return user


def require_permission(permission: str):
    """Dependency factory to require a specific permission"""
    async def permission_checker(current_user: User = Depends(get_current_user)) -> User:
        user_permissions = get_permissions_for_role(current_user.role)
        if not has_permission(user_permissions, permission):
            raise ForbiddenError(f"Permission required: {permission}")
        return current_user
    return permission_checker

