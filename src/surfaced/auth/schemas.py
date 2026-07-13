from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserBase(BaseModel):
    full_name: str
    email: EmailStr


class UserRegister(UserBase):
    password: str = Field(min_length=8)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class TokenRefresh(BaseModel):
    refresh_token: str


class PasswordChange(BaseModel):
    old_password: str
    new_password: str = Field(min_length=8)


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    full_name: str
    is_active: bool
    created_at: datetime


class UserUpdate(BaseModel):
    full_name: str | None = None


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    sub: str
    exp: datetime
    type: str
    jti: str
