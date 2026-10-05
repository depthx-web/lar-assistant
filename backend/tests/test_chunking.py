"""Tests for text chunking."""
from __future__ import annotations

import pytest

from app.document_processing.chunker import TextChunker


def test_chunk_simple_text():
    """Test chunking simple text."""
    chunker = TextChunker(chunk_size=10, chunk_overlap=2)
    
    text = "This is a test. " * 20  # Long text
    chunks = chunker.chunk_text(text, document_id=1)
    
    assert len(chunks) > 1
    assert all("chunk_id" in c for c in chunks)
    assert all("content" in c for c in chunks)
    assert all(c["document_id"] == 1 for c in chunks)


def test_chunk_paragraphs():
    """Test chunking with paragraphs."""
    chunker = TextChunker(chunk_size=20, chunk_overlap=5)
    
    text = """Paragraph 1 has some text here.
    
    Paragraph 2 has different text here.
    
    Paragraph 3 continues the story."""
    
    chunks = chunker.chunk_text(text, document_id=1)
    
    assert len(chunks) >= 1
    # Each chunk should have reasonable content
    assert all(len(c["content"].split()) > 0 for c in chunks)


def test_chunk_large_paragraph():
    """Test chunking a very large paragraph."""
    chunker = TextChunker(chunk_size=10, chunk_overlap=2)
    
    # Large paragraph with sentences
    text = "This is sentence one. This is sentence two. This is sentence three. " * 10
    
    chunks = chunker.chunk_text(text, document_id=1)
    
    # Should split into multiple chunks
    assert len(chunks) > 1
    # Each chunk should not exceed chunk_size significantly
    for chunk in chunks:
        word_count = len(chunk["content"].split())
        # Allow some flexibility due to sentence boundaries
        assert word_count <= chunker.chunk_size * 2


def test_chunk_id_generation():
    """Test chunk ID generation."""
    chunker = TextChunker()
    
    text = "Test text. " * 20
    chunks = chunker.chunk_text(text, document_id=1)
    
    # All chunk IDs should be unique
    chunk_ids = [c["chunk_id"] for c in chunks]
    assert len(chunk_ids) == len(set(chunk_ids))
    
    # Chunk IDs should be 16 char hex strings
    assert all(len(cid) == 16 for cid in chunk_ids)


def test_empty_text():
    """Test chunking empty text."""
    chunker = TextChunker()
    
    chunks = chunker.chunk_text("", document_id=1)
    
    assert len(chunks) == 0
