from typing import List, Optional
from datetime import datetime
from bson import ObjectId
from app.models.message import Message, Attachment
from app.models.conversation import Conversation
from app.models.instagram_account import InstagramAccount
from app.schemas.message import MessageCreate, AttachmentSchema
from app.core.exceptions import NotFoundError, BadRequestError
from app.utils.meta_api import send_instagram_message, send_instagram_attachment
import logging

logger = logging.getLogger(__name__)


async def get_conversation_messages(
    conversation_id: ObjectId, user_id: ObjectId, skip: int = 0, limit: int = 50, user_role: str = "user"
) -> dict:
    """Get messages for a conversation"""
    # Verify conversation exists
    conversation = await Conversation.find_one({"_id": conversation_id, "isActive": True})
    if not conversation:
        raise NotFoundError("Conversation not found")
    
    # Verify account belongs to user (unless admin)
    if user_role == "admin":
        # Admin can access any conversation - just verify account exists
        account = await InstagramAccount.find_one({"_id": conversation.instagramAccount, "isActive": True})
    else:
        # Regular user - must own the account
        account = await InstagramAccount.find_one({"_id": conversation.instagramAccount, "user": user_id, "isActive": True})
    
    if not account:
        raise NotFoundError("Conversation not found")
    
    # Get messages
    messages = await Message.find(
        {"conversation": conversation_id}
    ).sort("-timestamp").skip(skip).limit(limit).to_list()
    
    total = await Message.find({"conversation": conversation_id}).count()
    
    return {
        "messages": [message.transform() for message in messages],
        "total": total,
        "limit": limit,
        "skip": skip,
    }


async def send_message(
    conversation_id: ObjectId, user_id: ObjectId, data: MessageCreate, user_role: str = "user"
) -> dict:
    """Send a message via Instagram API"""
    # Validate at least one of text or attachment
    if not data.text and not data.attachment:
        raise BadRequestError("Either text or attachment is required")
    
    # Verify conversation exists
    conversation = await Conversation.find_one({"_id": conversation_id, "isActive": True})
    if not conversation:
        raise NotFoundError("Conversation not found")
    
    # Verify account belongs to user (unless admin)
    if user_role == "admin":
        # Admin can send messages from any account - just verify account exists
        account = await InstagramAccount.find_one({"_id": conversation.instagramAccount, "isActive": True})
    else:
        # Regular user - must own the account
        account = await InstagramAccount.find_one({"_id": conversation.instagramAccount, "user": user_id, "isActive": True})
    
    if not account:
        raise NotFoundError("Conversation not found")
    
    # Send message via Meta API
    message_id = None
    try:
        if data.attachment:
            attachment_dict = {
                "type": data.attachment.type,
                "url": data.attachment.url,
            }
            result = await send_instagram_attachment(
                conversation.igUserId,
                attachment_dict,
                account.pageAccessToken,
                account.instagramBusinessId,
                account.pageId,
            )
            message_id = result.get("message_id")
        else:
            result = await send_instagram_message(
                conversation.igUserId,
                data.text,
                account.pageAccessToken,
                account.instagramBusinessId,
                account.pageId,
            )
            message_id = result.get("message_id")
    except Exception as e:
        logger.error(f"Error sending message via Meta API: {e}")
        raise BadRequestError(f"Failed to send message: {str(e)}")
    
    # Create message record
    attachments = []
    if data.attachment:
        attachments.append(
            Attachment(type=data.attachment.type, url=data.attachment.url)
        )
    
    message = Message(
        conversation=conversation_id,
        instagramAccount=conversation.instagramAccount,
        messageId=message_id,
        sender="page",
        senderId=account.instagramBusinessId,
        text=data.text,
        attachments=attachments,
        timestamp=datetime.utcnow(),
        isRead=True,  # Outgoing messages are read
    )
    await message.insert()
    
    # Update conversation
    if data.text:
        conversation.update_last_message(data.text, datetime.utcnow())
    else:
        conversation.update_last_message(f"[{data.attachment.type}]", datetime.utcnow())
    await conversation.save()
    
    logger.info(f"Message sent: {message_id} in conversation {conversation_id}")
    
    return message.transform()


async def mark_messages_as_read(conversation_id: ObjectId, user_id: ObjectId, user_role: str = "user") -> None:
    """Mark all user messages in conversation as read"""
    # Verify conversation exists
    conversation = await Conversation.find_one({"_id": conversation_id, "isActive": True})
    if not conversation:
        raise NotFoundError("Conversation not found")
    
    # Verify account belongs to user (unless admin)
    if user_role == "admin":
        # Admin can mark messages as read for any conversation
        account = await InstagramAccount.find_one({"_id": conversation.instagramAccount, "isActive": True})
    else:
        # Regular user - must own the account
        account = await InstagramAccount.find_one({"_id": conversation.instagramAccount, "user": user_id, "isActive": True})
    
    if not account:
        raise NotFoundError("Conversation not found")
    
    # Mark all unread user messages as read
    await Message.find(
        {"conversation": conversation_id, "sender": "user", "isRead": False}
    ).update_many({"$set": {"isRead": True}})
    
    # Reset unread count
    conversation.unreadCount = 0
    conversation.updatedAt = datetime.utcnow()
    await conversation.save()
    
    logger.info(f"Messages marked as read for conversation {conversation_id}")

