import cloudinary
import cloudinary.uploader
from app.config.settings import settings
import logging

logger = logging.getLogger(__name__)

# Configure Cloudinary
cloudinary.config(
    cloud_name=settings.CLOUDINARY_CLOUD_NAME,
    api_key=settings.CLOUDINARY_API_KEY,
    api_secret=settings.CLOUDINARY_API_SECRET,
)


def upload_image(file_content: bytes, folder: str = "instagram-messages") -> dict:
    """
    Upload an image to Cloudinary
    
    Args:
        file_content: Bytes content of the image file
        folder: Cloudinary folder to store the image
        
    Returns:
        dict with 'url' and 'public_id' keys
    """
    try:
        # Upload to Cloudinary (synchronous operation)
        result = cloudinary.uploader.upload(
            file_content,
            folder=folder,
            resource_type="image",
            transformation=[
                {"quality": "auto"},
                {"fetch_format": "auto"}
            ]
        )
        
        return {
            "url": result.get("secure_url") or result.get("url"),
            "public_id": result.get("public_id"),
            "format": result.get("format"),
            "width": result.get("width"),
            "height": result.get("height"),
        }
    except Exception as e:
        logger.error(f"Error uploading image to Cloudinary: {e}")
        raise Exception(f"Failed to upload image: {str(e)}")


async def delete_image(public_id: str) -> bool:
    """
    Delete an image from Cloudinary
    
    Args:
        public_id: Cloudinary public ID of the image
        
    Returns:
        bool indicating success
    """
    try:
        result = cloudinary.uploader.destroy(public_id)
        return result.get("result") == "ok"
    except Exception as e:
        logger.error(f"Error deleting image from Cloudinary: {e}")
        return False

