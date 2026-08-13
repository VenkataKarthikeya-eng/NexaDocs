import os
import secrets
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "NexaDocs"
    API_V1_STR: str = "/api"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    
    # Secure JWT Secret Management
    # Auto-generate secure 64-char random hex secret if omitted or hardcoded default
    JWT_SECRET: str = os.getenv("JWT_SECRET", "")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours

    # Database: Render PostgreSQL Production & Local SQLite Fallback
    DATABASE_URL: str = os.getenv("DATABASE_URL", "")

    # Storage & Uploads Configuration
    STORAGE_TYPE: str = os.getenv("STORAGE_TYPE", "LOCAL") # LOCAL, S3, CLOUDINARY
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "uploads"))

    # AI Config
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")

    # CORS Allowed Origins
    CORS_ORIGINS: list = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "https://nexadocs.vercel.app"
    ]

    class Config:
        case_sensitive = True

settings = Settings()

# 1. Fallback / Random JWT secret generation to prevent hardcoded secrets
if not settings.JWT_SECRET or "nexadocs-super-secret" in settings.JWT_SECRET or len(settings.JWT_SECRET) < 32:
    settings.JWT_SECRET = secrets.token_hex(32)

# 2. Render PostgreSQL URL Normalization (postgres:// -> postgresql://)
if settings.DATABASE_URL.startswith("postgres://"):
    settings.DATABASE_URL = settings.DATABASE_URL.replace("postgres://", "postgresql://", 1)

# Default to SQLite for local development if no DATABASE_URL is provided
if not settings.DATABASE_URL:
    settings.DATABASE_URL = "sqlite:///./nexadocs.db"

# Ensure local upload directory exists
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
