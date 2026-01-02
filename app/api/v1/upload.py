from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from app.api.deps import require_permission
from app.models.user import User
from app.utils.cloudinary_service import upload_image
from app.core.exceptions import BadRequestError
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/image")
async def upload_image_file(
    file: UploadFile = File(...),
    current_user: User = Depends(require_permission("send-messages")),
):
    """
    Upload an image file to Cloudinary
    
    Returns the Cloudinary URL for the uploaded image
    """
    # Validate file type
    if not file.content_type or not file.content_type.startswith("image/"):
        raise BadRequestError("File must be an image")
    
    # Validate file size (max 10MB)
    file_content = await file.read()
    if len(file_content) > 10 * 1024 * 1024:  # 10MB
        raise BadRequestError("Image size must be less than 10MB")
    
    try:
        # Upload to Cloudinary (synchronous call)
        result = upload_image(file_content, folder=f"instagram-messages/user-{current_user.id}")
        
        return {
            "url": result["url"],
            "public_id": result["public_id"],
            "format": result.get("format"),
            "width": result.get("width"),
            "height": result.get("height"),
        }
    except Exception as e:
        logger.error(f"Error uploading image: {e}")
        raise BadRequestError(f"Failed to upload image: {str(e)}")

