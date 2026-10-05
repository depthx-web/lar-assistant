"""Document embedding generation."""
from __future__ import annotations

import json
import logging
from typing import List, Optional

from sqlalchemy.orm import Session

from app.ai.registry import get_provider
from app.models.document import DocumentChunk

logger = logging.getLogger(__name__)


class DocumentEmbedder:
    """Generate embeddings for document chunks."""

    def __init__(self, db: Session, model_name: str = "nomic-embed-text"):
        """Initialize embedder.
        
        Args:
            db: Database session
            model_name: Embedding model name
        """
        self.db = db
        self.model_name = model_name
        self.provider = get_provider("ollama")

    def embed_chunks(self, chunk_ids: List[int], batch_size: int = 10) -> int:
        """Generate embeddings for chunks.
        
        Args:
            chunk_ids: List of chunk IDs to embed
            batch_size: Batch size (currently processes sequentially)
        
        Returns:
            Number of chunks embedded
        """
        embedded_count = 0
        
        for chunk_id in chunk_ids:
            chunk = self.db.query(DocumentChunk).filter(DocumentChunk.id == chunk_id).first()
            if not chunk:
                logger.warning(f"Chunk {chunk_id} not found")
                continue
            
            try:
                # Generate embedding
                embedding = self.provider.embed(chunk.content, model=self.model_name)
                
                # Store as JSON
                chunk.embedding_vector = json.dumps(embedding)
                chunk.embedding_id = self.model_name
                self.db.commit()
                
                embedded_count += 1
                logger.debug(f"Embedded chunk {chunk_id}: {len(embedding)} dimensions")
                
            except Exception as e:
                logger.error(f"Failed to embed chunk {chunk_id}: {e}")
                self.db.rollback()
                continue
        
        logger.info(f"Embedded {embedded_count}/{len(chunk_ids)} chunks")
        return embedded_count

    def embed_text(self, text: str) -> Optional[List[float]]:
        """Generate embedding for a single text.
        
        Args:
            text: Text to embed
        
        Returns:
            Embedding vector or None on error
        """
        try:
            return self.provider.embed(text, model=self.model_name)
        except Exception as e:
            logger.error(f"Failed to embed text: {e}")
            return None

    def similarity_search(
        self,
        query: str,
        document_id: Optional[int] = None,
        top_k: int = 5
    ) -> List[tuple[DocumentChunk, float]]:
        """Find similar chunks using cosine similarity.
        
        Args:
            query: Query text
            document_id: Optional document ID to filter
            top_k: Number of results
        
        Returns:
            List of (chunk, similarity_score) tuples
        """
        # Embed query
        query_embedding = self.embed_text(query)
        if query_embedding is None:
            return []
        
        # Get all chunks with embeddings
        query_obj = self.db.query(DocumentChunk).filter(
            DocumentChunk.embedding_vector.isnot(None)
        )
        
        if document_id:
            query_obj = query_obj.filter(DocumentChunk.document_id == document_id)
        
        chunks = query_obj.all()
        
        if not chunks:
            logger.warning("No chunks with embeddings found")
            return []
        
        # Calculate cosine similarity
        results = []
        for chunk in chunks:
            try:
                chunk_embedding = json.loads(chunk.embedding_vector)
                similarity = self._cosine_similarity(query_embedding, chunk_embedding)
                results.append((chunk, similarity))
            except Exception as e:
                logger.warning(f"Failed to compare chunk {chunk.id}: {e}")
                continue
        
        # Sort by similarity descending
        results.sort(key=lambda x: x[1], reverse=True)
        
        return results[:top_k]

    @staticmethod
    def _cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity.
        
        Args:
            vec1: First vector
            vec2: Second vector
        
        Returns:
            Similarity score (0-1)
        """
        if len(vec1) != len(vec2):
            raise ValueError(f"Vector dimension mismatch: {len(vec1)} != {len(vec2)}")
        
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        magnitude1 = sum(a * a for a in vec1) ** 0.5
        magnitude2 = sum(b * b for b in vec2) ** 0.5
        
        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0
        
        return dot_product / (magnitude1 * magnitude2)
