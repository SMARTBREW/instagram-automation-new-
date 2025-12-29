from typing import List, Optional
from datetime import datetime
from bson import ObjectId
from app.models.instagram_account import InstagramAccount
from app.schemas.instagram_account import InstagramAccountCreate, InstagramAccountUpdate
from app.core.exceptions import NotFoundError, BadRequestError
from app.utils.meta_api import get_instagram_profile_details
import logging

logger = logging.getLogger(__name__)


async def create_instagram_account(user_id: ObjectId, data: InstagramAccountCreate) -> dict:
    """Create a new Instagram account"""
    # Check if instagram business ID is already taken
    if await InstagramAccount.is_instagram_business_id_taken(data.instagramBusinessId):
        raise BadRequestError("Instagram account already connected")
    
    account = InstagramAccount(
        user=user_id,
        pageId=data.pageId.strip(),
        instagramBusinessId=data.instagramBusinessId.strip(),
        pageAccessToken=data.pageAccessToken,
        username=data.username.strip() if data.username else None,
        profilePictureUrl=data.profilePictureUrl,
        followersCount=data.followersCount or 0,
    )
    await account.insert()
    
    logger.info(f"Instagram account created: {account.instagramBusinessId} for user {user_id}")
    
    return account.transform()


async def get_user_instagram_accounts(user_id: ObjectId, skip: int = 0, limit: int = 100) -> List[dict]:
    """Get all Instagram accounts for a user"""
    accounts = await InstagramAccount.find(
        {"user": user_id, "isActive": True}
    ).skip(skip).limit(limit).to_list()
    
    return [account.transform() for account in accounts]


async def get_instagram_account(account_id: ObjectId, user_id: ObjectId) -> InstagramAccount:
    """Get Instagram account by ID (must belong to user)"""
    account = await InstagramAccount.find_one({"_id": account_id, "user": user_id, "isActive": True})
    if not account:
        raise NotFoundError("Instagram account not found")
    return account


async def update_instagram_account(
    account_id: ObjectId, user_id: ObjectId, data: InstagramAccountUpdate
) -> dict:
    """Update Instagram account"""
    account = await get_instagram_account(account_id, user_id)
    
    update_data = data.model_dump(exclude_unset=True)
    if "username" in update_data and update_data["username"]:
        update_data["username"] = update_data["username"].strip()
    
    for key, value in update_data.items():
        setattr(account, key, value)
    
    account.updatedAt = datetime.utcnow()
    await account.save()
    
    logger.info(f"Instagram account updated: {account_id}")
    
    return account.transform()


async def delete_instagram_account(account_id: ObjectId, user_id: ObjectId) -> None:
    """Soft delete Instagram account"""
    account = await get_instagram_account(account_id, user_id)
    account.isActive = False
    account.updatedAt = datetime.utcnow()
    await account.save()
    
    logger.info(f"Instagram account deleted: {account_id}")


async def get_instagram_profile(account_id: ObjectId, user_id: ObjectId) -> dict:
    """Get Instagram profile details using Meta API"""
    account = await get_instagram_account(account_id, user_id)
    
    if not account.username:
        raise BadRequestError("Username not set for this account")
    
    try:
        profile = await get_instagram_profile_details(
            account.instagramBusinessId,
            account.username,
            account.pageAccessToken,
        )
        return profile
    except Exception as e:
        logger.error(f"Error fetching Instagram profile: {e}")
        raise BadRequestError(f"Failed to fetch profile: {str(e)}")

