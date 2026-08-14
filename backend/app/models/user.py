"""User Data Domain Models and Authentication Schemas.

Defines Pydantic models for user creation, update, database storage, API responses,
and JWT authentication tokens conforming to Section 8.3 schema.
"""

from datetime import datetime, timezone
from typing import Optional
from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    """Base user properties shared across request/response schemas."""

    email: EmailStr
    full_name: Optional[str] = None
    is_active: bool = True
    is_superuser: bool = False


class UserCreate(UserBase):
    """Schema for user registration requests containing raw password."""

    password: str = Field(..., min_length=6, description="User password (min 6 characters)")


class UserUpdate(BaseModel):
    """Schema for updating user profile information."""

    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None


class UserInDB(UserBase):
    """Schema representing complete User document persisted in MongoDB."""

    id: str = Field(..., description="Unique document ID (str of ObjectId)")
    hashed_password: str = Field(..., description="Bcrypt hashed password")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class UserResponse(UserBase):
    """Safe public schema for User responses excluding password hashes."""

    id: str
    created_at: datetime
    updated_at: datetime


class Token(BaseModel):
    """JWT bearer token response payload."""

    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Decoded JWT token payload subject data."""

    email: Optional[str] = None


__all__ = [
    "UserBase",
    "UserCreate",
    "UserUpdate",
    "UserInDB",
    "UserResponse",
    "Token",
    "TokenData",
]
