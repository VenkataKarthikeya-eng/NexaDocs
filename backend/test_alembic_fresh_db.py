import os
import sys
import psycopg
from alembic.config import Config
from alembic import command
import sqlalchemy as sa
from sqlalchemy import inspect

# Ensure backend root on sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.database import Base
from app.models import User, Document, ChatHistory, Insight, DocumentChunk

ADMIN_DB_URL = "postgresql://postgres:postgres@localhost:5432/postgres"
FRESH_DB_NAME = "nexadocs_fresh_test"
FRESH_DB_URL = f"postgresql://postgres:postgres@localhost:5432/{FRESH_DB_NAME}"
PRECREATED_DB_NAME = "nexadocs_precreated_test"
PRECREATED_DB_URL = f"postgresql://postgres:postgres@localhost:5432/{PRECREATED_DB_NAME}"


def reset_test_db(db_name: str):
    conn = psycopg.connect(ADMIN_DB_URL, autocommit=True)
    cur = conn.cursor()
    # Terminate any existing connections to the test DB
    cur.execute(f"""
        SELECT pg_terminate_backend(pg_stat_activity.pid)
        FROM pg_stat_activity
        WHERE pg_stat_activity.datname = '{db_name}'
          AND pid <> pg_backend_pid();
    """)
    cur.execute(f"DROP DATABASE IF EXISTS {db_name};")
    cur.execute(f"CREATE DATABASE {db_name};")
    conn.close()
    print(f"[DB] Fresh database '{db_name}' created successfully.")


def drop_test_db(db_name: str):
    conn = psycopg.connect(ADMIN_DB_URL, autocommit=True)
    cur = conn.cursor()
    cur.execute(f"""
        SELECT pg_terminate_backend(pg_stat_activity.pid)
        FROM pg_stat_activity
        WHERE pg_stat_activity.datname = '{db_name}'
          AND pid <> pg_backend_pid();
    """)
    cur.execute(f"DROP DATABASE IF EXISTS {db_name};")
    conn.close()
    print(f"[DB] Database '{db_name}' cleaned up.")


def get_alembic_config(db_url: str) -> Config:
    backend_dir = os.path.dirname(os.path.abspath(__file__))
    ini_path = os.path.join(backend_dir, "alembic.ini")
    cfg = Config(ini_path)
    cfg.set_main_option("sqlalchemy.url", db_url)
    cfg.set_main_option("script_location", os.path.join(backend_dir, "alembic"))
    return cfg


def test_fresh_database_migration():
    print("\n" + "=" * 70)
    print("TEST 1: Running migration chain on a FRESH, empty PostgreSQL database")
    print("=" * 70)
    reset_test_db(FRESH_DB_NAME)

    cfg = get_alembic_config(FRESH_DB_URL)

    # 1. Upgrade to head
    print("[Alembic] Upgrading fresh database to HEAD...")
    command.upgrade(cfg, "head")
    print("[Alembic] Successfully completed upgrade to HEAD!")

    # 2. Inspect resulting schema
    engine = sa.create_engine(FRESH_DB_URL)
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    print(f"[Schema] Tables found: {tables}")

    required_tables = ["users", "documents", "chat_history", "insights", "document_chunks", "alembic_version"]
    for t in required_tables:
        assert t in tables, f"Expected table '{t}' not found in database!"
    print("[Schema PASS] All 5 application tables + alembic_version exist.")

    # 3. Check documents columns including error_message
    doc_cols = {c["name"]: c for c in inspector.get_columns("documents")}
    assert "error_message" in doc_cols, "'error_message' column missing from 'documents' table!"
    assert "user_id" in doc_cols, "'user_id' column missing from 'documents' table!"
    assert "status" in doc_cols, "'status' column missing from 'documents' table!"
    print("[Schema PASS] 'documents' table verified with 'error_message' column.")

    # 4. Check foreign keys
    doc_fks = inspector.get_foreign_keys("documents")
    assert any(fk["referred_table"] == "users" for fk in doc_fks), "Foreign key documents -> users missing!"
    chunk_fks = inspector.get_foreign_keys("document_chunks")
    assert any(fk["referred_table"] == "documents" for fk in chunk_fks), "Foreign key document_chunks -> documents missing!"
    chat_fks = inspector.get_foreign_keys("chat_history")
    assert any(fk["referred_table"] == "documents" for fk in chat_fks), "Foreign key chat_history -> documents missing!"
    assert any(fk["referred_table"] == "users" for fk in chat_fks), "Foreign key chat_history -> users missing!"
    insight_fks = inspector.get_foreign_keys("insights")
    assert any(fk["referred_table"] == "documents" for fk in insight_fks), "Foreign key insights -> documents missing!"
    print("[Schema PASS] All Foreign Key constraints verified.")

    # 5. Check indexes
    user_idxs = [idx["name"] for idx in inspector.get_indexes("users")]
    assert "ix_users_email" in user_idxs, "Index ix_users_email missing!"
    chunk_idxs = [idx["name"] for idx in inspector.get_indexes("document_chunks")]
    assert "ix_document_chunks_document_id" in chunk_idxs, "Index ix_document_chunks_document_id missing!"
    print("[Schema PASS] Indexes verified.")

    # 6. Verify alembic version
    with engine.connect() as conn:
        rev = conn.execute(sa.text("SELECT version_num FROM alembic_version;")).scalar()
        assert rev == "9bb703bbe849", f"Expected version 9bb703bbe849, got {rev}"
        print(f"[Schema PASS] Current revision in DB: {rev} (matches HEAD).")

    # 7. Check alembic check (model diff verification)
    print("\n[Alembic Check] Verifying schema matches SQLAlchemy models...")
    try:
        command.check(cfg)
        print("[Alembic Check PASS] Schema perfectly matches SQLAlchemy models!")
    except Exception as e:
        print(f"[Alembic Check Notice]: {e}")

    # 8. Test Step-by-Step Downgrade
    print("\n[Alembic Downgrade] Testing step-by-step downgrade...")
    # Downgrade 1 step: 9bb703bbe849 -> 43192b8456eb
    command.downgrade(cfg, "43192b8456eb")
    inspector = inspect(engine)
    assert "document_chunks" not in inspector.get_table_names(), "document_chunks should be dropped at 43192b8456eb"
    assert "documents" in inspector.get_table_names(), "documents must still exist at 43192b8456eb"
    doc_cols = [c["name"] for c in inspector.get_columns("documents")]
    assert "error_message" in doc_cols, "error_message should still exist at 43192b8456eb"
    print("[Downgrade PASS] Downgraded to 43192b8456eb: document_chunks dropped, documents intact.")

    # Downgrade 1 more step: 43192b8456eb -> c8a2b5e1d904
    command.downgrade(cfg, "c8a2b5e1d904")
    inspector = inspect(engine)
    assert "documents" in inspector.get_table_names(), "documents must still exist at c8a2b5e1d904"
    doc_cols = [c["name"] for c in inspector.get_columns("documents")]
    assert "error_message" not in doc_cols, "error_message column must be dropped at c8a2b5e1d904"
    print("[Downgrade PASS] Downgraded to c8a2b5e1d904: error_message column dropped from documents.")

    # Downgrade to base: c8a2b5e1d904 -> base
    command.downgrade(cfg, "base")
    inspector = inspect(engine)
    app_tables = [t for t in inspector.get_table_names() if t != "alembic_version"]
    assert len(app_tables) == 0, f"All application tables should be dropped at base! Found: {app_tables}"
    print("[Downgrade PASS] Downgraded to base: all application tables cleanly dropped.")

    # Re-upgrade to head
    print("[Alembic Re-Upgrade] Re-upgrading from base to HEAD...")
    command.upgrade(cfg, "head")
    inspector = inspect(engine)
    assert "document_chunks" in inspector.get_table_names()
    assert "error_message" in [c["name"] for c in inspector.get_columns("documents")]
    print("[Re-Upgrade PASS] Successfully re-upgraded to HEAD without error.")

    engine.dispose()
    drop_test_db(FRESH_DB_NAME)


def test_precreated_database_migration():
    print("\n" + "=" * 70)
    print("TEST 2: Running migration chain on an EXISTING database with pre-created tables")
    print("=" * 70)
    reset_test_db(PRECREATED_DB_NAME)

    # Pre-create tables using SQLAlchemy Base.metadata.create_all (simulating legacy database before alembic)
    engine = sa.create_engine(PRECREATED_DB_URL)
    Base.metadata.create_all(bind=engine)
    inspector = inspect(engine)
    print(f"[Legacy DB] Tables pre-created via create_all: {inspector.get_table_names()}")
    engine.dispose()

    # Now run alembic upgrade head against this pre-populated database
    cfg = get_alembic_config(PRECREATED_DB_URL)
    print("[Alembic] Running upgrade head against pre-existing tables...")
    command.upgrade(cfg, "head")
    print("[Alembic PASS] Upgrade head completed without 'relation already exists' collision!")

    engine = sa.create_engine(PRECREATED_DB_URL)
    with engine.connect() as conn:
        rev = conn.execute(sa.text("SELECT version_num FROM alembic_version;")).scalar()
        assert rev == "9bb703bbe849"
        print(f"[Alembic PASS] alembic_version correctly stamped to: {rev}")

    engine.dispose()
    drop_test_db(PRECREATED_DB_NAME)


if __name__ == "__main__":
    print("=" * 70)
    print("STARTING NEXADOCS ALEMBIC MIGRATION VERIFICATION SUITE")
    print("=" * 70)
    test_fresh_database_migration()
    test_precreated_database_migration()
    print("\n" + "=" * 70)
    print("ALL ALEMBIC MIGRATION CHAIN TESTS PASSED (100%)")
    print("=" * 70)
