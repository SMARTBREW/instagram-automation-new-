import httpx
from typing import Optional, Dict, Any
from app.config.settings import settings
import logging

logger = logging.getLogger(__name__)


async def get_instagram_user_profile(ig_user_id: str, page_access_token: str) -> Dict[str, Any]:
    """Get Instagram user profile by user ID"""
    url = f"https://graph.facebook.com/{settings.META_API_VERSION}/{ig_user_id}"
    params = {
        "fields": "username,name",
        "access_token": page_access_token,
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            return {
                "username": data.get("username"),
                "name": data.get("name"),
            }
        except httpx.HTTPError as e:
            logger.error(f"Error fetching Instagram user profile: {e}")
            raise


async def get_instagram_user_by_username(
    instagram_business_id: str, username: str, page_access_token: str
) -> Dict[str, Any]:
    """Get Instagram user profile by username using business_discovery"""
    url = f"https://graph.facebook.com/{settings.META_API_VERSION}/{instagram_business_id}"
    params = {
        "fields": f"business_discovery.username({username}){{username,name,biography,website,profile_picture_url}}",
        "access_token": page_access_token,
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            business_discovery = data.get("business_discovery", {})
            return {
                "username": business_discovery.get("username"),
                "name": business_discovery.get("name"),
                "biography": business_discovery.get("biography"),
                "website": business_discovery.get("website"),
                "profile_picture_url": business_discovery.get("profile_picture_url"),
            }
        except httpx.HTTPError as e:
            logger.error(f"Error fetching Instagram user by username: {e}")
            raise


async def send_instagram_message(
    recipient_id: str,
    message: str,
    page_access_token: str,
    instagram_business_id: str,
    page_id: Optional[str] = None,
    messaging_tag: Optional[str] = None,
) -> Dict[str, Any]:
    """Send a text message via Instagram Messaging API
    
    Args:
        recipient_id: Instagram user ID to send message to
        message: Message text content
        page_access_token: Page access token
        instagram_business_id: Instagram Business Account ID
        page_id: Facebook Page ID (preferred for messaging)
        messaging_tag: Optional messaging tag (e.g., 'CONFIRMED_EVENT_UPDATE', 'POST_PURCHASE_UPDATE')
                      Required for messages outside 24-hour window. Tags must be approved by Meta.
    """
    # Use Page ID if available, otherwise fall back to Instagram Business ID
    target_id = page_id or instagram_business_id
    url = f"https://graph.facebook.com/{settings.META_API_VERSION}/{target_id}/messages"
    
    headers = {"Content-Type": "application/json"}
    params = {"access_token": page_access_token}
    data = {
        "recipient": {"id": recipient_id},
        "message": {"text": message},
    }
    
    # Add messaging tag if provided (for messages outside 24-hour window)
    if messaging_tag:
        data["messaging_type"] = "MESSAGE_TAG"
        data["tag"] = messaging_tag
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, json=data, headers=headers, params=params)
            response.raise_for_status()
            result = response.json()
            return {"message_id": result.get("message_id")}
        except httpx.HTTPStatusError as e:
            error_detail = "Unknown error"
            user_friendly_message = None
            if e.response is not None:
                try:
                    error_data = e.response.json()
                    error_detail = error_data.get("error", {}).get("message", str(e.response.text))
                    error_code = error_data.get("error", {}).get("code", "")
                    error_type = error_data.get("error", {}).get("type", "")
                    logger.error(f"Meta API Error - Type: {error_type}, Code: {error_code}, Message: {error_detail}")
                    
                    # Provide user-friendly error messages
                    if error_code == 10 or "(#10)" in error_detail:
                        user_friendly_message = (
                            "Cannot send message: The 24-hour messaging window has expired. "
                            "The user must message you again to open a new window, or you need to use "
                            "an approved messaging tag (requires Meta App Review approval)."
                        )
                    elif error_code == 3 or "(#3)" in error_detail:
                        user_friendly_message = (
                            "Cannot send message: Application does not have permission. "
                            "Please check your Meta App permissions and access token."
                        )
                except:
                    error_detail = e.response.text
            
            if user_friendly_message:
                logger.error(f"Error sending Instagram message: {user_friendly_message}")
                raise Exception(f"Failed to send message: {user_friendly_message}")
            else:
                logger.error(f"Error sending Instagram message: {error_detail}")
                raise Exception(f"Failed to send message: {error_detail}")
        except httpx.HTTPError as e:
            logger.error(f"Error sending Instagram message: {e}")
            if hasattr(e, "response") and e.response is not None:
                logger.error(f"Response: {e.response.text}")
            raise


async def send_instagram_attachment(
    recipient_id: str,
    attachment: Dict[str, Any],
    page_access_token: str,
    instagram_business_id: str,
    page_id: Optional[str] = None,
) -> Dict[str, Any]:
    """Send an attachment via Instagram Messaging API"""
    # Use Page ID if available, otherwise fall back to Instagram Business ID
    target_id = page_id or instagram_business_id
    url = f"https://graph.facebook.com/{settings.META_API_VERSION}/{target_id}/messages"
    
    headers = {"Content-Type": "application/json"}
    params = {"access_token": page_access_token}
    data = {
        "recipient": {"id": recipient_id},
        "message": {
            "attachment": {
                "type": attachment.get("type"),
                "payload": {"url": attachment.get("url")},
            }
        },
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, json=data, headers=headers, params=params)
            response.raise_for_status()
            result = response.json()
            return {"message_id": result.get("message_id")}
        except httpx.HTTPStatusError as e:
            error_detail = "Unknown error"
            if e.response is not None:
                try:
                    error_data = e.response.json()
                    error_detail = error_data.get("error", {}).get("message", str(e.response.text))
                    error_code = error_data.get("error", {}).get("code", "")
                    error_type = error_data.get("error", {}).get("type", "")
                    logger.error(f"Meta API Error - Type: {error_type}, Code: {error_code}, Message: {error_detail}")
                except:
                    error_detail = e.response.text
            logger.error(f"Error sending Instagram attachment: {error_detail}")
            raise Exception(f"Failed to send attachment: {error_detail}")
        except httpx.HTTPError as e:
            logger.error(f"Error sending Instagram attachment: {e}")
            if hasattr(e, "response") and e.response is not None:
                logger.error(f"Response: {e.response.text}")
            raise


async def get_instagram_profile_details(
    instagram_business_id: str, username: str, page_access_token: str
) -> Dict[str, Any]:
    """Get full Instagram profile details including media"""
    url = f"https://graph.facebook.com/{settings.META_API_VERSION}/{instagram_business_id}"
    params = {
        "fields": f"business_discovery.username({username}){{username,name,biography,website,profile_picture_url,followers_count,media_count,media{{id,caption,media_type,media_url,permalink,timestamp}}}}",
        "access_token": page_access_token,
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            business_discovery = data.get("business_discovery", {})
            media = business_discovery.get("media", {}).get("data", [])
            
            return {
                "username": business_discovery.get("username"),
                "name": business_discovery.get("name"),
                "biography": business_discovery.get("biography"),
                "website": business_discovery.get("website"),
                "profilePictureUrl": business_discovery.get("profile_picture_url"),
                "followersCount": business_discovery.get("followers_count", 0),
                "mediaCount": business_discovery.get("media_count", 0),
                "media": media,
            }
        except httpx.HTTPError as e:
            logger.error(f"Error fetching Instagram profile details: {e}")
            raise

