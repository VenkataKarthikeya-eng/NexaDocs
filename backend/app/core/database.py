import os
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

logger = logging.getLogger("nexadocs.database")

# Configure connection args based on database engine
connect_args = {}
if settings.DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

# Attempt primary database connection
try:
    engine = create_engine(
        settings.DATABASE_URL,
        connect_args=connect_args,
        pool_pre_ping=True
    )
    # Verify connection immediately
    with engine.connect() as conn:
        pass
    db_target = settings.DATABASE_URL.split('@')[-1] if '@' in settings.DATABASE_URL else settings.DATABASE_URL
    print(f"[Database] Successfully connected to database: {db_target}")
except Exception as e:
    logger.error(f"[Database] Connection to {settings.DATABASE_URL} failed: {e}")
    # In production, do NOT silently fall back to SQLite
    if settings.ENVIRONMENT == "production" or settings.DATABASE_URL.startswith("postgresql"):
        print(f"[Database] CRITICAL: PostgreSQL connection failed: {e}")
        # In non-production environments with PostgreSQL set, raise if strict
        if settings.ENVIRONMENT == "production":
            raise RuntimeError(f"Production database connection failed: {e}") from e
        else:
            print(f"[Database] Non-production PostgreSQL connection error: {e}")
            raise RuntimeError(f"Database connection error: {e}") from e

    # Explicit fallback only allowed for non-production without configured PostgreSQL
    sqlite_fallback_url = "sqlite:///./nexadocs.db"
    print(f"[Database] Falling back to local development SQLite: {sqlite_fallback_url}")
    settings.DATABASE_URL = sqlite_fallback_url
    connect_args = {"check_same_thread": False}
    engine = create_engine(
        settings.DATABASE_URL,
        connect_args=connect_args,
        pool_pre_ping=True
    )


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
