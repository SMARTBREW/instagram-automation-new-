from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional
from app.schemas.user import UserResponse


class TokenResponse(BaseModel):
    token: str
    expires: datetime


class TokensResponse(BaseModel):
    access: TokenResponse
    refresh: TokenResponse


class RegisterRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=8)


class RegisterResponse(BaseModel):
    user: UserResponse
    tokens: TokensResponse


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    user: UserResponse
    tokens: TokensResponse


class LogoutRequest(BaseModel):
    refreshToken: str


class RefreshTokenRequest(BaseModel):
    refreshToken: str


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ForgotPasswordResponse(BaseModel):
    resetPasswordToken: str


class ResetPasswordRequest(BaseModel):
    password: str = Field(..., min_length=8)


class VerifyEmailRequest(BaseModel):
    token: str

