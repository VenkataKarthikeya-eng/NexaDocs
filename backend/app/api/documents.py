import os
import uuid
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.responses import FileResponse, RedirectResponse, Response
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.document import Document
from app.models.insight import Insight
from app.schemas.document import DocumentResponse
from app.services.pdf_service import pdf_service
from app.services.embedding_service import embedding_service
from app.services.insight_service import insight_service
from app.services.storage_service import storage_service

router = APIRouter(prefix="/documents", tags=["Documents"])

@router.post("/upload", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Validate PDF file extension
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF documents (.pdf) are supported."
        )

    doc_id = str(uuid.uuid4())

    # Read contents & compute size
    contents = await file.read()
    if not contents or len(contents) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is empty (0 bytes)."
        )

    file_size_mb = round(len(contents) / (1024 * 1024), 2)
    file_size_str = f"{file_size_mb} MB" if file_size_mb >= 0.01 else "< 0.01 MB"

    # 1. Extract text and physical pages directly from in-memory bytes
    try:
        extracted = pdf_service.extract_text_and_pages_from_bytes(contents, file.filename)
        page_count = extracted["page_count"]
        chunks = pdf_service.chunk_text(extracted["pages"])
        chunk_count = len(chunks)
    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(ve)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"PDF parsing error: {str(e)}"
        )

    # 2. Save via StorageService (Neon S3 or local)
    try:
        file_path, file_url = await storage_service.save_file(doc_id, file.filename, contents)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Storage failure while saving document: {str(e)}"
        )

    # Determine automatic category
    name_low = file.filename.lower()
    if any(k in name_low for k in ["finan", "q1", "q2", "q3", "q4", "audit", "revenue", "budget"]):
        category = "Finance"
    elif any(k in name_low for k in ["tech", "arch", "system", "code", "api"]):
        category = "Engineering"
    elif any(k in name_low for k in ["legal", "sla", "contract", "soc2", "compliance"]):
        category = "Legal & Compliance"
    elif any(k in name_low for k in ["research", "paper", "study", "clinical"]):
        category = "Research"
    else:
        category = "General"

    # 3. Save Document record to DB first (so document_chunks foreign key succeeds)
    new_doc = Document(
        id=doc_id,
        user_id=current_user.id,
        title=file.filename,
        filename=file.filename,
        file_path=file_path,
        file_size=file_size_str,
        page_count=page_count,
        chunk_count=chunk_count,
        category=category,
        status="Ready",
        processing_progress=100
    )
    db.add(new_doc)
    db.flush()

    # 4. Index chunks in persistent vector engine (PostgreSQL/Gemini) and generate insights
    try:
        embedding_service.index_document_chunks(doc_id, chunks, db=db, commit=False)

        # Generate document insights
        extracted_insights = insight_service.generate_document_insights(
            file.filename, extracted["full_text"], extracted["pages"]
        )
    except Exception as e:
        # Clean up stored file and DB transaction on pipeline failure
        storage_service.delete_file(file_path)
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Document indexing pipeline failed: {str(e)}"
        )

    # Save Insight record to DB
    new_insight = Insight(
        document_id=doc_id,
        summary=extracted_insights["summary"],
        topics=extracted_insights["topics"],
        entities=extracted_insights["entities"],
        key_takeaways=extracted_insights["key_takeaways"]
    )
    db.add(new_insight)
    db.commit()

    return DocumentResponse(
        id=new_doc.id,
        title=new_doc.title,
        filename=new_doc.filename,
        fileSize=new_doc.file_size,
        pageCount=new_doc.page_count,
        chunkCount=new_doc.chunk_count,
        status=new_doc.status,
        processingProgress=new_doc.processing_progress,
        errorMessage=new_doc.error_message,
        category=new_doc.category,
        createdAt=new_doc.created_at.strftime("%Y-%m-%d"),
        summary=extracted_insights["summary"],
        topics=extracted_insights["topics"],
        entities=extracted_insights["entities"],
        highlights=extracted_insights["key_takeaways"]
    )

@router.get("", response_model=List[DocumentResponse])
def get_documents(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    docs = db.query(Document).filter(Document.user_id == current_user.id).order_by(Document.created_at.desc()).all()
    
    result = []
    for d in docs:
        insight = db.query(Insight).filter(Insight.document_id == d.id).first()
        result.append(DocumentResponse(
            id=d.id,
            title=d.title,
            filename=d.filename,
            fileSize=d.file_size,
            pageCount=d.page_count,
            chunkCount=d.chunk_count,
            status=d.status,
            processingProgress=d.processing_progress or 100,
            errorMessage=d.error_message,
            category=d.category,
            createdAt=d.created_at.strftime("%Y-%m-%d"),
            summary=insight.summary if insight else "Document indexed and ready for AI conversation.",
            topics=insight.topics if insight else ["PDF Document"],
            entities=insight.entities if insight else [],
            highlights=insight.key_takeaways if insight else []
        ))
    return result

@router.get("/{doc_id}", response_model=DocumentResponse)
def get_document(doc_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    doc = db.query(Document).filter(Document.id == doc_id, Document.user_id == current_user.id).first()
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found.")

    insight = db.query(Insight).filter(Insight.document_id == doc.id).first()
    return DocumentResponse(
        id=doc.id,
        title=doc.title,
        filename=doc.filename,
        fileSize=doc.file_size,
        pageCount=doc.page_count,
        chunkCount=doc.chunk_count,
        status=doc.status,
        processingProgress=doc.processing_progress or 100,
        errorMessage=doc.error_message,
        category=doc.category,
        createdAt=doc.created_at.strftime("%Y-%m-%d"),
        summary=insight.summary if insight else "",
        topics=insight.topics if insight else [],
        entities=insight.entities if insight else [],
        highlights=insight.key_takeaways if insight else []
    )

@router.delete("/{doc_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_document(doc_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    doc = db.query(Document).filter(Document.id == doc_id, Document.user_id == current_user.id).first()
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found.")

    # 1. Clean up file from storage
    storage_service.delete_file(doc.file_path)
    # 2. Clean up vector index and chunk files
    embedding_service.delete_index(doc.id)
    # 3. Clean up database records (cascading deletes chats & insights)
    db.delete(doc)
    db.commit()
    return None

@router.get("/{doc_id}/file")
def get_document_file(doc_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    doc = db.query(Document).filter(Document.id == doc_id, Document.user_id == current_user.id).first()
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found.")

    # 1. Neon S3-compatible private object storage handling
    if doc.file_path.startswith("s3://"):
        # Generate presigned download URL for private bucket
        presigned = storage_service.generate_presigned_download_url(doc.file_path, filename=doc.filename)
        if presigned:
            return RedirectResponse(url=presigned, status_code=status.HTTP_307_TEMPORARY_REDIRECT)

        # Fallback to direct authenticated server-side stream
        try:
            content = storage_service.get_file_bytes(doc.file_path)
            return Response(
                content=content,
                media_type="application/pdf",
                headers={"Content-Disposition": f'inline; filename="{doc.filename}"'}
            )
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"File not found in object storage: {str(e)}")

    # 2. Direct external HTTPS URL
    if doc.file_path.startswith("http://") or doc.file_path.startswith("https://"):
        return RedirectResponse(url=doc.file_path)

    # 3. Local filesystem storage
    if not os.path.exists(doc.file_path):
        if doc.id in ("doc-1", "doc-2", "doc-3"):
            try:
                from reportlab.pdfgen import canvas
                os.makedirs(os.path.dirname(doc.file_path) or ".", exist_ok=True)
                c = canvas.Canvas(doc.file_path)
                c.drawString(100, 750, f"{doc.title}")
                c.drawString(100, 700, f"NexaDocs Enterprise Knowledge Base: {doc.title}")
                c.showPage()
                c.save()
            except Exception:
                os.makedirs(os.path.dirname(doc.file_path) or ".", exist_ok=True)
                with open(doc.file_path, "wb") as f:
                    f.write(b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n2 0 obj\n<<\n/Type /Pages\n/Kids []\n/Count 0\n>>\nendobj\ntrailer\n<<\n/Root 1 0 R\n>>\n%%EOF\n")
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found on storage server.")

    return FileResponse(doc.file_path, media_type="application/pdf", filename=doc.filename)
