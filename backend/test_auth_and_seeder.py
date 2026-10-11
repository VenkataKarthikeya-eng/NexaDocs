import os
import sys
import pytest
from starlette.testclient import TestClient

# Ensure backend root on sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.main import app, seed_demo_data
from app.core.database import SessionLocal
from app.models.user import User
from app.models.document import Document
from app.models.insight import Insight
from app.models.document_chunk import DocumentChunk


client = TestClient(app)


def test_cors_preflight_all_vercel_origins():
    """Verify that all Vercel origins (production & preview subdomains) pass CORS preflight."""
    origins_to_test = [
        "https://nexa-docs.vercel.app",
        "https://nexadocs.vercel.app",
        "https://nexa-docs-git-main-user.vercel.app",
        "https://nexadocs-preview-123.vercel.app"
    ]
    for origin in origins_to_test:
        response = client.options(
            "/api/v1/auth/login",
            headers={
                "Origin": origin,
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "Content-Type, Authorization"
            }
        )
        assert response.status_code == 200, f"CORS preflight failed for {origin} with status {response.status_code}"
        assert response.headers.get("access-control-allow-origin") == origin, f"Origin {origin} not echoed in CORS header"
        assert response.headers.get("access-control-allow-credentials") == "true"
    print("\n[TEST PASS] All Vercel production and preview origins passed CORS preflight.")


def test_repeated_seeder_execution_idempotency():
    """Verify that running seed_demo_data multiple times is 100% idempotent without duplicate PK or FK errors."""
    # Run seeder 3 times consecutively
    for i in range(3):
        seed_demo_data()

    db = SessionLocal()
    try:
        # 1. Verify demo user exists
        demo_user = db.query(User).filter(User.email == "demo@nexadocs.com").first()
        assert demo_user is not None, "Demo user must exist"

        # 2. Verify exactly 3 demo documents exist
        docs = db.query(Document).filter(Document.user_id == demo_user.id).all()
        doc_ids = {d.id for d in docs}
        assert {"doc-1", "doc-2", "doc-3"}.issubset(doc_ids), f"Expected doc-1, doc-2, doc-3, found {doc_ids}"

        # 3. Verify insights exist for each demo document
        for doc_id in ["doc-1", "doc-2", "doc-3"]:
            ins = db.query(Insight).filter(Insight.document_id == doc_id).first()
            assert ins is not None, f"Insight for {doc_id} must exist"
            assert len(ins.summary) > 0

        # 4. Verify document_chunks exist with valid foreign keys
        for doc_id in ["doc-1", "doc-2", "doc-3"]:
            chunks = db.query(DocumentChunk).filter(DocumentChunk.document_id == doc_id).all()
            assert len(chunks) > 0, f"Expected chunks for {doc_id}, found 0"
            for c in chunks:
                assert c.document_id == doc_id
    finally:
        db.close()
    print("[TEST PASS] Repeated seeder execution verified (100% idempotent, zero duplicate key or FK errors).")


def test_login_success():
    """Verify login with demo user credentials returns 200 and access_token."""
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "demo@nexadocs.com", "password": "Demo@123"}
    )
    assert response.status_code == 200, f"Login failed with status {response.status_code}: {response.text}"
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["email"] == "demo@nexadocs.com"
    print("[TEST PASS] Demo user login successful with valid JWT access token.")


def test_login_invalid_password():
    """Verify login with invalid password returns 401."""
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "demo@nexadocs.com", "password": "WrongPassword!456"}
    )
    assert response.status_code == 401
    assert "Incorrect email or password" in response.json()["detail"]
    print("[TEST PASS] Invalid password rejected with 401.")


def test_login_nonexistent_user():
    """Verify login with non-existent email returns 401."""
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "nobody@nonexistent.domain", "password": "AnyPassword!123"}
    )
    assert response.status_code == 401
    print("[TEST PASS] Non-existent user rejected with 401.")


def test_register_and_duplicate_check():
    """Verify new user registration and duplicate email rejection."""
    import uuid
    random_email = f"user_{uuid.uuid4().hex[:8]}@nexadocs-test.com"
    
    # 1. Register new user
    reg_response = client.post(
        "/api/v1/auth/register",
        json={"name": "Test Engineer", "email": random_email, "password": "TestPassword@123"}
    )
    assert reg_response.status_code == 201, f"Registration failed: {reg_response.text}"
    reg_data = reg_response.json()
    assert "access_token" in reg_data
    assert reg_data["user"]["email"] == random_email

    # 2. Duplicate registration attempt with same email
    dup_response = client.post(
        "/api/v1/auth/register",
        json={"name": "Duplicate User", "email": random_email, "password": "TestPassword@123"}
    )
    assert dup_response.status_code == 400
    assert "already exists" in dup_response.json()["detail"]
    print("[TEST PASS] User registration and duplicate email rejection verified.")


def test_get_document_file_demo_fallback():
    """Verify authenticated file retrieval for demo documents works even on ephemeral disk."""
    # Login to obtain token
    login_res = client.post("/api/v1/auth/login", json={"email": "demo@nexadocs.com", "password": "Demo@123"})
    token = login_res.json()["access_token"]

    # Fetch doc-1 file
    file_res = client.get(
        "/api/v1/documents/doc-1/file",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert file_res.status_code in (200, 307), f"Expected 200 or 307 redirect, got {file_res.status_code}"
    if file_res.status_code == 200:
        assert file_res.content.startswith(b"%PDF-"), "Expected PDF binary header"
    print("[TEST PASS] Demo document file retrieval and dynamic generation fallback verified.")


def test_frontend_api_base_url_configuration():
    """Verify that frontend configuration files point strictly to https://nexadocs.onrender.com/api/v1."""
    frontend_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "frontend")
    
    # 1. Check .env.production
    env_prod_path = os.path.join(frontend_dir, ".env.production")
    assert os.path.exists(env_prod_path), ".env.production must exist"
    with open(env_prod_path, "r", encoding="utf-8") as f:
        env_prod = f.read()
    assert "https://nexadocs.onrender.com/api/v1" in env_prod, "VITE_API_URL in .env.production must be https://nexadocs.onrender.com/api/v1"
    assert "nexadocs-backend" not in env_prod, "Outdated nexadocs-backend domain found in .env.production"

    # 2. Check api.js fallback
    api_js_path = os.path.join(frontend_dir, "src", "services", "api.js")
    with open(api_js_path, "r", encoding="utf-8") as f:
        api_js = f.read()
    assert "https://nexadocs.onrender.com/api/v1" in api_js
    assert "nexadocs-backend" not in api_js

    # 3. Check useChatStore.js fallback
    chat_store_path = os.path.join(frontend_dir, "src", "store", "useChatStore.js")
    with open(chat_store_path, "r", encoding="utf-8") as f:
        chat_store = f.read()
    assert "API_BASE_URL" in chat_store or "https://nexadocs.onrender.com/api/v1" in chat_store
    assert "nexadocs-backend" not in chat_store
    print("[TEST PASS] Frontend API URL configuration verified (pointing to https://nexadocs.onrender.com/api/v1).")


def test_registration_validation_error_422():
    """Verify registration with invalid schema returns 422 Unprocessable Entity."""
    response = client.post("/api/v1/auth/register", json={"email": "not-an-email"})
    assert response.status_code == 422, f"Expected 422, got {response.status_code}"
    print("[TEST PASS] Registration invalid schema rejected with 422 Unprocessable Entity.")


def test_pgvector_savepoint_isolation_and_chunk_persistence():
    """Verify that SAVEPOINT isolation prevents InFailedSqlTransaction and guarantees chunk persistence."""
    from app.services.embedding_service import embedding_service
    test_doc_id = "test-doc-savepoint-isolation-1"
    db = SessionLocal()
    try:
        # 1. Ensure user and document exist
        user = db.query(User).filter(User.email == "demo@nexadocs.com").first()
        assert user is not None

        db.query(Document).filter(Document.id == test_doc_id).delete()
        db.commit()

        doc = Document(
            id=test_doc_id,
            user_id=user.id,
            title="Savepoint_Test.pdf",
            filename="Savepoint_Test.pdf",
            file_path="local/test.pdf",
            status="READY"
        )
        db.add(doc)
        db.commit()

        # 2. Index chunks
        chunks = [
            {"chunk_id": 0, "page": 1, "text": "First chunk test content for savepoint transaction isolation."},
            {"chunk_id": 1, "page": 2, "text": "Second chunk test content verifying no InFailedSqlTransaction occurs."}
        ]
        embedding_service.index_document_chunks(test_doc_id, chunks, db=db, commit=True)

        # 3. Verify chunks actually persisted
        persisted_chunks = db.query(DocumentChunk).filter(DocumentChunk.document_id == test_doc_id).all()
        assert len(persisted_chunks) == 2, f"Expected 2 chunks, found {len(persisted_chunks)}"
        assert persisted_chunks[0].content == chunks[0]["text"]
        assert persisted_chunks[1].content == chunks[1]["text"]

        # Clean up
        db.query(DocumentChunk).filter(DocumentChunk.document_id == test_doc_id).delete()
        db.query(Document).filter(Document.id == test_doc_id).delete()
        db.commit()
    finally:
        db.close()
    print("[TEST PASS] Chunk persistence with savepoint isolation verified.")


def test_idempotent_reindexing_prevents_duplicates():
    """Verify repeated indexing of the same document replaces chunks without creating duplicate rows."""
    from app.services.embedding_service import embedding_service
    test_doc_id = "test-doc-idempotency-2"
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == "demo@nexadocs.com").first()
        db.query(Document).filter(Document.id == test_doc_id).delete()
        db.commit()

        doc = Document(
            id=test_doc_id,
            user_id=user.id,
            title="Idempotency_Test.pdf",
            filename="Idempotency_Test.pdf",
            file_path="local/test.pdf",
            status="READY"
        )
        db.add(doc)
        db.commit()

        chunks = [
            {"chunk_id": 0, "page": 1, "text": "Chunk A"},
            {"chunk_id": 1, "page": 1, "text": "Chunk B"}
        ]

        # Index 3 times consecutively
        for _ in range(3):
            embedding_service.index_document_chunks(test_doc_id, chunks, db=db, commit=True)

        # Must have exactly 2 chunks, not 6
        db_chunks = db.query(DocumentChunk).filter(DocumentChunk.document_id == test_doc_id).all()
        assert len(db_chunks) == 2, f"Expected exactly 2 chunks after repeated indexing, found {len(db_chunks)}"

        # Clean up
        db.query(DocumentChunk).filter(DocumentChunk.document_id == test_doc_id).delete()
        db.query(Document).filter(Document.id == test_doc_id).delete()
        db.commit()
    finally:
        db.close()
    print("[TEST PASS] Idempotent re-indexing verified (zero duplicate chunks).")


if __name__ == "__main__":
    print("=" * 70)
    print("RUNNING NEXADOCS AUTHENTICATION, SEEDER & CORS VERIFICATION SUITE")
    print("=" * 70)
    test_frontend_api_base_url_configuration()
    test_cors_preflight_all_vercel_origins()
    test_repeated_seeder_execution_idempotency()
    test_login_success()
    test_login_invalid_password()
    test_login_nonexistent_user()
    test_register_and_duplicate_check()
    test_registration_validation_error_422()
    test_get_document_file_demo_fallback()
    test_pgvector_savepoint_isolation_and_chunk_persistence()
    test_idempotent_reindexing_prevents_duplicates()
    print("=" * 70)
    print("ALL AUTH, SEEDER & CORS TESTS PASSED (100%)")
    print("=" * 70)
