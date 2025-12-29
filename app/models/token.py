from beanie import Document
from pydantic import Field, ConfigDict
from datetime import datetime
from typing import Optional
from bson import ObjectId


class Token(Document):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    token: str = Field(..., index=True)
    user: ObjectId = Field(..., index=True)
    type: str = Field(..., pattern="^(refresh|resetPassword|verifyEmail)$")
    expires: datetime
    blacklisted: bool = Field(default=False)
    createdAt: datetime = Field(default_factory=datetime.utcnow)
    updatedAt: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "tokens"
        indexes = [
            [("token", 1)],
            [("user", 1)],
            [("type", 1)],
        ]

