"""Search schemas."""
from __future__ import annotations

from typing import List, Optional
from pydantic import BaseModel, Field


class SearchRequest(BaseModel):
    """Search request."""
    query: str = Field(..., min_length=1, max_length=1000, description="Search query")
    document_id: Optional[int] = Field(None, description="Filter by document ID")
    top_k: int = Field(5, ge=1, le=50, description="Number of results")


class ChunkResult(BaseModel):
    """Search result chunk."""
    chunk_id: str
    document_id: int
    content: str
    similarity: float
    page: Optional[int] = None
    section: Optional[str] = None
    source: Optional[str] = None


class SearchResponse(BaseModel):
    """Search response."""
    query: str
    results: List[ChunkResult]
    total: int
