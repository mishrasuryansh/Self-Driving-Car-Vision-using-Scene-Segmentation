"""Application Configuration Settings Module.

Provides typed, centralized configuration parsing via Pydantic BaseSettings,
reading environment variables matching the T007 `.env.example` contract without hardcoding secrets.
"""

from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Centralized application settings and environment variable bindings."""

    # Application Information
    PROJECT_NAME: str = "Self-Driving Car Vision API"
    API_V1_STR: str = "/api/v1"
    VERSION: str = "1.0.0"
    ALLOWED_ORIGINS: List[str] = ["*"]

    # Service Ports
    FRONTEND_PORT: int = 3000
    BACKEND_PORT: int = 8000
    DB_PORT: int = 27017
    REDIS_PORT: int = 6379

    # Database & Cache Connections
    MONGODB_URI: str = "mongodb://admin:secretpassword@db:27017/self_driving_db?authSource=admin"
    MONGO_INITDB_ROOT_USERNAME: str = "admin"
    MONGO_INITDB_ROOT_PASSWORD: str = "secretpassword"
    MONGO_INITDB_DATABASE: str = "self_driving_db"
    REDIS_URL: str = "redis://redis:6379/0"
    CELERY_BROKER_URL: str = "redis://redis:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://redis:6379/0"

    # Security & Authentication
    JWT_SECRET: str = "change-this-to-a-secure-random-secret-key"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # Storage & Media Processing
    STORAGE_UPLOADS_PATH: str = "storage/uploads"
    STORAGE_OUTPUTS_PATH: str = "storage/outputs"
    MAX_IMAGE_SIZE_MB: int = 10
    MAX_VIDEO_SIZE_MB: int = 100
    MAX_VIDEO_DURATION_SECONDS: int = 60

    # Inference Engine & AI Models
    MODEL_WEIGHTS_PATH: str = ""
    MODEL_DEVICE: str = "cpu"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=True,
    )


# Instantiate settings once as a singleton
settings = Settings()

__all__ = ["Settings", "settings"]
