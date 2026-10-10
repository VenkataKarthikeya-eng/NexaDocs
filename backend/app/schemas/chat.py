from pydantic import BaseModel
from typing import List, Optional, Any

class SourceCitation(BaseModel):
    page: int
    section: str
    relevance_score: float
    snippet: Optional[str] = None

class ChatRequest(BaseModel):
    document_id: str
    question: str

class ChatResponse(BaseModel):
    id: str
    sender: str = "assistant"
    question: str
    answer: str
    timestamp: str
    sources: List[SourceCitation] = []

class AnalyzeRequest(BaseModel):
    document_id: str

class InsightResponse(BaseModel):
    document_id: str
    summary: str
    topics: List[str] = []
    entities: List[Any] = []
    key_takeaways: List[Any] = []
