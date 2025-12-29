from fastapi import APIRouter, Depends, Query, status
from bson import ObjectId
from app.api.deps import get_current_user, require_permission
from app.models.user import User
from app.schemas.message import MessageCreate, MessageResponse, MessageListResponse
from app.services import message_service

router = APIRouter()


@router.get("/{conversation_id}", response_model=MessageListResponse)
async def get_messages(
    conversation_id: str,
    limit: int = Query(50, ge=1, le=100),
    skip: int = Query(0, ge=0),
    current_user: User = Depends(require_permission("view-messages")),
):
    """Get messages for a conversation. Admins can access any conversation."""
    return await message_service.get_conversation_messages(
        ObjectId(conversation_id), current_user.id, skip, limit, current_user.role
    )


@router.post("/{conversation_id}", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
async def send_message(
    conversation_id: str,
    data: MessageCreate,
    current_user: User = Depends(require_permission("send-messages")),
):
    """Send a message via Instagram API. Admins can send from any account."""
    return await message_service.send_message(ObjectId(conversation_id), current_user.id, data, current_user.role)


@router.post("/{conversation_id}/read", status_code=status.HTTP_204_NO_CONTENT)
async def mark_messages_read(
    conversation_id: str,
    current_user: User = Depends(require_permission("view-messages")),
):
    """Mark messages as read. Admins can mark any conversation as read."""
    await message_service.mark_messages_as_read(ObjectId(conversation_id), current_user.id, current_user.role)
    return None

