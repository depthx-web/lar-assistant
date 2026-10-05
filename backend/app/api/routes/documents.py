from __future__ import annotations

import logging
from pathlib import Path
from typing import List

from fastapi import APIRouter, File, HTTPException, UploadFile, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.core.config import settings
from app.core.security import file_hash
from app.models.document import Document, ProcessingStatus
from app.schemas.document import (
    DocumentListResponse,
    DocumentMetadata,
    DocumentUploadResponse,
    URLIngestRequest,
    URLIngestResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter(tags=["documents"])

# Allowed MIME types
ALLOWED_TYPES = {
    "application/pdf": "pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "docx",
    "text/plain": "txt",
}

MAX_FILE_SIZE = 20 * 1024 * 1024  # 20MB


@router.post("/documents", response_model=DocumentUploadResponse, summary="Upload document")
async def upload_document(
    file: UploadFile = File(..., description="Document file (PDF, DOCX, TXT)"),
    db: Session = Depends(get_db),
) -> DocumentUploadResponse:
    """Upload a document.
    
    - Validates MIME type and size
    - Calculates SHA-256 hash
    - Deduplicates based on hash
    - Stores file in storage/documents/
    - Creates DB record
    
    Returns existing document if duplicate detected.
    """
    # Validate MIME type
    content_type = file.content_type or ""
    if content_type not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {content_type}. Allowed: PDF, DOCX, TXT",
        )

    doc_type = ALLOWED_TYPES[content_type]

    # Read file content
    try:
        content = await file.read()
    except Exception as e:
        logger.exception("Failed to read uploaded file")
        raise HTTPException(status_code=500, detail=f"Failed to read file: {str(e)}")

    # Validate size
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail=f"File too large: {len(content)} bytes (max: {MAX_FILE_SIZE})",
        )

    if len(content) == 0:
        raise HTTPException(status_code=400, detail="Empty file")

    # Calculate hash
    file_sha256 = file_hash(content)

    # Check for duplicate
    existing_doc = db.query(Document).filter(Document.file_hash == file_sha256).first()
    if existing_doc:
        logger.info(f"Duplicate upload detected: {file_sha256[:16]}... (doc_id={existing_doc.id})")
        return DocumentUploadResponse(
            id=existing_doc.id,
            file_hash=existing_doc.file_hash,
            filename=file.filename or "unknown",
            size_bytes=len(content),
            document_type=existing_doc.document_type,
            processing_status=existing_doc.processing_status,
            is_duplicate=True,
            created_at=existing_doc.created_at,
        )

    # Save file
    docs_dir = settings.resolved_documents_root
    docs_dir.mkdir(parents=True, exist_ok=True)
    file_path = docs_dir / f"{file_sha256}.{doc_type}"
    try:
        with open(file_path, "wb") as f:
            f.write(content)
    except Exception as e:
        logger.exception("Failed to write file to storage")
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")

    # Create DB record
    new_doc = Document(
        title=file.filename,
        local_path=str(file_path.relative_to(settings.resolved_storage_root)),
        file_hash=file_sha256,
        document_type=doc_type,
        processing_status=ProcessingStatus.PENDING.value,
    )
    db.add(new_doc)
    try:
        db.commit()
        db.refresh(new_doc)
    except Exception as e:
        logger.exception("Failed to save document to DB")
        try:
            file_path.unlink(missing_ok=True)
        except Exception:
            pass
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

    logger.info(f"Document uploaded: id={new_doc.id}, hash={file_sha256[:16]}...")
    return DocumentUploadResponse(
        id=new_doc.id,
        file_hash=new_doc.file_hash,
        filename=file.filename or "unknown",
        size_bytes=len(content),
        document_type=new_doc.document_type,
        processing_status=new_doc.processing_status,
        is_duplicate=False,
        created_at=new_doc.created_at,
    )

@router.get("/documents", response_model=DocumentListResponse, summary="List documents")
def list_documents(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
) -> DocumentListResponse:
    """List uploaded documents."""
    if limit > 100:
        limit = 100
    total = db.query(Document).count()
    documents = db.query(Document).order_by(Document.created_at.desc()).offset(skip).limit(limit).all()
    return DocumentListResponse(
        documents=[DocumentMetadata.model_validate(doc) for doc in documents],
        total=total,
    )


@router.get("/documents/{document_id}", response_model=DocumentMetadata, summary="Get document")
def get_document(document_id: int, db: Session = Depends(get_db)) -> DocumentMetadata:
    """Get document metadata by ID."""
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail=f"Document {document_id} not found")
    return DocumentMetadata.model_validate(doc)


@router.delete("/documents/{document_id}", summary="Delete document")
def delete_document(document_id: int, db: Session = Depends(get_db)) -> dict:
    """Delete document and its file."""
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail=f"Document {document_id} not found")
    if doc.local_path:
        file_path = settings.resolved_storage_root / doc.local_path
        try:
            file_path.unlink(missing_ok=True)
        except Exception as e:
            logger.warning(f"Failed to delete file {file_path}: {e}")
    db.delete(doc)
    try:
        db.commit()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    return {"status": "ok", "deleted_id": document_id}


@router.post("/documents/{document_id}/process", summary="Process document")
def process_document(
    document_id: int,
    db: Session = Depends(get_db),
) -> dict:
    """Trigger document processing (extract text, metadata, tables).
    
    This is synchronous for now. In production, use background tasks.
    """
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail=f"Document {document_id} not found")

    # Import here to avoid circular dependency
    from app.document_processing.processor import DocumentProcessor

    try:
        processor = DocumentProcessor(db)
        processor.process_document(document_id)
        return {"status": "ok", "document_id": document_id, "processing_status": "COMPLETED"}
    except Exception as e:
        logger.exception(f"Processing failed for document {document_id}")
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")



@router.post("/documents/from-url", response_model=URLIngestResponse, summary="Ingest paper from URL")
async def ingest_from_url(
    request: URLIngestRequest,
    db: Session = Depends(get_db),
) -> URLIngestResponse:
    """Ingest a paper from URL (DOI, arXiv, PubMed, or direct link).
    
    - Fetches metadata from public APIs (CrossRef, arXiv, PubMed)
    - Respects paywalls - does NOT attempt to bypass authentication
    - Downloads PDF only if freely available
    - Creates document record with metadata
    - Returns access status for transparency
    
    Examples:
    - DOI: https://doi.org/10.xxxx/xxxxx or 10.xxxx/xxxxx
    - arXiv: https://arxiv.org/abs/2301.12345
    - PubMed: https://pubmed.ncbi.nlm.nih.gov/12345678/
    """
    from app.document_processing.url_fetcher import URLFetcher
    
    logger.info(f"Ingesting paper from URL: {request.url}")
    
    # Fetch metadata
    fetcher = URLFetcher()
    try:
        metadata = await fetcher.fetch_paper(request.url)
    except Exception as e:
        logger.exception(f"Failed to fetch URL: {request.url}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch URL: {str(e)}")
    
    if not metadata.title and not metadata.doi:
        raise HTTPException(
            status_code=404,
            detail="Could not extract paper metadata from URL. The paper may not exist or the URL format is not supported."
        )
    
    # Check for PDF download
    pdf_content = None
    pdf_downloaded = False
    
    if request.auto_download_pdf and metadata.pdf_url and metadata.access_status == "open":
        logger.info(f"Attempting to download PDF from: {metadata.pdf_url}")
        try:
            pdf_content = await fetcher.download_pdf(metadata.pdf_url)
            if pdf_content:
                pdf_downloaded = True
                logger.info(f"PDF downloaded successfully: {len(pdf_content)} bytes")
        except Exception as e:
            logger.warning(f"Failed to download PDF: {e}")
    
    # Generate hash for deduplication
    if pdf_content:
        content_hash = file_hash(pdf_content)
    else:
        # Use metadata hash if no PDF available
        content_hash = fetcher.generate_content_hash(metadata)
    
    # Check for duplicate
    existing_doc = db.query(Document).filter(Document.file_hash == content_hash).first()
    if existing_doc:
        logger.info(f"Duplicate document detected: {content_hash[:16]}... (doc_id={existing_doc.id})")
        return URLIngestResponse(
            id=existing_doc.id,
            title=existing_doc.title,
            authors=existing_doc.authors,
            doi=existing_doc.doi,
            journal=existing_doc.journal,
            year=existing_doc.year,
            source_url=existing_doc.source_url or request.url,
            access_status=metadata.access_status,
            pdf_downloaded=bool(existing_doc.local_path),
            processing_status=existing_doc.processing_status,
            created_at=existing_doc.created_at,
        )
    
    # Save PDF if downloaded
    local_path = None
    if pdf_content:
        docs_dir = settings.resolved_documents_root
        docs_dir.mkdir(parents=True, exist_ok=True)
        file_path = docs_dir / f"{content_hash}.pdf"
        try:
            with open(file_path, "wb") as f:
                f.write(pdf_content)
            local_path = str(file_path.relative_to(settings.resolved_storage_root))
            logger.info(f"PDF saved to: {file_path}")
        except Exception as e:
            logger.exception("Failed to write PDF to storage")
            raise HTTPException(status_code=500, detail=f"Failed to save PDF: {str(e)}")
    
    # Create document record
    new_doc = Document(
        title=metadata.title or "Unknown Title",
        authors=metadata.authors,
        doi=metadata.doi,
        journal=metadata.journal,
        year=metadata.year,
        source_url=metadata.source_url or request.url,
        local_path=local_path,
        file_hash=content_hash,
        document_type="pdf" if pdf_downloaded else "url",
        processing_status=ProcessingStatus.PENDING.value if pdf_downloaded else ProcessingStatus.COMPLETED.value,
        doc_metadata=f'{{"abstract": "{metadata.abstract}", "access_status": "{metadata.access_status}"}}' if metadata.abstract else f'{{"access_status": "{metadata.access_status}"}}',
    )
    
    db.add(new_doc)
    try:
        db.commit()
        db.refresh(new_doc)
    except Exception as e:
        logger.exception("Failed to save document to DB")
        if local_path:
            try:
                file_path.unlink(missing_ok=True)
            except Exception:
                pass
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    
    logger.info(f"Document ingested from URL: id={new_doc.id}, access_status={metadata.access_status}")
    
    return URLIngestResponse(
        id=new_doc.id,
        title=new_doc.title,
        authors=new_doc.authors,
        doi=new_doc.doi,
        journal=new_doc.journal,
        year=new_doc.year,
        source_url=new_doc.source_url,
        access_status=metadata.access_status,
        pdf_downloaded=pdf_downloaded,
        processing_status=new_doc.processing_status,
        created_at=new_doc.created_at,
    )
