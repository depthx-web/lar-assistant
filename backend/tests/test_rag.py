"""Tests for RAG engine."""
from __future__ import annotations

import pytest

from app.rag.engine import RAGEngine


def test_build_prompt():
    """Test RAG prompt building."""
    # Mock db (not used in this test)
    class MockDB:
        pass
    
    engine = RAGEngine(MockDB())
    
    question = "What is machine learning?"
    context = "[Source 1] Machine learning is a field of AI."
    
    prompt = engine._build_prompt(question, context)
    
    assert "machine learning" in prompt.lower()
    assert "[Source 1]" in prompt
    assert "context" in prompt.lower()
    assert "question" in prompt.lower()
    assert "cite sources" in prompt.lower()


def test_empty_context():
    """Test behavior with no context."""
    # Test that engine handles no search results gracefully
    # This would be tested in integration tests
    pass
