from typing import Optional
from pydantic import BaseModel, EmailStr, Field


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: dict | None = None


class TokenPayload(BaseModel):
    sub: str
    exp: int


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    full_name: str = Field(min_length=2)
    phone: str | None = None
    role: str = "customer"


class LoginRequest(BaseModel):
    identifier: str
    password: str


class GoogleLoginRequest(BaseModel):
    token: str
    role: Optional[str] = "customer"


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: Optional[str] = None
    email: Optional[EmailStr] = None
    otp: Optional[str] = None
    new_password: str = Field(min_length=8)


class SendResetOtpRequest(BaseModel):
    email: EmailStr


class VerifyResetOtpRequest(BaseModel):
    email: EmailStr
    otp: str = Field(min_length=6, max_length=6)


class VerifyResetOtpResponse(BaseModel):
    reset_token: str
    message: str = "OTP verified successfully"


class ResetPasswordWithOtpRequest(BaseModel):
    reset_token: str
    new_password: str = Field(min_length=8)
