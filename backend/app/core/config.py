import os
import secrets
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

ENV_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".env")

class Settings(BaseSettings):
    PROJECT_NAME: str = "NexaDocs"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = "development"
    
    # Secure JWT Secret Management
    JWT_SECRET: str = "nexadocs-enterprise-production-secure-jwt-key-2026-v1"
    SECRET_KEY: str = ""
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours

    # Database: Render PostgreSQL Production & Local SQLite Fallback
    DATABASE_URL: str = ""

    # Storage & Uploads Configuration (Local vs Neon S3-compatible Object Storage)
    STORAGE_TYPE: str = "LOCAL" # LOCAL, S3
    UPLOAD_DIR: str = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "uploads")
    FAISS_INDEX_PATH: str = ""
    DEBUG: bool = False

    # Neon / S3-Compatible Object Storage
    S3_ENDPOINT_URL: str = ""
    S3_BUCKET_NAME: str = "nexadocs-files"
    S3_REGION: str = "us-east-2"
    S3_ACCESS_KEY_ID: str = ""
    S3_SECRET_ACCESS_KEY: str = ""
    S3_PRESIGNED_EXPIRATION_SECONDS: int = 3600

    # Vector Storage & Remote Embedding Configuration
    VECTOR_STORAGE_TYPE: str = "POSTGRES" # POSTGRES, FAISS
    EMBEDDING_PROVIDER: str = "GEMINI"    # GEMINI (Production lightweight, <80MB RAM), LOCAL (SentenceTransformers)
    GEMINI_EMBEDDING_MODEL: str = "models/gemini-embedding-001"
    EMBEDDING_DIMENSION: int = 768

    # AI Config (Google Gemini Integration)
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-flash-lite-latest"
    GEMINI_FALLBACK_MODELS: list = ["gemini-3.5-flash", "gemini-flash-latest"]
    OPENAI_API_KEY: str = ""

    # CORS Allowed Origins
    CORS_ORIGINS: list = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:4173",
        "https://nexa-docs.vercel.app",
        "https://nexadocs.vercel.app",
        "https://nexadocs.onrender.com",
        "https://nexadocs-api.onrender.com"
    ]

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v):
        if isinstance(v, str):
            if v.startswith("[") and v.endswith("]"):
                import json
                try:
                    return json.loads(v)
                except Exception:
                    pass
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v

    model_config = SettingsConfigDict(
        env_file=ENV_PATH if os.path.exists(ENV_PATH) else None,
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=True
    )

settings = Settings()

# Support SECRET_KEY alias for JWT_SECRET
if settings.SECRET_KEY:
    settings.JWT_SECRET = settings.SECRET_KEY

# 1. Fallback JWT secret ensure at least 32 chars
if not settings.JWT_SECRET or len(settings.JWT_SECRET) < 32:
    settings.JWT_SECRET = "nexadocs-enterprise-production-secure-jwt-key-2026-v1"

# 2. Render & Neon PostgreSQL URL Normalization (postgres:// -> postgresql://)
if settings.DATABASE_URL.startswith("postgres://"):
    settings.DATABASE_URL = settings.DATABASE_URL.replace("postgres://", "postgresql://", 1)
elif settings.DATABASE_URL.startswith("postgres+psycopg://"):
    settings.DATABASE_URL = settings.DATABASE_URL.replace("postgres+psycopg://", "postgresql+psycopg://", 1)
elif settings.DATABASE_URL.startswith("postgres+psycopg2://"):
    settings.DATABASE_URL = settings.DATABASE_URL.replace("postgres+psycopg2://", "postgresql+psycopg2://", 1)

# Default to SQLite for local development only if no DATABASE_URL is provided
if not settings.DATABASE_URL:
    settings.DATABASE_URL = "sqlite:///./nexadocs.db"

# S3 standard AWS environment variable fallbacks
if not settings.S3_ENDPOINT_URL and os.environ.get("AWS_ENDPOINT_URL"):
    settings.S3_ENDPOINT_URL = os.environ["AWS_ENDPOINT_URL"]
if not settings.S3_ACCESS_KEY_ID and os.environ.get("AWS_ACCESS_KEY_ID"):
    settings.S3_ACCESS_KEY_ID = os.environ["AWS_ACCESS_KEY_ID"]
if not settings.S3_SECRET_ACCESS_KEY and os.environ.get("AWS_SECRET_ACCESS_KEY"):
    settings.S3_SECRET_ACCESS_KEY = os.environ["AWS_SECRET_ACCESS_KEY"]
if not settings.S3_BUCKET_NAME and os.environ.get("AWS_S3_BUCKET"):
    settings.S3_BUCKET_NAME = os.environ["AWS_S3_BUCKET"]
if not settings.S3_REGION and os.environ.get("AWS_REGION"):
    settings.S3_REGION = os.environ["AWS_REGION"]

# Ensure local upload directory exists
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

