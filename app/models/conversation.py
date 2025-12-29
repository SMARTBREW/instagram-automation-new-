from beanie import Document
from pydantic import Field, ConfigDict
from datetime import datetime
from typing import Optional
from bson import ObjectId


class Conversation(Document):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    instagramAccount: ObjectId = Field(..., index=True)
    igUserId: str = Field(..., min_length=1, index=True)
    igUsername: Optional[str] = Field(None, max_length=100)
    lastMessage: Optional[str] = None
    lastMessageTimestamp: Optional[datetime] = Field(None, index=True)
    unreadCount: int = Field(default=0, ge=0)
    isActive: bool = Field(default=True)
    createdAt: datetime = Field(default_factory=datetime.utcnow)
    updatedAt: datetime = Field(default_factory=datetime.utcnow)

    def update_last_message(self, text: str, timestamp: datetime):
        """Update last message and timestamp"""
        self.lastMessage = text[:500] if text else None  # Truncate to 500 chars
        self.lastMessageTimestamp = timestamp
        self.updatedAt = datetime.utcnow()

    def transform(self) -> dict:
        """Return conversation data"""
        return {
            "id": str(self.id),
            "instagramAccount": str(self.instagramAccount),
            "igUserId": self.igUserId,
            "igUsername": self.igUsername,
            "lastMessage": self.lastMessage,
            "lastMessageTimestamp": self.lastMessageTimestamp.isoformat() if self.lastMessageTimestamp else None,
            "unreadCount": self.unreadCount,
            "isActive": self.isActive,
            "createdAt": self.createdAt.isoformat(),
            "updatedAt": self.updatedAt.isoformat(),
        }

    @classmethod
    async def find_or_create(
        cls, instagram_account_id: ObjectId, ig_user_id: str, ig_username: Optional[str] = None
    ) -> "Conversation":
        """Find existing conversation or create new one"""
        conversation = await cls.find_one(
            {"instagramAccount": instagram_account_id, "igUserId": ig_user_id, "isActive": True}
        )
        if not conversation:
            conversation = cls(
                instagramAccount=instagram_account_id,
                igUserId=ig_user_id,
                igUsername=ig_username,
            )
            await conversation.insert()
        elif ig_username and conversation.igUsername != ig_username:
            conversation.igUsername = ig_username
            await conversation.save()
        return conversation

    class Settings:
        name = "conversations"
        indexes = [
            [("instagramAccount", 1), ("igUserId", 1)],  # Unique compound index
            [("instagramAccount", 1), ("lastMessageTimestamp", -1)],
            [("igUserId", 1)],
        ]

