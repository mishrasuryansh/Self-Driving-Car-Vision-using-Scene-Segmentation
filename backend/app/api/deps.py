"""FastAPI Authentication and Context Dependencies.

Provides OAuth2 bearer token extraction (`oauth2_scheme`), JWT token validation (`get_current_user`),
and active user status verification (`get_current_active_user`) matching Section 8.3 security specifications.
"""

import logging
from typing import Optional
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from app.config import settings
from app.core.security import decode_access_token
from app.db.memory_store import _in_memory_users
from app.db.mongodb import get_db
from app.exceptions import BadRequestException, UnauthorizedException
from app.models.user import UserInDB

logger = logging.getLogger("app.api.deps")

# OAuth2 Bearer token scheme matching Section 8.3 login endpoint
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login",
    auto_error=False,
)


async def get_current_user(
    token: Optional[str] = Depends(oauth2_scheme),
    db=Depends(get_db),
) -> UserInDB:
    """Decode JWT bearer token and retrieve authenticated User document."""
    if not token:
        raise UnauthorizedException(message="Authentication credentials required.")

    try:
        payload = decode_access_token(token)
        email: Optional[str] = payload.get("sub")
        if not email:
            raise UnauthorizedException(message="Could not validate credentials.")
    except Exception as exc:
        logger.warning("Token verification failed: %s", exc)
        raise UnauthorizedException(message="Could not validate credentials.") from exc

    email_clean = email.lower().strip()

    # Query user from MongoDB or in-memory fallback
    user_doc = None
    if db is not None:
        try:
            user_doc = await db["users"].find_one({"email": email_clean})
        except Exception as exc:
            logger.warning("MongoDB find_one failed in get_current_user: %s", exc)
            user_doc = _in_memory_users.get(email_clean)
    else:
        user_doc = _in_memory_users.get(email_clean)

    if not user_doc:
        raise UnauthorizedException(message="User not found.")

    return UserInDB(
        id=str(user_doc.get("_id") or user_doc.get("id")),
        email=user_doc["email"],
        full_name=user_doc.get("full_name"),
        is_active=user_doc.get("is_active", True),
        is_superuser=user_doc.get("is_superuser", False),
        hashed_password=user_doc["hashed_password"],
        created_at=user_doc.get("created_at"),
        updated_at=user_doc.get("updated_at"),
    )


async def get_current_active_user(
    current_user: UserInDB = Depends(get_current_user),
) -> UserInDB:
    """Verify that current authenticated user account is active."""
    if not current_user.is_active:
        raise BadRequestException(message="Inactive user account.")
    return current_user


__all__ = [
    "oauth2_scheme",
    "get_current_user",
    "get_current_active_user",
]
