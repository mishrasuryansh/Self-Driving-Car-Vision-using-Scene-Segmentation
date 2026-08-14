"""T036 User Security & Password Hashing Verification Script.

Tests:
1. Verification of bcrypt password hashing and verification routines.
2. Verification of JWT access token encoding and decoding.
3. Verification of User Pydantic models (UserCreate, UserInDB, UserResponse).
"""

from datetime import datetime, timezone
import logging
import os
import sys

# Ensure repository root and backend directory are in sys.path
repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
backend_path = os.path.join(repo_root, "backend")
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from app.core.security import create_access_token, decode_access_token, get_password_hash, verify_password
from app.models.user import Token, UserCreate, UserInDB, UserResponse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("test_t036")


def test_password_hashing():
    print("[TEST 1] Testing bcrypt password hashing and verification...")
    password = "SuperSecretPassword123!"
    hashed = get_password_hash(password)

    assert hashed != password
    assert hashed.startswith("$2b$") or hashed.startswith("$2a$")
    assert verify_password(password, hashed) is True
    assert verify_password("WrongPassword!", hashed) is False

    print(f" -> Plaintext: {password}")
    print(f" -> Hashed: {hashed[:20]}...")
    print(" -> PASSED! Password hashing & verification verified.")


def test_jwt_token_operations():
    print("[TEST 2] Testing JWT access token creation and decoding...")
    user_email = "driver@example.com"
    token_str = create_access_token(data={"sub": user_email})

    assert isinstance(token_str, str)
    assert len(token_str) > 0

    decoded = decode_access_token(token_str)
    assert decoded["sub"] == user_email
    assert "exp" in decoded
    assert "iat" in decoded

    token_obj = Token(access_token=token_str)
    assert token_obj.token_type == "bearer"

    print(f" -> Generated JWT Token: {token_str[:30]}...")
    print(f" -> Decoded Subject: {decoded['sub']}")
    print(" -> PASSED! JWT token operations verified.")


def test_user_pydantic_models():
    print("[TEST 3] Testing User Pydantic schemas and password exclusion...")
    raw_user = UserCreate(
        email="testuser@example.com",
        password="secret_password_123",
        full_name="Autonomous Driver",
    )
    assert raw_user.email == "testuser@example.com"

    now = datetime.now(timezone.utc)
    hashed_pwd = get_password_hash(raw_user.password)

    db_user = UserInDB(
        id="507f1f77bcf86cd799439011",
        email=raw_user.email,
        full_name=raw_user.full_name,
        hashed_password=hashed_pwd,
        created_at=now,
        updated_at=now,
    )
    assert db_user.hashed_password == hashed_pwd

    # Convert UserInDB to safe UserResponse (without hashed_password)
    user_resp = UserResponse(**db_user.model_dump())
    resp_dict = user_resp.model_dump()

    assert "hashed_password" not in resp_dict
    assert resp_dict["email"] == "testuser@example.com"
    assert resp_dict["id"] == "507f1f77bcf86cd799439011"

    print(f" -> UserResponse serialized payload: {resp_dict}")
    print(" -> PASSED! User Pydantic models & password exclusion verified.")


def run_all():
    print("====================================================")
    print("RUNNING T036 USER SECURITY SUITE")
    print("====================================================")
    test_password_hashing()
    test_jwt_token_operations()
    test_user_pydantic_models()
    print("====================================================")
    print("ALL T036 VERIFICATION TESTS PASSED SUCCESSFULLY!")
    print("====================================================")


if __name__ == "__main__":
    run_all()
