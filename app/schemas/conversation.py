from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class ConversationResponse(BaseModel):
    id: str
    instagramAccount: str
    igUserId: str
    igUsername: Optional[str] = None
    lastMessage: Optional[str] = None
    lastMessageTimestamp: Optional[datetime] = None
    unreadCount: int
    isActive: bool
    createdAt: datetime
    updatedAt: datetime

    class Config:
        from_attributes = True


class ConversationListResponse(BaseModel):
    conversations: list[ConversationResponse]
    total: int
    limit: int
    skip: int

