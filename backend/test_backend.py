import sys
import os
import time
import httpx
from fastapi.testclient import TestClient

# Ensure app package is importable
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.main import app

def run_tests():
    print("=== NexaDocs FastAPI Backend Test Suite ===")
    client = TestClient(app)

    # 1. Health Check
    res = client.get("/health")
    assert res.status_code == 200, f"Health check failed: {res.text}"
    print("[OK] Health Check PASSED:", res.json())

    # 2. User Registration
    test_email = f"test.user.{int(time.time())}@enterprise.com"
    reg_payload = {
        "name": "Alex Mercer",
        "email": test_email,
        "password": "SecurePassword123!"
    }
    reg_res = client.post("/api/auth/register", json=reg_payload)
    assert reg_res.status_code == 201, f"Register failed: {reg_res.text}"
    token_data = reg_res.json()
    token = token_data["access_token"]
    assert token, "Token missing from registration response"
    print("[OK] User Registration PASSED. JWT Received.")

    # 3. User Login
    login_payload = {
        "email": test_email,
        "password": "SecurePassword123!"
    }
    login_res = client.post("/api/auth/login", json=login_payload)
    assert login_res.status_code == 200, f"Login failed: {login_res.text}"
    login_token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {login_token}"}
    print("[OK] User Login PASSED.")

    # 4. Access Protected Route (/api/auth/me)
    me_res = client.get("/api/auth/me", headers=headers)
    assert me_res.status_code == 200, f"Protected route failed: {me_res.text}"
    user_info = me_res.json()
    assert user_info["email"] == test_email
    print(f"[OK] Protected Route GET /api/auth/me PASSED for user: {user_info['name']}")

    # 5. Upload Sample PDF Document
    pdf_content = b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n2 0 obj\n<<\n/Type /Pages\n/Kids [3 0 R]\n/Count 1\n>>\nendobj\n3 0 obj\n<<\n/Type /Page\n/Parent 2 0 R\n/Resources <<>>\n/MediaBox [0 0 612 792]\n/Contents 4 0 R\n>>\nendobj\n4 0 obj\n<<\n/Length 55\n>>\nstream\nBT\n/F1 12 Tf\n100 700 Td\n(NexaDocs Financial Audit Q3 Revenue $42.5M) Tj\nET\nendstream\nendobj\nxref\n0 5\n0000000000 65535 f\n0000000009 00000 n\n0000000058 00000 n\n0000000115 00000 n\n0000000216 00000 n\ntrailer\n<<\n/Size 5\n/Root 1 0 R\n>>\nstartxref\n321\n%%EOF"
    files = {"file": ("Q3_Financial_Audit_Test.pdf", pdf_content, "application/pdf")}
    
    upload_res = client.post("/api/documents/upload", headers=headers, files=files)
    assert upload_res.status_code == 201, f"Upload document failed: {upload_res.text}"
    doc_info = upload_res.json()
    doc_id = doc_info["id"]
    print(f"[OK] Document Upload POST /api/documents/upload PASSED. Doc ID: {doc_id}")

    # 6. Retrieve User Documents
    docs_res = client.get("/api/documents", headers=headers)
    assert docs_res.status_code == 200, f"Retrieve documents failed: {docs_res.text}"
    user_docs = docs_res.json()
    assert len(user_docs) >= 1
    print(f"[OK] Retrieve User Documents GET /api/documents PASSED. Total docs: {len(user_docs)}")

    # 7. AI RAG Chat Query
    chat_payload = {
        "document_id": doc_id,
        "question": "What is the Q3 revenue in the financial audit document?"
    }
    chat_res = client.post("/api/ai/chat", headers=headers, json=chat_payload)
    assert chat_res.status_code == 200, f"AI Chat failed: {chat_res.text}"
    chat_answer = chat_res.json()
    assert "answer" in chat_answer
    assert len(chat_answer["sources"]) > 0
    print("[OK] AI RAG Chat POST /api/ai/chat PASSED.")
    print("   Answer Output:", chat_answer["answer"])
    print("   Sources Citations:", chat_answer["sources"])

    print("\nALL 7 BACKEND API VERIFICATION TESTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    run_tests()
