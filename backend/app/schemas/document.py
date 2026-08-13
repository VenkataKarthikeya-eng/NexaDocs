from pydantic import BaseModel
from typing import List, Optional, Any
from datetime import datetime

class EntitySchema(BaseModel):
    name: str
    type: str
    detail: str

class HighlightSchema(BaseModel):
    page: int
    text: str

class DocumentResponse(BaseModel):
    id: str
    title: str
    filename: str
    fileSize: str
    pageCount: int
    chunkCount: int
    status: str
    processingProgress: int = 100
    category: str
    createdAt: str
    summary: Optional[str] = None
    topics: List[str] = []
    entities: List[EntitySchema] = []
    highlights: List[HighlightSchema] = []

    class Config:
        from_attributes = True

class DocumentListResponse(BaseModel):
    documents: List[DocumentResponse]
