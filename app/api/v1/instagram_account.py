from fastapi import APIRouter, Depends, Query, status
from bson import ObjectId
from app.api.deps import get_current_user, require_permission
from app.models.user import User
from app.schemas.instagram_account import (
    InstagramAccountCreate,
    InstagramAccountResponse,
    InstagramAccountUpdate,
    InstagramProfileResponse,
)
from app.services import instagram_service

router = APIRouter()


@router.post("", response_model=InstagramAccountResponse, status_code=status.HTTP_201_CREATED)
async def create_instagram_account(
    data: InstagramAccountCreate,
    current_user: User = Depends(require_permission("manage-instagram-accounts")),
):
    """Connect a new Instagram account"""
    return await instagram_service.create_instagram_account(current_user.id, data)


@router.get("", response_model=list[InstagramAccountResponse])
async def list_instagram_accounts(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: User = Depends(require_permission("manage-instagram-accounts")),
):
    """List Instagram accounts. Admins see all accounts, users see only their own."""
    return await instagram_service.get_user_instagram_accounts(current_user.id, skip, limit, current_user.role)


@router.get("/{account_id}", response_model=InstagramAccountResponse)
async def get_instagram_account(
    account_id: str,
    current_user: User = Depends(require_permission("manage-instagram-accounts")),
):
    """Get Instagram account details. Admins can access any account."""
    account = await instagram_service.get_instagram_account(ObjectId(account_id), current_user.id, current_user.role)
    return await account.transform(include_user_info=(current_user.role == "admin"))


@router.patch("/{account_id}", response_model=InstagramAccountResponse)
async def update_instagram_account(
    account_id: str,
    data: InstagramAccountUpdate,
    current_user: User = Depends(require_permission("manage-instagram-accounts")),
):
    """Update Instagram account. Admins can update any account."""
    return await instagram_service.update_instagram_account(
        ObjectId(account_id), current_user.id, data, current_user.role
    )


@router.delete("/{account_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_instagram_account(
    account_id: str,
    current_user: User = Depends(require_permission("manage-instagram-accounts")),
):
    """Delete Instagram account (soft delete). Admins can delete any account."""
    await instagram_service.delete_instagram_account(ObjectId(account_id), current_user.id, current_user.role)
    return None


@router.get("/{account_id}/profile", response_model=InstagramProfileResponse)
async def get_instagram_profile(
    account_id: str,
    current_user: User = Depends(require_permission("manage-instagram-accounts")),
):
    """Get Instagram profile details. Admins can access any account."""
    return await instagram_service.get_instagram_profile(ObjectId(account_id), current_user.id, current_user.role)

