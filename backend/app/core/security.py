"""Security, Password Hashing, and JWT Token Utilities.

Provides bcrypt password hashing, verification routines, and JWT access token creation/decoding
matching Section 8.3 & Section 11 security requirements.
"""

from datetime import datetime, timedelta, timezone
import logging
from typing import Any, Dict, Optional
import bcrypt
import jwt
from app.config import settings

logger = logging.getLogger("app.core.security")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify plain text password against stored bcrypt hash."""
    try:
        password_bytes = plain_password.encode("utf-8")[:72]
        hash_bytes = hashed_password.encode("utf-8")
        return bcrypt.checkpw(password_bytes, hash_bytes)
    except Exception as exc:
        logger.error("Password verification error: %s", exc)
        return False


def get_password_hash(password: str) -> str:
    """Generate bcrypt password hash for plain text password."""
    password_bytes = password.encode("utf-8")[:72]
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password_bytes, salt).decode("utf-8")


def create_access_token(
    data: Dict[str, Any], expires_delta: Optional[timedelta] = None
) -> str:
    """Generate signed JWT access token with expiration payload."""
    to_encode = data.copy()
    now = datetime.now(timezone.utc)
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire, "iat": now})
    encoded_jwt = jwt.encode(
        to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt


def decode_access_token(token: str) -> Dict[str, Any]:
    """Decode and verify signed JWT access token."""
    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM]
        )
        return payload
    except jwt.PyJWTError as exc:
        logger.warning("JWT token decoding failed: %s", exc)
        raise ValueError(f"Invalid or expired JWT token: {exc}") from exc


__all__ = [
    "verify_password",
    "get_password_hash",
    "create_access_token",
    "decode_access_token",
]
