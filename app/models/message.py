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
        # Ensure timestamps are sent as UTC with 'Z' suffix for proper frontend parsing
        # Python's isoformat() doesn't add 'Z' for naive datetimes, so we add it manually
        timestamp_str = self.timestamp.isoformat()
        if not timestamp_str.endswith('Z') and '+' not in timestamp_str:
            timestamp_str = timestamp_str + 'Z'
        
        created_at_str = self.createdAt.isoformat()
        if not created_at_str.endswith('Z') and '+' not in created_at_str:
            created_at_str = created_at_str + 'Z'
        
        updated_at_str = self.updatedAt.isoformat()
        if not updated_at_str.endswith('Z') and '+' not in updated_at_str:
            updated_at_str = updated_at_str + 'Z'
        
        return {
            "id": str(self.id),
            "conversation": str(self.conversation),
            "instagramAccount": str(self.instagramAccount),
            "messageId": self.messageId,
            "sender": self.sender,
            "senderId": self.senderId,
            "text": self.text,
            "attachments": [{"type": a.type, "url": str(a.url)} for a in self.attachments],
            "timestamp": timestamp_str,
            "isRead": self.isRead,
            "metadata": self.metadata,
            "createdAt": created_at_str,
            "updatedAt": updated_at_str,
        }

    class Settings:
        name = "messages"
        indexes = [
            [("conversation", 1), ("timestamp", -1)],
            [("instagramAccount", 1), ("timestamp", -1)],
            [("messageId", 1)],  # Unique sparse index
            [("sender", 1), ("isRead", 1)],
        ]

