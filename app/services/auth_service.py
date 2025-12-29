from datetime import datetime, timedelta
from typing import Optional
from bson import ObjectId
from app.models.user import User
from app.models.token import Token
from app.schemas.auth import RegisterRequest, LoginRequest
from app.core.security import create_access_token, create_refresh_token, decode_token
from app.core.exceptions import UnauthorizedError, BadRequestError
from app.config.settings import settings
import logging

logger = logging.getLogger(__name__)


async def register_user(data: RegisterRequest) -> dict:
    """Register a new user"""
    # Check if email is taken
    if await User.is_email_taken(data.email):
        raise BadRequestError("Email already registered")
    
    # Create user
    user = User(
        name=data.name.strip(),
        email=data.email.lower(),
        password=data.password,  # Will be hashed by validator
    )
    await user.insert()
    
    # Generate tokens
    access_token = create_access_token({"sub": str(user.id), "role": user.role})
    refresh_token = create_refresh_token({"sub": str(user.id)})
    
    # Store refresh token
    refresh_token_doc = Token(
        token=refresh_token,
        user=user.id,
        type="refresh",
        expires=datetime.utcnow() + timedelta(days=settings.JWT_REFRESH_EXPIRATION_DAYS),
    )
    await refresh_token_doc.insert()
    
    logger.info(f"User registered: {user.email}")
    
    return {
        "user": user.transform(),
        "tokens": {
            "access": {
                "token": access_token,
                "expires": datetime.utcnow() + timedelta(minutes=settings.JWT_ACCESS_EXPIRATION_MINUTES),
            },
            "refresh": {
                "token": refresh_token,
                "expires": datetime.utcnow() + timedelta(days=settings.JWT_REFRESH_EXPIRATION_DAYS),
            },
        },
    }


async def login_user(data: LoginRequest) -> dict:
    """Login user"""
    user = await User.find_one({"email": data.email.lower()})
    if not user or not user.is_password_match(data.password):
        raise UnauthorizedError("Invalid email or password")
    
    # Generate tokens
    access_token = create_access_token({"sub": str(user.id), "role": user.role})
    refresh_token = create_refresh_token({"sub": str(user.id)})
    
    # Store refresh token
    refresh_token_doc = Token(
        token=refresh_token,
        user=user.id,
        type="refresh",
        expires=datetime.utcnow() + timedelta(days=settings.JWT_REFRESH_EXPIRATION_DAYS),
    )
    await refresh_token_doc.insert()
    
    logger.info(f"User logged in: {user.email}")
    
    return {
        "user": user.transform(),
        "tokens": {
            "access": {
                "token": access_token,
                "expires": datetime.utcnow() + timedelta(minutes=settings.JWT_ACCESS_EXPIRATION_MINUTES),
            },
            "refresh": {
                "token": refresh_token,
                "expires": datetime.utcnow() + timedelta(days=settings.JWT_REFRESH_EXPIRATION_DAYS),
            },
        },
    }


async def logout_user(refresh_token: str) -> None:
    """Logout user by blacklisting refresh token"""
    token_doc = await Token.find_one({"token": refresh_token, "type": "refresh"})
    if token_doc:
        token_doc.blacklisted = True
        await token_doc.save()
        logger.info(f"User logged out: {token_doc.user}")


async def refresh_tokens(refresh_token: str) -> dict:
    """Refresh access token using refresh token"""
    # Check if token exists and is not blacklisted
    token_doc = await Token.find_one({"token": refresh_token, "type": "refresh", "blacklisted": False})
    if not token_doc:
        raise UnauthorizedError("Invalid refresh token")
    
    # Check if token is expired
    if token_doc.expires < datetime.utcnow():
        raise UnauthorizedError("Refresh token expired")
    
    # Verify token signature
    payload = decode_token(refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise UnauthorizedError("Invalid refresh token")
    
    # Get user
    user = await User.get(token_doc.user)
    if not user:
        raise UnauthorizedError("User not found")
    
    # Generate new tokens
    access_token = create_access_token({"sub": str(user.id), "role": user.role})
    new_refresh_token = create_refresh_token({"sub": str(user.id)})
    
    # Blacklist old refresh token
    token_doc.blacklisted = True
    await token_doc.save()
    
    # Store new refresh token
    new_refresh_token_doc = Token(
        token=new_refresh_token,
        user=user.id,
        type="refresh",
        expires=datetime.utcnow() + timedelta(days=settings.JWT_REFRESH_EXPIRATION_DAYS),
    )
    await new_refresh_token_doc.insert()
    
    return {
        "access": {
            "token": access_token,
            "expires": datetime.utcnow() + timedelta(minutes=settings.JWT_ACCESS_EXPIRATION_MINUTES),
        },
        "refresh": {
            "token": new_refresh_token,
            "expires": datetime.utcnow() + timedelta(days=settings.JWT_REFRESH_EXPIRATION_DAYS),
        },
    }


async def forgot_password(email: str) -> dict:
    """Generate password reset token"""
    user = await User.find_one({"email": email.lower()})
    if not user:
        # Don't reveal if email exists
        return {"resetPasswordToken": "dummy_token"}
    
    # Generate reset token
    reset_token = create_refresh_token({"sub": str(user.id), "type": "resetPassword"})
    
    # Store reset token
    reset_token_doc = Token(
        token=reset_token,
        user=user.id,
        type="resetPassword",
        expires=datetime.utcnow() + timedelta(hours=1),  # 1 hour expiry
    )
    await reset_token_doc.insert()
    
    logger.info(f"Password reset token generated for: {user.email}")
    
    return {"resetPasswordToken": reset_token}


async def reset_password(token: str, new_password: str) -> None:
    """Reset password using reset token"""
    # Check if token exists and is not blacklisted
    token_doc = await Token.find_one({"token": token, "type": "resetPassword", "blacklisted": False})
    if not token_doc:
        raise UnauthorizedError("Invalid reset token")
    
    # Check if token is expired
    if token_doc.expires < datetime.utcnow():
        raise UnauthorizedError("Reset token expired")
    
    # Verify token signature
    payload = decode_token(token)
    if not payload or payload.get("type") != "resetPassword":
        raise UnauthorizedError("Invalid reset token")
    
    # Get user
    user = await User.get(token_doc.user)
    if not user:
        raise UnauthorizedError("User not found")
    
    # Update password
    user.password = new_password  # Will be hashed by validator
    user.updatedAt = datetime.utcnow()
    await user.save()
    
    # Blacklist reset token
    token_doc.blacklisted = True
    await token_doc.save()
    
    logger.info(f"Password reset for: {user.email}")


async def verify_email(token: str) -> None:
    """Verify email using verification token"""
    # Check if token exists and is not blacklisted
    token_doc = await Token.find_one({"token": token, "type": "verifyEmail", "blacklisted": False})
    if not token_doc:
        raise UnauthorizedError("Invalid verification token")
    
    # Check if token is expired
    if token_doc.expires < datetime.utcnow():
        raise UnauthorizedError("Verification token expired")
    
    # Verify token signature
    payload = decode_token(token)
    if not payload or payload.get("type") != "verifyEmail":
        raise UnauthorizedError("Invalid verification token")
    
    # Get user
    user = await User.get(token_doc.user)
    if not user:
        raise UnauthorizedError("User not found")
    
    # Mark email as verified (you can add an emailVerified field to User model if needed)
    # For now, just blacklist the token
    token_doc.blacklisted = True
    await token_doc.save()
    
    logger.info(f"Email verified for: {user.email}")

