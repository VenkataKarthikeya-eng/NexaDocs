import sys
import os
import time
import json
from fastapi.testclient import TestClient

# Ensure app package is importable
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.main import app
from app.services.embedding_service import embedding_service
from app.core.config import settings

def run_tests():
    print("=== NexaDocs FastAPI Backend Production Readiness Test Suite ===")
    print(f"[*] Database URL: {settings.DATABASE_URL}")
    client = TestClient(app)

    # 1. Health Checks (Root, /health, /api/health, /api/v1/health)
    for path in ["/health", "/api/health", "/api/v1/health"]:
        res = client.get(path)
        assert res.status_code == 200, f"Health check failed on {path}: {res.text}"
    print("[OK] Health Checks PASSED across /health, /api/health, and /api/v1/health.")

    # 2. Demo User Login (Seeded in PostgreSQL)
    demo_login = client.post("/api/v1/auth/login", json={"email": "demo@nexadocs.com", "password": "Demo@123"})
    assert demo_login.status_code == 200, f"Demo login failed: {demo_login.text}"
    demo_token = demo_login.json()["access_token"]
    assert demo_token, "Token missing from demo login"
    print("[OK] Demo User Login PASSED on PostgreSQL (demo@nexadocs.com).")

    # 3. User Registration via /api/v1
    test_email = f"alex.mercer.{int(time.time())}@enterprise.com"
    reg_payload = {
        "name": "Alex Mercer",
        "email": test_email,
        "password": "SecurePassword123!"
    }
    reg_res = client.post("/api/v1/auth/register", json=reg_payload)
    assert reg_res.status_code == 201, f"Register failed: {reg_res.text}"
    token_data = reg_res.json()
    token = token_data["access_token"]
    assert token, "Token missing from registration response"
    headers = {"Authorization": f"Bearer {token}"}
    print("[OK] User Registration PASSED via /api/v1.")

    # 4. User Login via /api/v1
    login_res = client.post("/api/v1/auth/login", json={"email": test_email, "password": "SecurePassword123!"})
    assert login_res.status_code == 200, f"Login failed: {login_res.text}"
    print("[OK] User Login PASSED via /api/v1.")

    # 5. Access Protected Route (/api/v1/auth/me & /api/auth/me)
    me_res = client.get("/api/v1/auth/me", headers=headers)
    assert me_res.status_code == 200, f"Protected route failed: {me_res.text}"
    user_info = me_res.json()
    assert user_info["email"] == test_email
    me_legacy = client.get("/api/auth/me", headers=headers)
    assert me_legacy.status_code == 200, "Legacy route /api/auth/me failed"
    print(f"[OK] Protected Route GET /api/v1/auth/me and /api/auth/me PASSED for user: {user_info['name']}.")

    # 6. User Profile Update via PUT /api/v1/users/profile
    update_res = client.put("/api/v1/users/profile", headers=headers, json={"role": "Lead Architect", "name": "Alexander Mercer"})
    assert update_res.status_code == 200, f"Profile update failed: {update_res.text}"
    assert update_res.json()["role"] == "Lead Architect"
    print("[OK] User Profile Update PUT /api/v1/users/profile PASSED in PostgreSQL.")

    # 7. Upload Sample PDF Document via /api/v1/documents/upload
    pdf_content = b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n2 0 obj\n<<\n/Type /Pages\n/Kids [3 0 R]\n/Count 1\n>>\nendobj\n3 0 obj\n<<\n/Type /Page\n/Parent 2 0 R\n/Resources <<>>\n/MediaBox [0 0 612 792]\n/Contents 4 0 R\n>>\nendobj\n4 0 obj\n<<\n/Length 55\n>>\nstream\nBT\n/F1 12 Tf\n100 700 Td\n(NexaDocs Financial Audit Q3 Revenue $42.5M) Tj\nET\nendstream\nendobj\nxref\n0 5\n0000000000 65535 f\n0000000009 00000 n\n0000000058 00000 n\n0000000115 00000 n\n0000000216 00000 n\ntrailer\n<<\n/Size 5\n/Root 1 0 R\n>>\nstartxref\n321\n%%EOF"
    files = {"file": ("Q3_Financial_Audit_Test.pdf", pdf_content, "application/pdf")}
    upload_res = client.post("/api/v1/documents/upload", headers=headers, files=files)
    assert upload_res.status_code == 201, f"Upload document failed: {upload_res.text}"
    doc_info = upload_res.json()
    doc_id = doc_info["id"]
    print(f"[OK] Document Upload POST /api/v1/documents/upload PASSED. Doc ID: {doc_id}")

    # 8. Retrieve User Documents via /api/v1/documents
    docs_res = client.get("/api/v1/documents", headers=headers)
    assert docs_res.status_code == 200, f"Retrieve documents failed: {docs_res.text}"
    user_docs = docs_res.json()
    assert len(user_docs) >= 1
    print(f"[OK] Retrieve User Documents GET /api/v1/documents PASSED. Total docs in PostgreSQL: {len(user_docs)}")

    # 9. AI RAG Chat Query via /api/v1/ai/chat
    chat_payload = {
        "document_id": doc_id,
        "question": "What is the Q3 revenue in the financial audit document?"
    }
    chat_res = client.post("/api/v1/ai/chat", headers=headers, json=chat_payload)
    assert chat_res.status_code == 200, f"AI Chat failed: {chat_res.text}"
    chat_answer = chat_res.json()
    assert "answer" in chat_answer
    assert len(chat_answer["sources"]) > 0
    print("[OK] AI RAG Chat POST /api/v1/ai/chat PASSED with page citations.")

    # 10. AI SSE Streaming Query via /api/v1/ai/chat/stream
    stream_res = client.post("/api/v1/ai/chat/stream", headers=headers, json=chat_payload)
    assert stream_res.status_code == 200, f"AI Streaming failed: {stream_res.text}"
    assert "text/event-stream" in stream_res.headers.get("content-type", "")
    stream_text = stream_res.text
    assert "data: " in stream_text
    assert "start" in stream_text
    assert "done" in stream_text
    print("[OK] AI SSE Streaming POST /api/v1/ai/chat/stream PASSED (received token chunks).")

    # 11. Chat History Retrieval via /api/v1/ai/chat/history/{doc_id}
    hist_res = client.get(f"/api/v1/ai/chat/history/{doc_id}", headers=headers)
    assert hist_res.status_code == 200, f"History retrieval failed: {hist_res.text}"
    history_records = hist_res.json()
    assert len(history_records) >= 1
    print(f"[OK] Chat History GET /api/v1/ai/chat/history/{doc_id} PASSED ({len(history_records)} records).")

    # 12. FAISS Persistence Test (Simulate Server Restart by clearing in-memory caches)
    print("\n--- Testing FAISS Disk Persistence across Restart ---")
    embedding_service.doc_chunks.clear()
    embedding_service.faiss_indices.clear()
    assert doc_id not in embedding_service.doc_chunks, "Memory cache should be empty"
    
    # Query again: it must reload chunks and index from disk!
    reloaded_chunks = embedding_service.search_similar_chunks(doc_id, "revenue", top_k=2)
    assert len(reloaded_chunks) > 0, "Failed to reload vector chunks from persistent storage"
    assert doc_id in embedding_service.doc_chunks, "doc_chunks should now be repopulated from disk"
    print(f"[OK] FAISS Vector Persistence PASSED: Successfully retrieved {len(reloaded_chunks)} chunks after memory clear.")

    # 13. Document Deletion & Storage Cleanup
    del_res = client.delete(f"/api/v1/documents/{doc_id}", headers=headers)
    assert del_res.status_code == 204, f"Delete document failed: {del_res.status_code}"
    assert doc_id not in embedding_service.doc_chunks, "Index should be removed on deletion"
    print("[OK] Document Deletion DELETE /api/v1/documents/{doc_id} and FAISS Index cleanup PASSED.")

    print("\nALL 13 PRODUCTION READINESS VERIFICATION TESTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    run_tests()
