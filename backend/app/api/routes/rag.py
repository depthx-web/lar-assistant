"""RAG endpoints."""
from __future__ import annotations

import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.rag.engine import RAGEngine
from app.schemas.rag import RAGRequest, RAGResponse

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/rag/ask", response_model=RAGResponse, summary="RAG question answering")
def ask_question(
    request: RAGRequest,
    db: Annotated[Session, Depends(get_db)],
) -> RAGResponse:
    """Ask a question and get an answer based on document context.
    
    Uses RAG (Retrieval-Augmented Generation):
    1. Retrieves relevant document chunks via semantic search
    2. Builds context from top-k chunks
    3. Generates answer using LLM with citations
    
    Requires:
    - Ollama running with qwen2.5:3b-instruct (or specified model)
    - Documents processed with embeddings
    """
    logger.info(f"RAG question: {request.question[:100]}...")
    
    try:
        model_name = request.model or "qwen2.5:3b-instruct"
        engine = RAGEngine(db, model_name=model_name)
        
        result = engine.ask(
            question=request.question,
            document_id=request.document_id,
            top_k=request.top_k,
            temperature=request.temperature,
        )
        
        return RAGResponse(**result)
    
    except Exception as e:
        logger.exception(f"RAG failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"RAG failed: {str(e)}. Ensure Ollama is running with required models.",
        )


@router.post("/rag/ask/stream", summary="RAG question answering (streaming)")
def ask_question_stream(
    request: RAGRequest,
    db: Annotated[Session, Depends(get_db)],
):
    """Ask a question and stream the answer.
    
    Same as /rag/ask but streams the response using Server-Sent Events.
    """
    logger.info(f"RAG streaming question: {request.question[:100]}...")
    
    try:
        model_name = request.model or "qwen2.5:3b-instruct"
        engine = RAGEngine(db, model_name=model_name)
        
        def generate():
            for chunk in engine.stream_answer(
                question=request.question,
                document_id=request.document_id,
                top_k=request.top_k,
                temperature=request.temperature,
            ):
                yield f"data: {chunk}\n\n"
        
        return StreamingResponse(generate(), media_type="text/event-stream")
    
    except Exception as e:
        logger.exception(f"RAG streaming failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"RAG streaming failed: {str(e)}",
        )
