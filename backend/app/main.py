import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import engine, Base
from app.models import User, Document, ChatHistory, Insight, DocumentChunk
from app.api import auth, users, documents, ai

# Initialize Database tables in PostgreSQL / SQLite
Base.metadata.create_all(bind=engine)

def _generate_sample_pdf_bytes(doc_info: dict) -> bytes:
    try:
        import io
        from reportlab.pdfgen import canvas
        buf = io.BytesIO()
        c = canvas.Canvas(buf)
        c.drawString(100, 750, f"{doc_info.get('title', 'Document')}")
        c.drawString(100, 720, f"Summary: {doc_info.get('summary', '')[:80]}...")
        for chunk in doc_info.get("chunks", []):
            c.drawString(100, 680 - (chunk.get("chunk_id", 0) * 40), f"P{chunk.get('page', 1)}: {chunk.get('text', '')[:60]}")
        c.showPage()
        c.save()
        return buf.getvalue()
    except Exception:
        return b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n2 0 obj\n<<\n/Type /Pages\n/Kids []\n/Count 0\n>>\nendobj\ntrailer\n<<\n/Root 1 0 R\n>>\n%%EOF\n"


def seed_demo_data():
    """Seeds default demo account and sample enterprise knowledge base docs idempotently."""
    from app.core.database import SessionLocal
    from app.core.security import get_password_hash, verify_password
    from app.services.embedding_service import embedding_service
    from app.services.storage_service import storage_service

    db = SessionLocal()
    try:
        demo_user = db.query(User).filter(User.email == "demo@nexadocs.com").first()
        if not demo_user:
            demo_user = User(
                id="user-demo-alex-mercer",
                name="Alex Mercer",
                email="demo@nexadocs.com",
                password_hash=get_password_hash("Demo@123"),
                role="Enterprise Lead",
                plan="Enterprise Pro"
            )
            db.add(demo_user)
            db.commit()
            db.refresh(demo_user)
            print("[Seeder] Created default demo user: demo@nexadocs.com")
        else:
            if not verify_password("Demo@123", demo_user.password_hash):
                demo_user.password_hash = get_password_hash("Demo@123")
                db.commit()

        sample_data = [
            {
                "id": "doc-1",
                "title": "Enterprise Financial Report.pdf",
                "filename": "Enterprise_Financial_Report.pdf",
                "file_size": "4.8 MB",
                "page_count": 38,
                "chunk_count": 142,
                "category": "Finance",
                "summary": "Comprehensive financial report detailing Q3 enterprise revenue growth ($42.5M, +24% YoY), EBITDA margins (31.2%), and capital allocation toward cloud data infrastructure.",
                "topics": ["Revenue Growth", "EBITDA Margin", "CapEx Allocation", "Supply Chain Risk", "Market Expansion"],
                "entities": [
                    {"name": "Total Q3 Revenue", "type": "Metric", "detail": "$42.5 Million (+24%)"},
                    {"name": "AI Infrastructure Budget", "type": "Financial", "detail": "$8.2 Million"},
                    {"name": "Deloitte Auditing Group", "type": "Organization", "detail": "External Auditor"},
                    {"name": "Target Q4 Growth", "type": "Forecast", "detail": "28% YoY expansion"}
                ],
                "highlights": [
                    {"page": 4, "text": "Operating expenses decreased by 6.4% due to automated document intelligence pipelines."},
                    {"page": 12, "text": "Cloud infrastructure unit economics improved with 99.99% service availability."}
                ],
                "chunks": [
                    {"chunk_id": 0, "page": 1, "text": "Enterprise Financial Report Q3. Executive Overview: Consolidated performance achieved milestones across North America and EMEA."},
                    {"chunk_id": 1, "page": 4, "text": "Financial Metrics: In Q3, enterprise revenue reached $42.5 Million (+24% YoY). Operating EBITDA margin expanded to 31.2%, exceeding analyst projections."},
                    {"chunk_id": 2, "page": 12, "text": "Capital Allocation & Unit Economics: $8.2 Million was directed to AI infrastructure and scalable vector retrieval systems, reducing compute burn by 21%."}
                ]
            },
            {
                "id": "doc-2",
                "title": "AI Research Paper.pdf",
                "filename": "AI_Research_Paper.pdf",
                "file_size": "6.1 MB",
                "page_count": 52,
                "chunk_count": 210,
                "category": "Research",
                "summary": "Peer-reviewed research study examining the deployment of retrieval-augmented generation models, vector similarity indexing, and citation matching in clinical diagnostics and software compliance.",
                "topics": ["Clinical RAG", "FDA Compliance", "Medical Diagnostics", "FAISS Indexing", "NLP Extraction"],
                "entities": [
                    {"name": "Diagnostic Precision", "type": "Metric", "detail": "94.8% accuracy score"},
                    {"name": "FDA Software Standard", "type": "Regulatory", "detail": "Class II Software Medical Device"},
                    {"name": "Stanford Medical Labs", "type": "Partner", "detail": "Research Institution"}
                ],
                "highlights": [
                    {"page": 14, "text": "Document intelligence platforms reduced diagnostic transcription time by 42%."}
                ],
                "chunks": [
                    {"chunk_id": 0, "page": 1, "text": "AI Research Paper: Evaluating Multi-Modal RAG in Healthcare & Enterprise Document Compliance."},
                    {"chunk_id": 1, "page": 14, "text": "Diagnostic Precision & Results: Document intelligence platforms reduced diagnostic transcription time by 42% with 94.8% accuracy matching."}
                ]
            },
            {
                "id": "doc-3",
                "title": "Technical Architecture Document.pdf",
                "filename": "Technical_Architecture_Document.pdf",
                "file_size": "2.3 MB",
                "page_count": 22,
                "chunk_count": 88,
                "category": "Engineering",
                "summary": "Technical architecture specification outlining FAISS vector indexing, smart recursive chunking algorithms, PyPDF text extraction, FastAPI async backend, and React Zustand frontend integration.",
                "topics": ["FAISS Indexing", "FastAPI Backend", "RAG Retrieval", "Vector Embeddings", "JWT Auth"],
                "entities": [
                    {"name": "SentenceTransformers", "type": "AI Framework", "detail": "all-MiniLM-L6-v2 model"},
                    {"name": "FAISS Vector DB", "type": "Database", "detail": "FlatIP Indexing for sub-180ms queries"},
                    {"name": "FastAPI / Uvicorn", "type": "Backend", "detail": "Async ASGI Python framework"},
                    {"name": "PyPDF / PDFPlumber", "type": "Extractor", "detail": "Multi-threaded text & table parser"}
                ],
                "highlights": [
                    {"page": 2, "text": "RAG retrieval latency targeted at under 180ms for enterprise document querying."},
                    {"page": 8, "text": "FAISS index automatically regenerated upon incremental document uploads."}
                ],
                "chunks": [
                    {"chunk_id": 0, "page": 1, "text": "Technical Architecture Document: NexaDocs Vector Ingestion Engine. Recursive chunking splits text into 500 characters with 100 character overlap."},
                    {"chunk_id": 1, "page": 2, "text": "Latency & FAISS Benchmarks: RAG retrieval latency is targeted at under 180ms for enterprise document querying with sub-millisecond IndexFlatIP inner-product ranking."},
                    {"chunk_id": 2, "page": 8, "text": "Security & Compliance: SOC2 Type II compliance, AES-256 encryption at rest, TLS 1.3 in transit. Vector indices are persisted to disk."}
                ]
            }
        ]

        all_seeded_successfully = True
        failed_docs = []

        for s in sample_data:
            doc_id = s["id"]
            filename = s["filename"]

            # 1. Resolve file_path (Neon Object Storage vs Local)
            file_path = ""
            if storage_service.storage_type == "S3":
                s3_key = f"documents/{doc_id}_{filename}"
                s3_uri = f"s3://{storage_service.bucket_name}/{s3_key}"
                file_path = s3_uri
                try:
                    s3_client = storage_service._get_s3_client()
                    if s3_client and storage_service.bucket_name:
                        try:
                            s3_client.head_object(Bucket=storage_service.bucket_name, Key=s3_key)
                        except Exception:
                            pdf_bytes = _generate_sample_pdf_bytes(s)
                            s3_client.put_object(
                                Bucket=storage_service.bucket_name,
                                Key=s3_key,
                                Body=pdf_bytes,
                                ContentType="application/pdf"
                            )
                            print(f"[Seeder] Uploaded {doc_id} to S3 bucket {storage_service.bucket_name}")
                except Exception as s3_err:
                    print(f"[Seeder] S3 notice for {doc_id}: {s3_err}")
            else:
                local_path = os.path.join(settings.UPLOAD_DIR, filename)
                if not os.path.exists(local_path):
                    pdf_bytes = _generate_sample_pdf_bytes(s)
                    with open(local_path, "wb") as f:
                        f.write(pdf_bytes)
                file_path = local_path

            # 2. Idempotently get or create Document
            existing_doc = db.query(Document).filter(Document.id == doc_id).first()
            if not existing_doc:
                doc = Document(
                    id=doc_id,
                    user_id=demo_user.id,
                    title=s["title"],
                    filename=filename,
                    file_path=file_path,
                    file_size=s["file_size"],
                    page_count=s["page_count"],
                    chunk_count=s["chunk_count"],
                    category=s["category"],
                    status="READY",
                    processing_progress=100,
                    error_message=None
                )
                db.add(doc)
                db.commit()
                db.refresh(doc)
            else:
                existing_doc.user_id = demo_user.id
                existing_doc.title = s["title"]
                existing_doc.filename = filename
                existing_doc.file_path = file_path
                existing_doc.file_size = s["file_size"]
                existing_doc.page_count = s["page_count"]
                existing_doc.chunk_count = s["chunk_count"]
                existing_doc.category = s["category"]
                existing_doc.status = "READY"
                existing_doc.processing_progress = 100
                existing_doc.error_message = None
                db.commit()

            # 3. Idempotently get or create Insight
            existing_ins = db.query(Insight).filter(Insight.document_id == doc_id).first()
            if not existing_ins:
                ins = Insight(
                    document_id=doc_id,
                    summary=s["summary"],
                    topics=s["topics"],
                    entities=s["entities"],
                    key_takeaways=s["highlights"]
                )
                db.add(ins)
                db.commit()
            else:
                existing_ins.summary = s["summary"]
                existing_ins.topics = s["topics"]
                existing_ins.entities = s["entities"]
                existing_ins.key_takeaways = s["highlights"]
                db.commit()

            # 4. Idempotently index document chunks if not already persisted
            existing_chunks = db.query(DocumentChunk).filter(DocumentChunk.document_id == doc_id).all()
            if len(existing_chunks) != len(s["chunks"]):
                try:
                    embedding_service.index_document_chunks(doc_id, s["chunks"], db=db, commit=True)
                except Exception as chunk_err:
                    db.rollback()
                    print(f"[Seeder] Chunk indexing error for {doc_id}: {chunk_err}")

            # 5. Strict verification: ensure Document, Insight, and required Chunks are actually persisted
            verified_doc = db.query(Document).filter(Document.id == doc_id).first()
            verified_ins = db.query(Insight).filter(Insight.document_id == doc_id).first()
            verified_chunks = db.query(DocumentChunk).filter(DocumentChunk.document_id == doc_id).all()

            if not verified_doc or not verified_ins or len(verified_chunks) < len(s["chunks"]):
                all_seeded_successfully = False
                failed_docs.append({
                    "doc_id": doc_id,
                    "doc_persisted": bool(verified_doc),
                    "insight_persisted": bool(verified_ins),
                    "chunks_persisted": len(verified_chunks),
                    "chunks_required": len(s["chunks"])
                })
                print(f"[Seeder] Persistence verification FAILED for {doc_id}: doc={bool(verified_doc)}, insight={bool(verified_ins)}, chunks={len(verified_chunks)}/{len(s['chunks'])}")

        if all_seeded_successfully:
            print(f"[Seeder] Successfully verified and seeded demo knowledge base ({len(sample_data)} docs).")
        else:
            print(f"[Seeder] CRITICAL: Seeding verification failed. Incomplete documents: {failed_docs}")
            raise RuntimeError(f"Demo knowledge base seeding verification failed: {failed_docs}")
    except Exception as e:
        db.rollback()
        print(f"[Seeder] Seeder failure: {e}")
        raise
    finally:
        db.close()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: seed demo user and initial documents idempotently
    try:
        seed_demo_data()
    except Exception as e:
        print(f"[Lifespan] Seeder notice during startup: {e}")
    yield

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="AI-Powered Document Intelligence Platform API",
    version="2.4.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Configure CORS Middleware with explicit allowed origins and Vercel regex
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_origin_regex=r"^https:\/\/.*\.vercel\.app$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers under /api/v1 (primary) and /api (backwards-compatibility)
app.include_router(auth.router, prefix=settings.API_V1_STR)
app.include_router(users.router, prefix=settings.API_V1_STR)
app.include_router(documents.router, prefix=settings.API_V1_STR)
app.include_router(ai.router, prefix=settings.API_V1_STR)

app.include_router(auth.router, prefix="/api")
app.include_router(users.router, prefix="/api")
app.include_router(documents.router, prefix="/api")
app.include_router(ai.router, prefix="/api")

@app.get("/")
def root():
    return {
        "status": "healthy",
        "app": "NexaDocs API",
        "version": "2.4.0",
        "docs": "/docs",
        "vector_engine": "FAISS Dense Semantic Active"
    }

@app.get("/health")
@app.get("/api/health")
@app.get("/api/v1/health")
def health_check():
    from sqlalchemy import text
    from app.core.database import SessionLocal
    db_status = "connected"
    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
    except Exception as e:
        db_status = f"unhealthy: {e}"

    return {
        "status": "ok" if db_status == "connected" else "degraded",
        "database": db_status,
        "vector_engine": "FAISS Active",
        "embedding_model": "all-MiniLM-L6-v2",
        "gemini_model": settings.GEMINI_MODEL
    }

