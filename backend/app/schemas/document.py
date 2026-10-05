from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class DocumentUploadResponse(BaseModel):
    """Response after document upload."""
    id: int = Field(..., description="Document ID")
    file_hash: str = Field(..., description="SHA-256 hash")
    filename: str = Field(..., description="Original filename")
    size_bytes: int = Field(..., description="File size in bytes")
    document_type: str = Field(..., description="Document type (pdf, docx, txt)")
    processing_status: str = Field(..., description="Processing status")
    is_duplicate: bool = Field(..., description="Whether this was a duplicate upload")
    created_at: datetime = Field(..., description="Upload timestamp")


class DocumentMetadata(BaseModel):
    """Document metadata."""
    id: int
    title: Optional[str] = None
    authors: Optional[str] = None
    doi: Optional[str] = None
    journal: Optional[str] = None
    year: Optional[int] = None
    source_url: Optional[str] = None
    local_path: Optional[str] = None
    file_hash: str
    document_type: str
    processing_status: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class DocumentListResponse(BaseModel):
    """List of documents."""
    documents: list[DocumentMetadata]
    total: int


class URLIngestRequest(BaseModel):
    """Request to ingest paper from URL."""
    url: str = Field(..., description="Paper URL (DOI, arXiv, PubMed, or direct link)")
    auto_download_pdf: bool = Field(default=True, description="Automatically download PDF if available")


class URLIngestResponse(BaseModel):
    """Response after URL ingestion."""
    id: int = Field(..., description="Document ID")
    title: Optional[str] = None
    authors: Optional[str] = None
    doi: Optional[str] = None
    journal: Optional[str] = None
    year: Optional[int] = None
    source_url: str
    access_status: str = Field(..., description="Access status: open, restricted, paywall, unknown")
    pdf_downloaded: bool = Field(..., description="Whether PDF was downloaded")
    processing_status: str
    created_at: datetime
