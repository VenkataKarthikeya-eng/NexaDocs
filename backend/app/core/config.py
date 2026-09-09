import os
import secrets
from pydantic_settings import BaseSettings, SettingsConfigDict

ENV_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".env")

class Settings(BaseSettings):
    PROJECT_NAME: str = "NexaDocs"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = "development"
    
    # Secure JWT Secret Management
    JWT_SECRET: str = "nexadocs-enterprise-production-secure-jwt-key-2026-v1"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours

    # Database: Render PostgreSQL Production & Local SQLite Fallback
    DATABASE_URL: str = ""

    # Storage & Uploads Configuration
    STORAGE_TYPE: str = "LOCAL" # LOCAL, S3, CLOUDINARY
    UPLOAD_DIR: str = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "uploads")

    # AI Config
    OPENAI_API_KEY: str = ""

    # CORS Allowed Origins
    CORS_ORIGINS: list = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "https://nexadocs.vercel.app"
    ]

    model_config = SettingsConfigDict(
        env_file=ENV_PATH if os.path.exists(ENV_PATH) else None,
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=True
    )

settings = Settings()

# 1. Fallback JWT secret ensure at least 32 chars
if not settings.JWT_SECRET or len(settings.JWT_SECRET) < 32:
    settings.JWT_SECRET = "nexadocs-enterprise-production-secure-jwt-key-2026-v1"

# 2. Render PostgreSQL URL Normalization (postgres:// -> postgresql://)
if settings.DATABASE_URL.startswith("postgres://"):
    settings.DATABASE_URL = settings.DATABASE_URL.replace("postgres://", "postgresql://", 1)

# Default to SQLite for local development if no DATABASE_URL is provided
if not settings.DATABASE_URL:
    settings.DATABASE_URL = "sqlite:///./nexadocs.db"

# Ensure local upload directory exists
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
