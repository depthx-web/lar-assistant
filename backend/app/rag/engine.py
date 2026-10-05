"""RAG (Retrieval-Augmented Generation) engine."""
from __future__ import annotations

import logging
from typing import List, Optional, Dict, Any

from sqlalchemy.orm import Session

from app.ai.registry import get_provider
from app.document_processing.embedder import DocumentEmbedder
from app.models.document import Document

logger = logging.getLogger(__name__)


class RAGEngine:
    """RAG engine for question answering."""

    def __init__(self, db: Session, model_name: str = "qwen2.5:3b-instruct"):
        """Initialize RAG engine.
        
        Args:
            db: Database session
            model_name: LLM model name for generation
        """
        self.db = db
        self.model_name = model_name
        self.provider = get_provider("ollama")
        self.embedder = DocumentEmbedder(db)

    def ask(
        self,
        question: str,
        document_id: Optional[int] = None,
        top_k: int = 5,
        temperature: float = 0.7,
    ) -> Dict[str, Any]:
        """Ask a question and get an answer with sources.
        
        Args:
            question: User question
            document_id: Optional document ID to filter
            top_k: Number of context chunks to retrieve
            temperature: LLM temperature
        
        Returns:
            Dict with answer, sources, and metadata
        """
        logger.info(f"RAG question: {question[:100]}...")
        
        # Step 1: Retrieve relevant context
        search_results = self.embedder.similarity_search(
            query=question,
            document_id=document_id,
            top_k=top_k,
        )
        
        if not search_results:
            return {
                "answer": "I couldn't find any relevant information to answer your question. Please make sure documents are uploaded and processed.",
                "sources": [],
                "context_used": 0,
                "model": self.model_name,
            }
        
        logger.info(f"Retrieved {len(search_results)} context chunks")
        
        # Step 2: Build context from chunks
        context_chunks = []
        sources = []
        
        for idx, (chunk, similarity) in enumerate(search_results):
            # Get document info
            doc = self.db.query(Document).filter(Document.id == chunk.document_id).first()
            doc_title = doc.title if doc else f"Document {chunk.document_id}"
            
            context_chunks.append(f"[Source {idx + 1}] {chunk.content}")
            
            sources.append({
                "source_id": idx + 1,
                "chunk_id": chunk.chunk_id,
                "document_id": chunk.document_id,
                "document_title": doc_title,
                "similarity": round(similarity, 3),
                "content_preview": chunk.content[:200] + "..." if len(chunk.content) > 200 else chunk.content,
            })
        
        context_text = "\n\n".join(context_chunks)
        
        # Step 3: Build prompt
        prompt = self._build_prompt(question, context_text)
        
        # Step 4: Generate answer
        try:
            answer = self.provider.generate(
                prompt=prompt,
                model=self.model_name,
                temperature=temperature,
                max_tokens=1000,
            )
            
            logger.info(f"Answer generated: {len(answer)} chars")
            
            return {
                "answer": answer.strip(),
                "sources": sources,
                "context_used": len(context_chunks),
                "model": self.model_name,
                "question": question,
            }
        
        except Exception as e:
            logger.exception(f"Failed to generate answer: {e}")
            return {
                "answer": f"Error generating answer: {str(e)}",
                "sources": sources,
                "context_used": len(context_chunks),
                "model": self.model_name,
                "error": str(e),
            }

    def _build_prompt(self, question: str, context: str) -> str:
        """Build RAG prompt.
        
        Args:
            question: User question
            context: Retrieved context
        
        Returns:
            Formatted prompt
        """
        return f"""You are an academic research assistant. Answer the user's question based ONLY on the provided context. If the context doesn't contain enough information, say so clearly.

Context:
{context}

Question: {question}

Instructions:
- Answer based strictly on the provided context
- Cite sources using [Source N] notation
- If information is insufficient, state that clearly
- Be precise and academic in your response
- Do not add information not present in the context

Answer:"""

    def stream_answer(
        self,
        question: str,
        document_id: Optional[int] = None,
        top_k: int = 5,
        temperature: float = 0.7,
    ):
        """Stream answer generation.
        
        Args:
            question: User question
            document_id: Optional document ID
            top_k: Number of context chunks
            temperature: LLM temperature
        
        Yields:
            Answer chunks
        """
        # Retrieve context
        search_results = self.embedder.similarity_search(
            query=question,
            document_id=document_id,
            top_k=top_k,
        )
        
        if not search_results:
            yield "I couldn't find any relevant information to answer your question."
            return
        
        # Build context
        context_chunks = []
        for idx, (chunk, _) in enumerate(search_results):
            context_chunks.append(f"[Source {idx + 1}] {chunk.content}")
        
        context_text = "\n\n".join(context_chunks)
        prompt = self._build_prompt(question, context_text)
        
        # Stream answer
        try:
            for chunk in self.provider.stream(
                prompt=prompt,
                model=self.model_name,
                temperature=temperature,
                max_tokens=1000,
            ):
                yield chunk
        except Exception as e:
            logger.exception(f"Streaming failed: {e}")
            yield f"\n\nError: {str(e)}"

