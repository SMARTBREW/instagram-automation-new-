from fastapi import APIRouter, Depends, Query, status
from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.auth import (
    RegisterRequest,
    RegisterResponse,
    LoginRequest,
    LoginResponse,
    LogoutRequest,
    RefreshTokenRequest,
    TokensResponse,
    ForgotPasswordRequest,
    ForgotPasswordResponse,
    ResetPasswordRequest,
    VerifyEmailRequest,
)
from app.services import auth_service

router = APIRouter()


@router.post("/register", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED)
async def register(data: RegisterRequest):
    """Register a new user"""
    return await auth_service.register_user(data)


@router.post("/login", response_model=LoginResponse)
async def login(data: LoginRequest):
    """Login user"""
    return await auth_service.login_user(data)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(data: LogoutRequest):
    """Logout user"""
    await auth_service.logout_user(data.refreshToken)
    return None


@router.post("/refresh-tokens", response_model=TokensResponse)
async def refresh_tokens(data: RefreshTokenRequest):
    """Refresh access token"""
    return await auth_service.refresh_tokens(data.refreshToken)


@router.post("/forgot-password", response_model=ForgotPasswordResponse)
async def forgot_password(data: ForgotPasswordRequest):
    """Request password reset"""
    return await auth_service.forgot_password(data.email)


@router.post("/reset-password", status_code=status.HTTP_204_NO_CONTENT)
async def reset_password(token: str = Query(...), data: ResetPasswordRequest = ...):
    """Reset password"""
    await auth_service.reset_password(token, data.password)
    return None


@router.post("/verify-email", status_code=status.HTTP_204_NO_CONTENT)
async def verify_email(token: str = Query(...)):
    """Verify email"""
    await auth_service.verify_email(token)
    return None

