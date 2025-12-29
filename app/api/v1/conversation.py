from fastapi import APIRouter, Depends, Query, status
from bson import ObjectId
from app.api.deps import get_current_user, require_permission
from app.models.user import User
from app.schemas.conversation import ConversationResponse, ConversationListResponse
from app.models.conversation import Conversation
from app.models.instagram_account import InstagramAccount
from app.core.exceptions import NotFoundError

router = APIRouter()


@router.get("/{account_id}", response_model=ConversationListResponse)
async def get_conversations(
    account_id: str,
    limit: int = Query(20, ge=1, le=100),
    skip: int = Query(0, ge=0),
    current_user: User = Depends(require_permission("view-conversations")),
):
    """Get conversations for an Instagram account. Admins can access any account."""
    # Verify account exists (admin can access any, user must own it)
    if current_user.role == "admin":
        account = await InstagramAccount.find_one({"_id": ObjectId(account_id), "isActive": True})
    else:
        account = await InstagramAccount.find_one({"_id": ObjectId(account_id), "user": current_user.id, "isActive": True})
    
    if not account:
        raise NotFoundError("Instagram account not found")
    
    # Get conversations
    conversations = await Conversation.find(
        {"instagramAccount": account.id, "isActive": True}
    ).sort("-lastMessageTimestamp").skip(skip).limit(limit).to_list()
    
    total = await Conversation.find({"instagramAccount": account.id, "isActive": True}).count()
    
    return ConversationListResponse(
        conversations=[conv.transform() for conv in conversations],
        total=total,
        limit=limit,
        skip=skip,
    )


@router.get("/detail/{conversation_id}", response_model=ConversationResponse)
async def get_conversation_detail(
    conversation_id: str,
    current_user: User = Depends(require_permission("view-conversations")),
):
    """Get conversation details. Admins can access any conversation."""
    conversation = await Conversation.find_one({"_id": ObjectId(conversation_id), "isActive": True})
    if not conversation:
        raise NotFoundError("Conversation not found")
    
    # Verify account (admin can access any, user must own it)
    if current_user.role == "admin":
        account = await InstagramAccount.find_one({"_id": conversation.instagramAccount, "isActive": True})
    else:
        account = await InstagramAccount.find_one({"_id": conversation.instagramAccount, "user": current_user.id, "isActive": True})
    
    if not account:
        raise NotFoundError("Conversation not found")
    
    return conversation.transform()


@router.delete("/detail/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_conversation(
    conversation_id: str,
    current_user: User = Depends(require_permission("view-conversations")),
):
    """Delete conversation (soft delete). Admins can delete any conversation."""
    conversation = await Conversation.find_one({"_id": ObjectId(conversation_id), "isActive": True})
    if not conversation:
        raise NotFoundError("Conversation not found")
    
    # Verify account (admin can delete any, user must own it)
    if current_user.role == "admin":
        account = await InstagramAccount.find_one({"_id": conversation.instagramAccount, "isActive": True})
    else:
        account = await InstagramAccount.find_one({"_id": conversation.instagramAccount, "user": current_user.id, "isActive": True})
    
    if not account:
        raise NotFoundError("Conversation not found")
    
    conversation.isActive = False
    await conversation.save()
    return None

