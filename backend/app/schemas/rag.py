"""RAG schemas."""
from __future__ import annotations

from typing import List, Optional
from pydantic import BaseModel, Field


class RAGRequest(BaseModel):
    """RAG question request."""
    question: str = Field(..., min_length=1, max_length=2000, description="User question")
    document_id: Optional[int] = Field(None, description="Filter by document ID")
    top_k: int = Field(5, ge=1, le=20, description="Number of context chunks")
    temperature: float = Field(0.7, ge=0.0, le=2.0, description="LLM temperature")
    model: Optional[str] = Field(None, description="Override default model")


class SourceInfo(BaseModel):
    """Source information."""
    source_id: int
    chunk_id: str
    document_id: int
    document_title: str
    similarity: float
    content_preview: str


class RAGResponse(BaseModel):
    """RAG answer response."""
    answer: str
    sources: List[SourceInfo]
    context_used: int
    model: str
    question: str
    error: Optional[str] = None
