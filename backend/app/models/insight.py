import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.core.database import Base

class Insight(Base):
    __tablename__ = "insights"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    document_id = Column(String, ForeignKey("documents.id", ondelete="CASCADE"), unique=True, nullable=False)
    summary = Column(Text, nullable=False)
    topics = Column(JSON, default=list)        # List of topic tags ["#EBITDA", "#CapEx"]
    entities = Column(JSON, default=list)      # Extracted entities [{name: "Deloitte", type: "Org"}]
    key_takeaways = Column(JSON, default=list) # List of key highlights [{page: 1, text: "..."}]
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    document = relationship("Document", back_populates="insight")
