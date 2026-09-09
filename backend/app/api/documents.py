import os
import uuid
from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.responses import FileResponse, RedirectResponse
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
    # Validate PDF file format
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF documents are supported."
        )

    doc_id = str(uuid.uuid4())
    safe_filename = f"{doc_id}_{file.filename}"

    # Read contents & compute size
    contents = await file.read()
    file_size_mb = round(len(contents) / (1024 * 1024), 2)
    file_size_str = f"{file_size_mb} MB" if file_size_mb >= 0.01 else "< 0.01 MB"

    # Save via StorageService (Supports Local Disk and Cloud S3/Cloudinary for Render production)
    file_path, file_url = await storage_service.save_file(safe_filename, contents)

    # Extract text with PDF service
    extracted = pdf_service.extract_text_and_pages(file_path)
    page_count = extracted["page_count"]
    chunks = pdf_service.chunk_text(extracted["pages"])
    chunk_count = len(chunks)

    # Index chunks in FAISS vector engine
    embedding_service.index_document_chunks(doc_id, chunks)

    # Generate document insights
    extracted_insights = insight_service.generate_document_insights(
        file.filename, extracted["full_text"], extracted["pages"]
    )

    # Save Document record to DB
    new_doc = Document(
        id=doc_id,
        user_id=current_user.id,
        title=file.filename,
        filename=file.filename,
        file_path=file_path,
        file_size=file_size_str,
        page_count=page_count,
        chunk_count=chunk_count,
        category="Engineering" if "tech" in file.filename.lower() or "arch" in file.filename.lower() else "General",
        status="Ready"
    )
    db.add(new_doc)
    db.flush()

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

    storage_service.delete_file(doc.file_path)
    embedding_service.delete_index(doc.id)
    db.delete(doc)
    db.commit()
    return None

@router.get("/{doc_id}/file")
def get_document_file(doc_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    doc = db.query(Document).filter(Document.id == doc_id, Document.user_id == current_user.id).first()
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found.")

    if doc.file_path.startswith("http://") or doc.file_path.startswith("https://"):
        return RedirectResponse(url=doc.file_path)

    if not os.path.exists(doc.file_path):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found on storage server.")

    return FileResponse(doc.file_path, media_type="application/pdf", filename=doc.filename)
