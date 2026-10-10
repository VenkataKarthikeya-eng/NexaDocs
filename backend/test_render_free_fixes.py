import os
import io
import sys
import json
import pytest
from unittest.mock import MagicMock, patch

# Ensure backend root on sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.config import settings
from app.core.database import SessionLocal, engine
from app.models.document import Document
from app.models.document_chunk import DocumentChunk
from app.models.user import User
from app.services.storage_service import StorageService
from app.services.pdf_service import pdf_service
from app.services.embedding_service import embedding_service
from app.services.rag_service import rag_service
from reportlab.pdfgen import canvas


def create_sample_pdf_bytes(pages_data):
    """Generates valid multi-page PDF bytes in memory using ReportLab."""
    buf = io.BytesIO()
    c = canvas.Canvas(buf)
    for p_num, text_content in pages_data:
        c.drawString(100, 750, f"Page {p_num}")
        c.drawString(100, 700, text_content)
        c.showPage()
    c.save()
    return buf.getvalue()


def test_pdf_extraction_from_bytes_valid():
    """Test 1: Verify PDF text extraction directly from in-memory bytes preserving physical page numbers."""
    pages_data = [
        (1, "NexaDocs Cloud Architecture and S3 Storage Engine Specifications."),
        (2, "PostgreSQL database vector embeddings and similarity indexing with pgvector."),
        (3, "Google Gemini AI integration for evidence-grounded RAG answers and accurate citations.")
    ]
    pdf_bytes = create_sample_pdf_bytes(pages_data)

    extracted = pdf_service.extract_text_and_pages_from_bytes(pdf_bytes, filename="architecture.pdf")
    assert extracted["page_count"] == 3
    assert len(extracted["pages"]) == 3
    assert extracted["pages"][0]["page_number"] == 1
    assert "Cloud Architecture" in extracted["pages"][0]["text"]
    assert extracted["pages"][1]["page_number"] == 2
    assert "pgvector" in extracted["pages"][1]["text"]
    assert extracted["pages"][2]["page_number"] == 3
    assert "Google Gemini" in extracted["pages"][2]["text"]
    print("\n[TEST PASS] PDF extraction from bytes with physical page preservation.")


def test_pdf_extraction_corrupt_and_empty():
    """Test 2: Verify extraction rejects empty and corrupted bytes truthfully."""
    with pytest.raises(ValueError, match="empty"):
        pdf_service.extract_text_and_pages_from_bytes(b"", "empty.pdf")

    with pytest.raises(ValueError, match="header"):
        pdf_service.extract_text_and_pages_from_bytes(b"NOT_A_PDF_FILE_HEADER", "corrupt.pdf")
    print("[TEST PASS] PDF extraction rejection of corrupt and empty files.")


def test_s3_storage_mocked_operations():
    """Test 3: Verify S3-compatible storage (Neon Object Storage) upload, download, presigned URL, and deletion."""
    mock_boto_client = MagicMock()
    # Mock put_object
    mock_boto_client.put_object.return_value = {"ETag": '"test-etag"'}
    # Mock get_object
    mock_body = MagicMock()
    mock_body.read.return_value = b"%PDF-1.4 Mocked S3 PDF bytes content."
    mock_boto_client.get_object.return_value = {"Body": mock_body}
    # Mock presigned url
    mock_boto_client.generate_presigned_url.return_value = "https://us-east-2.storage.neon.tech/nexadocs-files/doc_presigned?token=xyz"
    # Mock head_object
    mock_boto_client.head_object.return_value = {"ContentLength": 1024}
    # Mock delete_object
    mock_boto_client.delete_object.return_value = {"DeleteMarker": True}

    storage = StorageService()
    storage.storage_type = "S3"
    storage.bucket_name = "nexadocs-files"
    storage.endpoint_url = "https://us-east-2.storage.neon.tech"
    storage._s3_client = mock_boto_client

    sample_content = b"%PDF-1.4 Valid S3 upload test document content for NexaDocs."
    import asyncio
    file_path, file_url = asyncio.run(storage.save_file("doc-neon-1", "spec.pdf", sample_content))

    assert file_path == "s3://nexadocs-files/documents/doc-neon-1_spec.pdf"
    assert file_url == "/api/v1/documents/doc-neon-1/file"
    mock_boto_client.put_object.assert_called_once()

    # Test download bytes
    downloaded_bytes = storage.get_file_bytes(file_path)
    assert downloaded_bytes == b"%PDF-1.4 Mocked S3 PDF bytes content."
    mock_boto_client.get_object.assert_called_once_with(Bucket="nexadocs-files", Key="documents/doc-neon-1_spec.pdf")

    # Test presigned URL generation for private bucket
    presigned = storage.generate_presigned_download_url(file_path, filename="spec.pdf")
    assert "token=xyz" in presigned

    # Test file exists check
    assert storage.file_exists(file_path) is True

    # Test delete
    assert storage.delete_file(file_path) is True
    mock_boto_client.delete_object.assert_called_once_with(Bucket="nexadocs-files", Key="documents/doc-neon-1_spec.pdf")
    print("[TEST PASS] S3-compatible upload, download, presigned URL, and deletion.")


def test_postgresql_vector_persistence_and_similarity():
    """Test 4: Verify chunk and vector persistence in PostgreSQL and cosine similarity retrieval."""
    test_doc_id = "test-doc-postgres-vector-1"

    # Create a parent Document record in DB to satisfy foreign key constraint
    db = SessionLocal()
    try:
        # Get or create demo user
        user = db.query(User).filter(User.email == "demo@nexadocs.com").first()
        if not user:
            user = User(email="demo@nexadocs.com", name="Demo User", password_hash="test")
            db.add(user)
            db.commit()

        # Clean existing test doc
        db.query(Document).filter(Document.id == test_doc_id).delete()
        db.commit()

        doc = Document(
            id=test_doc_id,
            user_id=user.id,
            title="Q3_Report.pdf",
            filename="Q3_Report.pdf",
            file_path="s3://nexadocs-files/documents/Q3_Report.pdf",
            status="READY"
        )
        db.add(doc)
        db.commit()
    finally:
        db.close()

    chunks = [
        {"chunk_id": 0, "page": 1, "text": "NexaDocs Q3 enterprise revenue was $42.5 million with 24% year-over-year expansion."},
        {"chunk_id": 1, "page": 1, "text": "Operating EBITDA margin expanded to 31.2% exceeding projections across EMEA."},
        {"chunk_id": 2, "page": 2, "text": "Cloud infrastructure and Neon PostgreSQL database migration reduced latency by 35%."}
    ]

    # Index chunks into PostgreSQL
    embedding_service.index_document_chunks(test_doc_id, chunks)

    # Verify rows in PostgreSQL table document_chunks
    db = SessionLocal()
    try:
        db_chunks = db.query(DocumentChunk).filter(DocumentChunk.document_id == test_doc_id).all()
        assert len(db_chunks) == 3, f"Expected 3 chunks in PostgreSQL, found {len(db_chunks)}"
        assert db_chunks[0].page_number == 1
        assert "revenue" in db_chunks[0].content
        # Verify embedding JSON is present
        emb = json.loads(db_chunks[0].embedding_json)
        assert len(emb) == embedding_service.dimension
        print(f"[TEST PASS] Successfully stored {len(db_chunks)} chunks in PostgreSQL document_chunks table.")
    finally:
        db.close()

    # Clear memory cache to test recovery from PostgreSQL
    embedding_service.doc_chunks.pop(test_doc_id, None)
    assert test_doc_id not in embedding_service.doc_chunks

    # Search similar chunks (loads from PostgreSQL)
    results = embedding_service.search_similar_chunks(test_doc_id, "enterprise revenue growth", top_k=2)
    assert len(results) > 0
    top_chunk = results[0]
    assert top_chunk["page_number"] == 1
    assert "revenue" in top_chunk["content"].lower()
    assert top_chunk["similarity"] > 0.3
    print(f"[TEST PASS] Retrieved from PostgreSQL: Page {top_chunk['page_number']}, score: {top_chunk['similarity']}")

    # Clean up test document (cascading deletes all chunks in DB)
    db = SessionLocal()
    try:
        doc = db.query(Document).filter(Document.id == test_doc_id).first()
        if doc:
            db.delete(doc)
            db.commit()
        assert db.query(DocumentChunk).filter(DocumentChunk.document_id == test_doc_id).count() == 0
    finally:
        db.close()
    embedding_service.delete_index(test_doc_id)
    print("[TEST PASS] Document deletion purged all chunks from PostgreSQL.")


def test_embedding_api_memory_and_fallback():
    """Test 5: Verify embedding service operates without PyTorch/SentenceTransformers in memory."""
    assert embedding_service.embedding_provider == "GEMINI"
    # Ensure local model is NOT loaded in memory
    assert embedding_service._local_model is None, "SentenceTransformers was loaded prematurely into RAM"

    # Test single embedding
    vec = embedding_service.get_embedding("Test prompt for vector dimension verification")
    assert len(vec) == embedding_service.dimension
    assert abs(float(sum(vec**2)) - 1.0) < 0.05, "Vector should be approximately unit length"

    # Test batch embedding
    batch = embedding_service.get_batch_embeddings(["Chunk 1 text", "Chunk 2 text"])
    assert len(batch) == 2
    assert batch.shape[1] == embedding_service.dimension
    print(f"[TEST PASS] Remote embedding generation verified (dimension: {embedding_service.dimension}, local model not in RAM).")


def test_document_ownership_and_rag_grounded():
    """Test 6: Verify end-to-end RAG grounded answer with citations from PostgreSQL chunks."""
    doc_id = "test-doc-rag-grounded-1"

    # Create parent Document in DB
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == "demo@nexadocs.com").first()
        if not user:
            user = User(email="demo@nexadocs.com", name="Demo User", password_hash="test")
            db.add(user)
            db.commit()

        db.query(Document).filter(Document.id == doc_id).delete()
        db.commit()

        doc = Document(
            id=doc_id,
            user_id=user.id,
            title="Security_Report.pdf",
            filename="Security_Report.pdf",
            file_path="s3://nexadocs-files/documents/Security_Report.pdf",
            status="READY"
        )
        db.add(doc)
        db.commit()
    finally:
        db.close()

    chunks = [
        {"chunk_id": 0, "page": 1, "text": "NexaDocs SOC2 Type II certification was completed by Deloitte in September 2026."},
        {"chunk_id": 1, "page": 2, "text": "Data is encrypted at rest using AES-256 and in transit using TLS 1.3."}
    ]
    embedding_service.index_document_chunks(doc_id, chunks)

    # Test grounded RAG query
    rag_res = rag_service.answer_question(doc_id, "Security_Report.pdf", "Who audited the SOC2 certification?")
    assert "answer" in rag_res
    assert len(rag_res["sources"]) > 0
    top_source = rag_res["sources"][0]
    assert top_source["page"] == 1
    assert "deloitte" in top_source["snippet"].lower() or "soc2" in top_source["snippet"].lower()

    # Test honest abstention on missing topic
    abstain_res = rag_service.answer_question(doc_id, "Security_Report.pdf", "What is the average flight speed of an eagle?")
    assert "sources" in abstain_res and len(abstain_res["sources"]) == 0
    assert "does not contain sufficient" in abstain_res["answer"]

    # Cleanup
    embedding_service.delete_index(doc_id)
    print("[TEST PASS] Grounded RAG with citations and honest abstention verified.")


if __name__ == "__main__":
    print("=" * 70)
    print("Running NexaDocs Render Free Deployment Verification Suite")
    print("=" * 70)
    test_pdf_extraction_from_bytes_valid()
    test_pdf_extraction_corrupt_and_empty()
    test_s3_storage_mocked_operations()
    test_postgresql_vector_persistence_and_similarity()
    test_embedding_api_memory_and_fallback()
    test_document_ownership_and_rag_grounded()
    print("=" * 70)
    print("ALL 6 RENDER FREE VERIFICATION TESTS PASSED (100%)")
    print("=" * 70)
