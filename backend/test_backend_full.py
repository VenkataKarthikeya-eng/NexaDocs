import sys
import os
import io
import time
import json
import uuid
from reportlab.pdfgen import canvas
from fastapi.testclient import TestClient

# Ensure app is importable
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.main import app
from app.core.config import settings
from app.core.database import SessionLocal
from app.models.user import User
from app.models.document import Document
from app.core.security import get_password_hash, verify_password
from app.services.embedding_service import embedding_service
from app.services.pdf_service import pdf_service

def generate_multi_page_test_pdf() -> bytes:
    """Generates a valid 3-page PDF with deterministic text on known physical pages."""
    buf = io.BytesIO()
    c = canvas.Canvas(buf)

    # Page 1: Financial Performance
    c.drawString(72, 750, "NexaDocs Q3 Financial Audit Report")
    c.drawString(72, 720, "Consolidated enterprise revenue reached $42.5 Million in Q3, a 24% YoY expansion.")
    c.drawString(72, 690, "Operating EBITDA margin expanded to 31.2%, exceeding analyst forecasts.")
    c.showPage()

    # Page 2: Technical Architecture
    c.drawString(72, 750, "NexaDocs Vector Retrieval Architecture")
    c.drawString(72, 720, "FAISS IndexFlatIP executes cosine vector similarity ranking in under 180ms.")
    c.drawString(72, 690, "Textual chunking preserves physical page metadata and complete semantic tokens.")
    c.showPage()

    # Page 3: Compliance & Security
    c.drawString(72, 750, "Regulatory Compliance & Security SLA")
    c.drawString(72, 720, "NexaDocs infrastructure satisfies SOC2 Type II compliance standards.")
    c.drawString(72, 690, "All customer document embeddings and vectors are encrypted at rest with AES-256.")
    c.showPage()

    c.save()
    return buf.getvalue()

def generate_image_only_pdf() -> bytes:
    """Generates a PDF with an empty page (simulating scanned document without text layer)."""
    buf = io.BytesIO()
    c = canvas.Canvas(buf)
    # Draw blank rectangle simulating image without text
    c.rect(50, 50, 500, 700, fill=0)
    c.showPage()
    c.save()
    return buf.getvalue()

def run_all_tests():
    print("=" * 70)
    print("  NexaDocs End-to-End Enterprise Backend Verification Suite")
    print(f"  Target Database: {settings.DATABASE_URL.split('@')[-1] if '@' in settings.DATABASE_URL else settings.DATABASE_URL}")
    print(f"  Gemini Primary Model: {settings.GEMINI_MODEL}")
    print("=" * 70)

    client = TestClient(app)

    # -------------------------------------------------------------
    # 1. Health & Database Readiness
    # -------------------------------------------------------------
    for endpoint in ["/health", "/api/health", "/api/v1/health"]:
        res = client.get(endpoint)
        assert res.status_code == 200, f"Health check failed at {endpoint}: {res.text}"
        data = res.json()
        assert data["database"] == "connected", f"Database not connected at {endpoint}"
        assert data["status"] == "ok"
    print("[PASS] 1. Health & Database Readiness Verified on PostgreSQL.")

    # -------------------------------------------------------------
    # 2. Authentication: Argon2id Hashing & Registration
    # -------------------------------------------------------------
    test_user_a_email = f"user.a.{int(time.time())}@enterprise.com"
    pwd_a = "StrongPassword@2026!"
    reg_a = client.post("/api/v1/auth/register", json={
        "name": "Alice Enterprise",
        "email": test_user_a_email,
        "password": pwd_a
    })
    assert reg_a.status_code == 201, f"Registration failed: {reg_a.text}"
    token_a = reg_a.json()["access_token"]
    assert token_a, "Token A missing"
    headers_a = {"Authorization": f"Bearer {token_a}"}

    # Verify that stored hash is Argon2id
    db = SessionLocal()
    user_db_a = db.query(User).filter(User.email == test_user_a_email).first()
    assert user_db_a is not None
    assert user_db_a.password_hash.startswith("$argon2id"), f"Password hash is not Argon2id: {user_db_a.password_hash[:20]}"
    db.close()
    print("[PASS] 2. User Registration & Argon2id Hashing Verified.")

    # -------------------------------------------------------------
    # 3. Authentication: Login & Legacy Bcrypt Backward Compatibility
    # -------------------------------------------------------------
    login_a = client.post("/api/v1/auth/login", json={"email": test_user_a_email, "password": pwd_a})
    assert login_a.status_code == 200, f"Login failed: {login_a.text}"
    assert login_a.json()["access_token"]

    # Test legacy bcrypt backward compatibility and auto-upgrade
    test_bcrypt_email = f"legacy.bcrypt.{int(time.time())}@enterprise.com"
    import bcrypt
    bcrypt_salt = bcrypt.gensalt()
    legacy_hash = bcrypt.hashpw(b"LegacyPassword123!", bcrypt_salt).decode("utf-8")
    
    db = SessionLocal()
    legacy_user = User(
        name="Legacy User",
        email=test_bcrypt_email,
        password_hash=legacy_hash,
        role="Legacy Lead",
        plan="Enterprise Pro"
    )
    db.add(legacy_user)
    db.commit()
    db.close()

    # Login with legacy user: must succeed AND automatically upgrade hash to Argon2id
    legacy_login = client.post("/api/v1/auth/login", json={"email": test_bcrypt_email, "password": "LegacyPassword123!"})
    assert legacy_login.status_code == 200, "Legacy bcrypt login failed"

    db = SessionLocal()
    upgraded_user = db.query(User).filter(User.email == test_bcrypt_email).first()
    assert upgraded_user.password_hash.startswith("$argon2id"), "Legacy bcrypt hash was not upgraded to Argon2id"
    db.delete(upgraded_user)
    db.commit()
    db.close()
    print("[PASS] 3. Login & Transparent Bcrypt -> Argon2id Migration Verified.")

    # -------------------------------------------------------------
    # 4. Token Security: Invalid & Expired Token Rejection
    # -------------------------------------------------------------
    invalid_res = client.get("/api/v1/auth/me", headers={"Authorization": "Bearer invalid.token.payload"})
    assert invalid_res.status_code == 401, f"Expected 401 on invalid token, got {invalid_res.status_code}"

    no_auth_res = client.get("/api/v1/auth/me")
    assert no_auth_res.status_code == 401, f"Expected 401 on missing auth, got {no_auth_res.status_code}"
    print("[PASS] 4. Token Security & Unauthorized Rejection Verified.")

    # -------------------------------------------------------------
    # 5. Multi-Tenant Authorization & IDOR Protection
    # -------------------------------------------------------------
    test_user_b_email = f"user.b.{int(time.time())}@enterprise.com"
    reg_b = client.post("/api/v1/auth/register", json={
        "name": "Bob Enterprise",
        "email": test_user_b_email,
        "password": "StrongPassword@2026!"
    })
    assert reg_b.status_code == 201
    headers_b = {"Authorization": f"Bearer {reg_b.json()['access_token']}"}

    # -------------------------------------------------------------
    # 6. PDF Validation: Empty, Corrupt, and Scanned Documents
    # -------------------------------------------------------------
    # Empty file
    empty_upload = client.post(
        "/api/v1/documents/upload",
        headers=headers_a,
        files={"file": ("empty.pdf", b"", "application/pdf")}
    )
    assert empty_upload.status_code == 400, "Empty PDF was not rejected"

    # Corrupt non-PDF bytes
    corrupt_upload = client.post(
        "/api/v1/documents/upload",
        headers=headers_a,
        files={"file": ("corrupt.pdf", b"This is plain text pretending to be a PDF", "application/pdf")}
    )
    assert corrupt_upload.status_code == 400, "Corrupt PDF was not rejected"

    # Scanned PDF without text layer
    scanned_bytes = generate_image_only_pdf()
    scanned_upload = client.post(
        "/api/v1/documents/upload",
        headers=headers_a,
        files={"file": ("scanned_blank.pdf", scanned_bytes, "application/pdf")}
    )
    assert scanned_upload.status_code == 400, f"Image-only PDF should be rejected: {scanned_upload.text}"
    assert "searchable text" in scanned_upload.json()["detail"].lower() or "ocr" in scanned_upload.json()["detail"].lower()
    print("[PASS] 6. PDF Validation: Empty, Corrupt & Scanned Rejection Verified.")

    # -------------------------------------------------------------
    # 7. Valid Multi-Page PDF Upload & Extraction
    # -------------------------------------------------------------
    valid_pdf_bytes = generate_multi_page_test_pdf()
    upload_res = client.post(
        "/api/v1/documents/upload",
        headers=headers_a,
        files={"file": ("Enterprise_Q3_Audit.pdf", valid_pdf_bytes, "application/pdf")}
    )
    assert upload_res.status_code == 201, f"Valid PDF upload failed: {upload_res.text}"
    doc_data = upload_res.json()
    doc_id = doc_data["id"]
    assert doc_data["pageCount"] == 3, f"Expected 3 pages, got {doc_data['pageCount']}"
    assert doc_data["chunkCount"] >= 3, f"Expected >= 3 chunks, got {doc_data['chunkCount']}"
    assert doc_data["status"] == "Ready"
    print(f"[PASS] 7. Valid PDF Upload & PyMuPDF Extraction Verified. Doc ID: {doc_id}")

    # -------------------------------------------------------------
    # 8. Multi-Tenant Isolation: User B Cannot Access User A's Document
    # -------------------------------------------------------------
    idor_get = client.get(f"/api/v1/documents/{doc_id}", headers=headers_b)
    assert idor_get.status_code == 404, f"IDOR vulnerability! User B accessed User A's doc: {idor_get.status_code}"

    idor_file = client.get(f"/api/v1/documents/{doc_id}/file", headers=headers_b)
    assert idor_file.status_code == 404, "User B accessed User A's file download"

    idor_chat = client.post(
        "/api/v1/ai/chat",
        headers=headers_b,
        json={"document_id": doc_id, "question": "What is the revenue?"}
    )
    assert idor_chat.status_code == 404, "User B executed AI query on User A's doc"
    print("[PASS] 8. Multi-Tenant User Isolation (IDOR Protection) Verified.")

    # -------------------------------------------------------------
    # 9. Dense Semantic Embeddings & FAISS Vector Search
    # -------------------------------------------------------------
    # Query for financial metrics on Page 1
    chunks_revenue = embedding_service.search_similar_chunks(doc_id, "enterprise revenue growth", top_k=2)
    assert len(chunks_revenue) > 0
    top_chunk = chunks_revenue[0]
    assert top_chunk["page"] == 1, f"Expected Page 1 for revenue query, got Page {top_chunk['page']}"
    assert "42.5" in top_chunk["text"]
    assert top_chunk["score"] > 0.25, f"Expected genuine similarity score, got {top_chunk['score']}"

    # Query for compliance on Page 3
    chunks_soc = embedding_service.search_similar_chunks(doc_id, "SOC2 compliance security standard", top_k=2)
    assert len(chunks_soc) > 0
    top_soc = chunks_soc[0]
    assert top_soc["page"] == 3, f"Expected Page 3 for SOC2 query, got Page {top_soc['page']}"
    assert "SOC2" in top_soc["text"]
    print("[PASS] 9. Dense Semantic Embeddings & FAISS Vector Search Verified.")

    # -------------------------------------------------------------
    # 10. Accurate RAG Answering with Verified Page Citations
    # -------------------------------------------------------------
    chat_req = {
        "document_id": doc_id,
        "question": "What is the enterprise revenue and EBITDA margin reported?"
    }
    chat_res = client.post("/api/v1/ai/chat", headers=headers_a, json=chat_req)
    assert chat_res.status_code == 200, f"AI Chat failed: {chat_res.text}"
    ans_data = chat_res.json()
    assert len(ans_data["sources"]) > 0, "No sources returned"
    first_citation = ans_data["sources"][0]
    assert first_citation["page"] == 1, f"Expected Citation Page 1, got Page {first_citation['page']}"
    assert first_citation["relevance_score"] > 0.2, "Relevance score was zero or invalid"
    assert "42.5" in ans_data["answer"]
    print("[PASS] 10. Evidence-Grounded RAG Answer & Physical Page 1 Citation Verified.")

    # -------------------------------------------------------------
    # 11. Honest Abstention on Questions Without Evidence
    # -------------------------------------------------------------
    abstain_req = {
        "document_id": doc_id,
        "question": "What is the average temperature on the surface of Neptune?"
    }
    abstain_res = client.post("/api/v1/ai/chat", headers=headers_a, json=abstain_req)
    assert abstain_res.status_code == 200
    abstain_data = abstain_res.json()
    # Must abstain honestly and have 0 sources!
    assert len(abstain_data["sources"]) == 0, f"Expected 0 sources for out-of-scope query, got: {abstain_data['sources']}"
    assert any(phrase in abstain_data["answer"].lower() for phrase in ["not contain", "not found", "sufficient evidence"])
    print("[PASS] 11. Honest Abstention Without Hallucination Verified.")

    # -------------------------------------------------------------
    # 12. True Server-Sent Events (SSE) Streaming
    # -------------------------------------------------------------
    stream_req = {
        "document_id": doc_id,
        "question": "What security compliance standard does NexaDocs satisfy?"
    }
    stream_res = client.post("/api/v1/ai/chat/stream", headers=headers_a, json=stream_req)
    assert stream_res.status_code == 200
    assert "text/event-stream" in stream_res.headers.get("content-type", "")
    stream_body = stream_res.text
    assert "data: " in stream_body
    assert '"type": "start"' in stream_body
    assert '"type": "token"' in stream_body
    assert '"type": "done"' in stream_body
    print("[PASS] 12. Real Server-Sent Events (SSE) Streaming Verified.")

    # -------------------------------------------------------------
    # 13. Chat History & Multi-Tenant Isolation
    # -------------------------------------------------------------
    hist_res = client.get(f"/api/v1/ai/chat/history/{doc_id}", headers=headers_a)
    assert hist_res.status_code == 200
    records = hist_res.json()
    assert len(records) >= 2, f"Expected at least 2 chat history records, got {len(records)}"

    # User B cannot access User A's chat history
    hist_b = client.get(f"/api/v1/ai/chat/history/{doc_id}", headers=headers_b)
    assert hist_b.status_code == 404, "User B accessed User A's chat history"
    print("[PASS] 13. Chat History & Authorization Isolation Verified.")

    # -------------------------------------------------------------
    # 14. Vector Index Persistence across Server Restart
    # -------------------------------------------------------------
    # Clear in-memory vector cache completely to simulate backend shutdown
    embedding_service.doc_chunks.clear()
    embedding_service.faiss_indices.clear()
    assert doc_id not in embedding_service.doc_chunks

    # Query again: must load .faiss and chunks.json from disk
    reloaded_chunks = embedding_service.search_similar_chunks(doc_id, "SOC2 compliance", top_k=2)
    assert len(reloaded_chunks) > 0, "Failed to reload index from persistent disk storage"
    assert doc_id in embedding_service.doc_chunks, "Cache was not restored from disk"
    print("[PASS] 14. FAISS Vector Persistence Across Restart Verified.")

    # -------------------------------------------------------------
    # 15. Clean Cascading Deletion & Storage Cleanup
    # -------------------------------------------------------------
    del_res = client.delete(f"/api/v1/documents/{doc_id}", headers=headers_a)
    assert del_res.status_code == 204, f"Delete failed: {del_res.status_code}"

    # Verify document is gone from DB
    get_after_del = client.get(f"/api/v1/documents/{doc_id}", headers=headers_a)
    assert get_after_del.status_code == 404

    # Verify vector index is purged
    assert doc_id not in embedding_service.doc_chunks
    assert not os.path.exists(os.path.join(embedding_service.indices_dir, f"{doc_id}.faiss"))
    assert not os.path.exists(os.path.join(embedding_service.indices_dir, f"{doc_id}_chunks.json"))
    print("[PASS] 15. Document Deletion, Storage & Vector Purge Verified.")

    # Clean up test users
    db = SessionLocal()
    for email in [test_user_a_email, test_user_b_email]:
        u = db.query(User).filter(User.email == email).first()
        if u:
            db.delete(u)
    db.commit()
    db.close()

    print("=" * 70)
    print("  ALL 15 COMPREHENSIVE END-TO-END VERIFICATION TESTS PASSED!")
    print("=" * 70)

def test_full_nexadocs_production_suite():
    run_all_tests()

if __name__ == "__main__":
    run_all_tests()

