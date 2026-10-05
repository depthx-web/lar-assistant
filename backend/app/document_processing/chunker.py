"""Document chunking strategies."""
from __future__ import annotations

import hashlib
import re
from typing import List, Dict, Any


class TextChunker:
    """Semantic text chunking."""

    def __init__(self, chunk_size: int = 512, chunk_overlap: int = 50):
        """Initialize chunker.
        
        Args:
            chunk_size: Target chunk size in words
            chunk_overlap: Overlap between chunks in words
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk_text(self, text: str, document_id: int) -> List[Dict[str, Any]]:
        """Split text into semantic chunks.
        
        Args:
            text: Text to chunk
            document_id: Document ID for chunk IDs
        
        Returns:
            List of chunk dicts with content, chunk_id, etc.
        """
        # Split by paragraphs first
        paragraphs = self._split_paragraphs(text)
        
        chunks = []
        current_chunk = []
        current_word_count = 0
        
        for para in paragraphs:
            para_words = para.split()
            para_word_count = len(para_words)
            
            # If paragraph alone exceeds chunk_size, split it
            if para_word_count > self.chunk_size:
                # Save current chunk if exists
                if current_chunk:
                    chunks.append(" ".join(current_chunk))
                    current_chunk = []
                    current_word_count = 0
                
                # Split large paragraph
                chunks.extend(self._split_large_paragraph(para))
            
            # If adding this paragraph exceeds chunk_size, save current chunk
            elif current_word_count + para_word_count > self.chunk_size:
                if current_chunk:
                    chunks.append(" ".join(current_chunk))
                
                # Start new chunk with overlap
                if chunks and self.chunk_overlap > 0:
                    overlap_text = " ".join(current_chunk[-self.chunk_overlap:])
                    current_chunk = [overlap_text, para]
                    current_word_count = len(overlap_text.split()) + para_word_count
                else:
                    current_chunk = [para]
                    current_word_count = para_word_count
            else:
                # Add paragraph to current chunk
                current_chunk.append(para)
                current_word_count += para_word_count
        
        # Add remaining chunk
        if current_chunk:
            chunks.append(" ".join(current_chunk))
        
        # Generate chunk metadata
        return [
            {
                "chunk_id": self._generate_chunk_id(document_id, idx),
                "content": chunk,
                "document_id": document_id,
                "page": None,
                "section": None,
                "subsection": None,
                "source": f"chunk_{idx}",
            }
            for idx, chunk in enumerate(chunks)
        ]

    def _split_paragraphs(self, text: str) -> List[str]:
        """Split text into paragraphs.
        
        Args:
            text: Input text
        
        Returns:
            List of paragraphs
        """
        # Split by double newlines or more
        paragraphs = re.split(r"\n\s*\n+", text)
        # Filter empty and strip
        return [p.strip() for p in paragraphs if p.strip()]

    def _split_large_paragraph(self, paragraph: str) -> List[str]:
        """Split a large paragraph into sentence-based chunks.
        
        Args:
            paragraph: Large paragraph
        
        Returns:
            List of chunks
        """
        # Split by sentences
        sentences = re.split(r"(?<=[.!?])\s+", paragraph)
        
        chunks = []
        current_chunk = []
        current_word_count = 0
        
        for sentence in sentences:
            sentence_words = sentence.split()
            sentence_word_count = len(sentence_words)
            
            if current_word_count + sentence_word_count > self.chunk_size:
                if current_chunk:
                    chunks.append(" ".join(current_chunk))
                current_chunk = [sentence]
                current_word_count = sentence_word_count
            else:
                current_chunk.append(sentence)
                current_word_count += sentence_word_count
        
        if current_chunk:
            chunks.append(" ".join(current_chunk))
        
        return chunks

    def _generate_chunk_id(self, document_id: int, chunk_index: int) -> str:
        """Generate unique chunk ID.
        
        Args:
            document_id: Document ID
            chunk_index: Chunk index
        
        Returns:
            Chunk ID hash
        """
        raw_id = f"doc{document_id}_chunk{chunk_index}"
        return hashlib.sha256(raw_id.encode()).hexdigest()[:16]
