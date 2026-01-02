from fastapi import APIRouter
from app.api.v1 import auth, instagram_account, conversation, message, webhook, upload

router = APIRouter(prefix="/v1")

router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
router.include_router(instagram_account.router, prefix="/instagram", tags=["Instagram Accounts"])
router.include_router(conversation.router, prefix="/conversations", tags=["Conversations"])
router.include_router(message.router, prefix="/messages", tags=["Messages"])
router.include_router(webhook.router, prefix="/webhook", tags=["Webhook"])
router.include_router(upload.router, prefix="/upload", tags=["Upload"])

