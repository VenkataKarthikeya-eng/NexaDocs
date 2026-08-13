from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.document import Document
from app.models.chat_history import ChatHistory
from app.models.insight import Insight
from app.schemas.chat import ChatRequest, ChatResponse, AnalyzeRequest, InsightResponse
from app.services.rag_service import rag_service
from app.services.insight_service import insight_service

router = APIRouter(prefix="/ai", tags=["AI Engine"])

@router.post("/chat", response_model=ChatResponse)
def ai_chat(
    req: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    doc = db.query(Document).filter(Document.id == req.document_id, Document.user_id == current_user.id).first()
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found.")

    rag_result = rag_service.answer_question(doc.id, doc.filename, req.question)

    chat_rec = ChatHistory(
        user_id=current_user.id,
        document_id=doc.id,
        question=req.question,
        answer=rag_result["answer"],
        sources=rag_result["sources"]
    )
    db.add(chat_rec)
    db.commit()
    db.refresh(chat_rec)

    return ChatResponse(
        id=chat_rec.id,
        sender="assistant",
        question=chat_rec.question,
        answer=chat_rec.answer,
        timestamp=chat_rec.timestamp.strftime("%I:%M %p"),
        sources=rag_result["sources"]
    )

@router.post("/chat/stream")
async def ai_chat_stream(
    req: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Streaming Server-Sent Events (SSE) RAG Response Endpoint.
    Yields progressive tokens for ChatGPT-like progressive text rendering.
    """
    doc = db.query(Document).filter(Document.id == req.document_id, Document.user_id == current_user.id).first()
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found.")

    return StreamingResponse(
        rag_service.stream_answer(doc.id, doc.filename, req.question),
        media_type="text/event-stream"
    )

@router.post("/analyze", response_model=InsightResponse)
def analyze_document(
    req: AnalyzeRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    doc = db.query(Document).filter(Document.id == req.document_id, Document.user_id == current_user.id).first()
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found.")

    insight = db.query(Insight).filter(Insight.document_id == doc.id).first()
    if not insight:
        extracted = insight_service.generate_document_insights(doc.filename, "Extracted text content.", [])
        insight = Insight(
            document_id=doc.id,
            summary=extracted["summary"],
            topics=extracted["topics"],
            entities=extracted["entities"],
            key_takeaways=extracted["key_takeaways"]
        )
        db.add(insight)
        db.commit()
        db.refresh(insight)

    return InsightResponse(
        document_id=doc.id,
        summary=insight.summary,
        topics=insight.topics or [],
        entities=insight.entities or [],
        key_takeaways=insight.key_takeaways or []
    )

@router.get("/insights/{doc_id}", response_model=InsightResponse)
def get_insights(
    doc_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    doc = db.query(Document).filter(Document.id == doc_id, Document.user_id == current_user.id).first()
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found.")

    insight = db.query(Insight).filter(Insight.document_id == doc.id).first()
    if not insight:
        return InsightResponse(
            document_id=doc.id,
            summary="Document indexed and ready for AI insights.",
            topics=["General"],
            entities=[],
            key_takeaways=[]
        )

    return InsightResponse(
        document_id=doc.id,
        summary=insight.summary,
        topics=insight.topics or [],
        entities=insight.entities or [],
        key_takeaways=insight.key_takeaways or []
    )
