from beanie import Document
from pydantic import EmailStr, Field, field_validator, ConfigDict
from datetime import datetime
from typing import Optional
from bson import ObjectId
from app.core.security import get_password_hash, verify_password


class User(Document):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr = Field(..., unique=True)
    password: str = Field(..., min_length=8)
    role: str = Field(default="user", pattern="^(user|admin)$")
    createdAt: datetime = Field(default_factory=datetime.utcnow)
    updatedAt: datetime = Field(default_factory=datetime.utcnow)

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        # Check if password is already hashed (bcrypt hashes start with $2b$, $2a$, or $2y$)
        if v.startswith("$2") and len(v) == 60:
            # Already hashed, return as-is
            return v
        
        # Validate plain password requirements
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        if not any(c.isalpha() for c in v):
            raise ValueError("Password must contain at least one letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one number")
        
        # Hash the plain password
        return get_password_hash(v)

    def is_password_match(self, password: str) -> bool:
        """Verify password"""
        return verify_password(password, self.password)

    def transform(self) -> dict:
        """Return user data without password"""
        return {
            "id": str(self.id),
            "name": self.name,
            "email": self.email,
            "role": self.role,
            "createdAt": self.createdAt.isoformat(),
            "updatedAt": self.updatedAt.isoformat(),
        }

    @classmethod
    async def is_email_taken(cls, email: str, exclude_user_id: Optional[ObjectId] = None) -> bool:
        """Check if email is already taken"""
        query = {"email": email.lower()}
        if exclude_user_id:
            query["_id"] = {"$ne": exclude_user_id}
        user = await cls.find_one(query)
        return user is not None

    class Settings:
        name = "users"
        indexes = [
            [("email", 1)],  # Unique index on email
        ]

