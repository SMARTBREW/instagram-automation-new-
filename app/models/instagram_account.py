from beanie import Document
from pydantic import Field, HttpUrl, ConfigDict
from datetime import datetime
from typing import Optional
from bson import ObjectId


class InstagramAccount(Document):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    user: ObjectId = Field(..., index=True)
    pageId: str = Field(..., min_length=1)
    instagramBusinessId: str = Field(..., unique=True, min_length=1)
    pageAccessToken: str = Field(..., min_length=1)  # Sensitive, never return in API
    username: Optional[str] = Field(None, max_length=100)
    profilePictureUrl: Optional[HttpUrl] = None
    followersCount: int = Field(default=0, ge=0)
    isActive: bool = Field(default=True)
    createdAt: datetime = Field(default_factory=datetime.utcnow)
    updatedAt: datetime = Field(default_factory=datetime.utcnow)

    def transform(self) -> dict:
        """Return account data without sensitive fields"""
        return {
            "id": str(self.id),
            "user": str(self.user),
            "pageId": self.pageId,
            "instagramBusinessId": self.instagramBusinessId,
            "username": self.username,
            "profilePictureUrl": str(self.profilePictureUrl) if self.profilePictureUrl else None,
            "followersCount": self.followersCount,
            "isActive": self.isActive,
            "createdAt": self.createdAt.isoformat(),
            "updatedAt": self.updatedAt.isoformat(),
        }

    @classmethod
    async def is_instagram_business_id_taken(
        cls, instagram_business_id: str, exclude_account_id: Optional[ObjectId] = None
    ) -> bool:
        """Check if instagram business ID is already taken"""
        query = {"instagramBusinessId": instagram_business_id}
        if exclude_account_id:
            query["_id"] = {"$ne": exclude_account_id}
        account = await cls.find_one(query)
        return account is not None

    class Settings:
        name = "instagram_accounts"
        indexes = [
            [("user", 1), ("instagramBusinessId", 1)],
            [("instagramBusinessId", 1)],  # Unique index
        ]

