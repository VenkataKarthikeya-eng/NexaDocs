from pydantic import BaseModel, ConfigDict
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
    errorMessage: Optional[str] = None
    category: str
    createdAt: str
    summary: Optional[str] = None
    topics: List[str] = []
    entities: List[EntitySchema] = []
    highlights: List[HighlightSchema] = []

    model_config = ConfigDict(from_attributes=True)


class DocumentListResponse(BaseModel):
    documents: List[DocumentResponse]
