from beanie import Document
from pydantic import BaseModel, Field, HttpUrl, ConfigDict
from datetime import datetime
from typing import Optional, List, Literal
from bson import ObjectId


class Attachment(BaseModel):
    type: Literal["image", "video", "audio", "file"]
    url: HttpUrl


class Message(Document):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    conversation: ObjectId = Field(..., index=True)
    instagramAccount: ObjectId = Field(..., index=True)
    messageId: Optional[str] = Field(None, unique=True, sparse=True)  # Meta message ID
    sender: Literal["user", "page"] = Field(...)
    senderId: str = Field(..., min_length=1)
    text: Optional[str] = None
    attachments: List[Attachment] = Field(default_factory=list)
    timestamp: datetime = Field(..., index=True)
    isRead: bool = Field(default=False, index=True)
    metadata: Optional[dict] = None
    createdAt: datetime = Field(default_factory=datetime.utcnow)
    updatedAt: datetime = Field(default_factory=datetime.utcnow)

    def transform(self) -> dict:
        """Return message data"""
        return {
            "id": str(self.id),
            "conversation": str(self.conversation),
            "instagramAccount": str(self.instagramAccount),
            "messageId": self.messageId,
            "sender": self.sender,
            "senderId": self.senderId,
            "text": self.text,
            "attachments": [{"type": a.type, "url": str(a.url)} for a in self.attachments],
            "timestamp": self.timestamp.isoformat(),
            "isRead": self.isRead,
            "metadata": self.metadata,
            "createdAt": self.createdAt.isoformat(),
            "updatedAt": self.updatedAt.isoformat(),
        }

    class Settings:
        name = "messages"
        indexes = [
            [("conversation", 1), ("timestamp", -1)],
            [("instagramAccount", 1), ("timestamp", -1)],
            [("messageId", 1)],  # Unique sparse index
            [("sender", 1), ("isRead", 1)],
        ]

