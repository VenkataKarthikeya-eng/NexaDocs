import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Float, Text
from sqlalchemy.orm import relationship
from app.core.database import Base

class Document(Base):
    __tablename__ = "documents"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String, nullable=False)
    filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    file_size = Column(String, default="0 MB")
    page_count = Column(Integer, default=1)
    chunk_count = Column(Integer, default=1)
    category = Column(String, default="General")
    status = Column(String, default="READY")  # UPLOAD, EXTRACTING, EMBEDDING, INDEXING, READY, FAILED
    error_message = Column(Text, nullable=True)
    processing_progress = Column(Integer, default=100) # 0 to 100%
    processed_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    owner = relationship("User", back_populates="documents")
    chats = relationship("ChatHistory", back_populates="document", cascade="all, delete-orphan")
    insight = relationship("Insight", back_populates="document", uselist=False, cascade="all, delete-orphan")
