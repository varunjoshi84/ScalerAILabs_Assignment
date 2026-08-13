from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class UserBase(BaseModel):
    email: str = Field(..., description="The user's email address")

class UserCreate(UserBase):
    password: str = Field(..., min_length=6, description="The user's password (min 6 characters)")

class UserLogin(UserBase):
    password: str = Field(..., description="The user's password")

class UserResponse(UserBase):
    id: int
    is_active: bool
    is_superuser: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_at: datetime

    class Config:
        from_attributes = True
