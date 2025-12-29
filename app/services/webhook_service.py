from datetime import datetime
from typing import Dict, Any, Optional
from bson import ObjectId
from app.models.instagram_account import InstagramAccount
from app.models.conversation import Conversation
from app.models.message import Message, Attachment
from app.utils.meta_api import get_instagram_user_profile
from app.config.settings import settings
import logging

logger = logging.getLogger(__name__)


async def verify_webhook(mode: str, verify_token: str, challenge: str) -> Optional[str]:
    """Verify webhook subscription"""
    if mode == "subscribe" and verify_token == settings.META_VERIFY_TOKEN:
        logger.info("Webhook verified successfully")
        return challenge
    logger.warning(f"Webhook verification failed: mode={mode}, token_match={verify_token == settings.META_VERIFY_TOKEN}")
    return None


async def process_webhook_event(event_data: Dict[str, Any]) -> str:
    """Process incoming webhook event from Meta"""
    try:
        entry = event_data.get("entry", [])
        if not entry:
            logger.warning("Empty webhook entry")
            return "EVENT_RECEIVED"
        
        for entry_item in entry:
            messaging = entry_item.get("messaging", [])
            for message_event in messaging:
                await process_messaging_event(message_event)
        
        return "EVENT_RECEIVED"
    except Exception as e:
        logger.error(f"Error processing webhook event: {e}", exc_info=True)
        return "EVENT_RECEIVED"  # Always return success to Meta


async def process_messaging_event(event: Dict[str, Any]) -> None:
    """Process a single messaging event"""
    sender = event.get("sender", {})
    recipient = event.get("recipient", {})
    
    sender_id = sender.get("id")
    recipient_id = recipient.get("id")
    
    if not sender_id or not recipient_id:
        logger.warning("Missing sender or recipient ID in webhook event")
        return
    
    # Find Instagram account by recipient ID (instagramBusinessId)
    account = await InstagramAccount.find_one(
        {"instagramBusinessId": recipient_id, "isActive": True}
    )
    if not account:
        logger.warning(f"Instagram account not found for recipient: {recipient_id}")
        return
    
    # Handle different event types
    if "message" in event:
        await process_message_event(event, account, sender_id)
    elif "reaction" in event:
        await process_reaction_event(event, account, sender_id)
    elif "read" in event:
        await process_read_event(event, account, sender_id)


async def process_message_event(
    event: Dict[str, Any], account: InstagramAccount, sender_id: str
) -> None:
    """Process incoming message event"""
    message_data = event.get("message", {})
    message_id = message_data.get("mid")
    text = message_data.get("text")
    attachments = message_data.get("attachments", [])
    timestamp = event.get("timestamp")
    
    if not message_id:
        logger.warning("Message ID missing in webhook event")
        return
    
    # Check if message already exists (prevent duplicates)
    existing_message = await Message.find_one({"messageId": message_id})
    if existing_message:
        logger.info(f"Duplicate message ignored: {message_id}")
        return
    
    # Get username from Meta API
    ig_username = None
    try:
        user_profile = await get_instagram_user_profile(sender_id, account.pageAccessToken)
        ig_username = user_profile.get("username")
    except Exception as e:
        logger.warning(f"Failed to fetch username for {sender_id}: {e}")
    
    # Find or create conversation
    conversation = await Conversation.find_or_create(
        account.id, sender_id, ig_username
    )
    
    # Process attachments
    attachment_objects = []
    for att in attachments:
        att_type = att.get("type", "file")
        payload = att.get("payload", {})
        url = payload.get("url")
        if url:
            attachment_objects.append(Attachment(type=att_type, url=url))
    
    # Create message timestamp
    if timestamp:
        message_timestamp = datetime.fromtimestamp(timestamp / 1000)
    else:
        message_timestamp = datetime.utcnow()
    
    # Create message record
    message = Message(
        conversation=conversation.id,
        instagramAccount=account.id,
        messageId=message_id,
        sender="user",
        senderId=sender_id,
        text=text,
        attachments=attachment_objects,
        timestamp=message_timestamp,
        isRead=False,
    )
    await message.insert()
    
    # Update conversation
    conversation.update_last_message(text or f"[{len(attachments)} attachment(s)]", message_timestamp)
    conversation.unreadCount += 1
    conversation.updatedAt = datetime.utcnow()
    await conversation.save()
    
    logger.info(f"Message processed: {message_id} from {sender_id} in conversation {conversation.id}")


async def process_reaction_event(
    event: Dict[str, Any], account: InstagramAccount, sender_id: str
) -> None:
    """Process reaction event (optional implementation)"""
    reaction = event.get("reaction", {})
    logger.info(f"Reaction event received: {reaction} from {sender_id}")
    # Implement reaction logging if needed


async def process_read_event(
    event: Dict[str, Any], account: InstagramAccount, sender_id: str
) -> None:
    """Process read receipt event (optional implementation)"""
    read = event.get("read", {})
    logger.info(f"Read receipt received: {read} from {sender_id}")
    # Implement read receipt logging if needed

