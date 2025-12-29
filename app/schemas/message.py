from pydantic import BaseModel, Field, HttpUrl
from datetime import datetime
from typing import Optional, List, Literal


class AttachmentSchema(BaseModel):
    type: Literal["image", "video", "audio", "file"]
    url: str


class MessageBase(BaseModel):
    text: Optional[str] = None
    attachment: Optional[AttachmentSchema] = None


class MessageCreate(MessageBase):
    pass


class MessageResponse(BaseModel):
    id: str
    conversation: str
    instagramAccount: str
    messageId: Optional[str] = None
    sender: Literal["user", "page"]
    senderId: str
    text: Optional[str] = None
    attachments: List[AttachmentSchema] = []
    timestamp: datetime
    isRead: bool
    metadata: Optional[dict] = None
    createdAt: datetime
    updatedAt: datetime

    class Config:
        from_attributes = True


class MessageListResponse(BaseModel):
    messages: List[MessageResponse]
    total: int
    limit: int
    skip: int

