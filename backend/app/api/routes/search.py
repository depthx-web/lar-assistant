"""Search endpoints."""
from __future__ import annotations

import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.document_processing.embedder import DocumentEmbedder
from app.schemas.search import ChunkResult, SearchRequest, SearchResponse

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/search", response_model=SearchResponse, summary="Semantic search")
def search_documents(
    request: SearchRequest,
    db: Annotated[Session, Depends(get_db)],
) -> SearchResponse:
    """Search documents using semantic similarity.
    
    Requires Ollama to be running with nomic-embed-text model.
    """
    logger.info(f"Search query: {request.query[:50]}...")
    
    try:
        embedder = DocumentEmbedder(db)
        results = embedder.similarity_search(
            query=request.query,
            document_id=request.document_id,
            top_k=request.top_k,
        )
        
        chunk_results = [
            ChunkResult(
                chunk_id=chunk.chunk_id,
                document_id=chunk.document_id,
                content=chunk.content,
                similarity=similarity,
                page=chunk.page,
                section=chunk.section,
                source=chunk.source,
            )
            for chunk, similarity in results
        ]
        
        return SearchResponse(
            query=request.query,
            results=chunk_results,
            total=len(chunk_results),
        )
    
    except Exception as e:
        logger.exception(f"Search failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Search failed: {str(e)}. Ensure Ollama is running with nomic-embed-text model.",
        )
