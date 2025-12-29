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
) -> Dict[str, Any]:
    """Send a text message via Instagram Messaging API"""
    target_id = page_id or instagram_business_id
    url = f"https://graph.facebook.com/{settings.META_API_VERSION}/{target_id}/messages"
    
    headers = {"Content-Type": "application/json"}
    params = {"access_token": page_access_token}
    data = {
        "recipient": {"id": recipient_id},
        "message": {"text": message},
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, json=data, headers=headers, params=params)
            response.raise_for_status()
            result = response.json()
            return {"message_id": result.get("message_id")}
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

