"""Authentication Endpoints (Registration & Login).

Provides user registration (`POST /api/v1/auth/register`) and JWT authentication login (`POST /api/v1/auth/login`)
matching Section 8.3 schema and security specifications.
"""

from datetime import datetime, timezone
import logging
from typing import Optional, Union
import uuid
from fastapi import APIRouter, Depends, Form, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr
from app.core.security import create_access_token, get_password_hash, verify_password
from app.db.mongodb import get_db
from app.exceptions import BadRequestException, UnauthorizedException
from app.models.user import Token, UserCreate, UserResponse

logger = logging.getLogger("app.api.v1.endpoints.auth")
router = APIRouter()

from app.db.memory_store import _in_memory_users


class LoginRequest(BaseModel):
    """JSON payload for user login request."""

    username: str
    password: str


@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    response_model=UserResponse,
    summary="Register a new user account",
)
async def register_user(
    user_in: UserCreate,
    db=Depends(get_db),
) -> UserResponse:
    """Register a new user, hash password with bcrypt, and persist user document."""
    email_clean = user_in.email.lower().strip()

    # Query existing user from MongoDB or in-memory fallback
    existing_user = None
    if db is not None:
        try:
            existing_user = await db["users"].find_one({"email": email_clean})
        except Exception as exc:
            logger.warning("MongoDB find_one failed during registration: %s. Using fallback store.", exc)
            existing_user = _in_memory_users.get(email_clean)
    else:
        existing_user = _in_memory_users.get(email_clean)

    if existing_user:
        raise BadRequestException(message="Email already registered.")

    now = datetime.now(timezone.utc)
    user_id = str(uuid.uuid4())
    hashed_pwd = get_password_hash(user_in.password)

    user_doc = {
        "_id": user_id,
        "id": user_id,
        "email": email_clean,
        "full_name": user_in.full_name,
        "is_active": user_in.is_active,
        "is_superuser": user_in.is_superuser,
        "hashed_password": hashed_pwd,
        "created_at": now,
        "updated_at": now,
    }

    if db is not None:
        try:
            await db["users"].insert_one(user_doc)
        except Exception as exc:
            logger.warning("MongoDB insert_one failed: %s. Storing in fallback store.", exc)
            _in_memory_users[email_clean] = user_doc
    else:
        _in_memory_users[email_clean] = user_doc

    logger.info("User registered successfully: '%s' (ID: %s)", email_clean, user_id)

    return UserResponse(
        id=user_id,
        email=email_clean,
        full_name=user_in.full_name,
        is_active=user_in.is_active,
        is_superuser=user_in.is_superuser,
        created_at=now,
        updated_at=now,
    )


@router.post(
    "/login",
    status_code=status.HTTP_200_OK,
    response_model=Token,
    summary="Authenticate user and issue JWT bearer token",
)
async def login_user(
    request: Request,
    db=Depends(get_db),
) -> Token:
    """Authenticate user credentials (JSON or Form data) and issue signed JWT access token."""
    content_type = request.headers.get("content-type", "")
    username = ""
    password = ""

    if "application/json" in content_type:
        body = await request.json()
        username = body.get("username") or body.get("email") or ""
        password = body.get("password") or ""
    else:
        form = await request.form()
        username = form.get("username") or form.get("email") or ""
        password = form.get("password") or ""

    email_clean = str(username).lower().strip()
    if not email_clean or not password:
        raise UnauthorizedException(message="Incorrect email or password.")

    # Find user document
    user = None
    if db is not None:
        try:
            user = await db["users"].find_one({"email": email_clean})
        except Exception as exc:
            logger.warning("MongoDB find_one failed during login: %s. Checking fallback store.", exc)
            user = _in_memory_users.get(email_clean)
    else:
        user = _in_memory_users.get(email_clean)

    if not user:
        raise UnauthorizedException(message="Incorrect email or password.")

    if not verify_password(password, user["hashed_password"]):
        raise UnauthorizedException(message="Incorrect email or password.")

    if not user.get("is_active", True):
        raise BadRequestException(message="User account is inactive.")

    # Issue signed JWT access token
    access_token = create_access_token(data={"sub": user["email"]})
    logger.info("User authenticated successfully: '%s'", email_clean)

    return Token(access_token=access_token, token_type="bearer")


from app.api.deps import get_current_active_user


@router.get(
    "/me",
    status_code=status.HTTP_200_OK,
    response_model=UserResponse,
    summary="Get authenticated current user profile",
)
async def read_users_me(
    current_user=Depends(get_current_active_user),
) -> UserResponse:
    """Return profile details for current authenticated user."""
    return current_user


__all__ = ["router"]
