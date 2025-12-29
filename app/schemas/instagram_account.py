from pydantic import BaseModel, Field, HttpUrl
from datetime import datetime
from typing import Optional


class InstagramAccountBase(BaseModel):
    pageId: str = Field(..., min_length=1)
    instagramBusinessId: str = Field(..., min_length=1)
    username: Optional[str] = Field(None, max_length=100)
    profilePictureUrl: Optional[HttpUrl] = None
    followersCount: Optional[int] = Field(None, ge=0)


class InstagramAccountCreate(InstagramAccountBase):
    pageAccessToken: str = Field(..., min_length=1)


class InstagramAccountResponse(InstagramAccountBase):
    id: str
    user: str
    isActive: bool
    createdAt: datetime
    updatedAt: datetime

    class Config:
        from_attributes = True


class InstagramAccountUpdate(BaseModel):
    username: Optional[str] = Field(None, max_length=100)
    profilePictureUrl: Optional[HttpUrl] = None
    followersCount: Optional[int] = Field(None, ge=0)
    isActive: Optional[bool] = None


class InstagramProfileResponse(BaseModel):
    username: Optional[str] = None
    name: Optional[str] = None
    biography: Optional[str] = None
    website: Optional[str] = None
    profilePictureUrl: Optional[str] = None
    followersCount: int = 0
    mediaCount: int = 0
    media: list[dict] = []

