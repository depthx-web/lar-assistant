"""Tests for embeddings."""
from __future__ import annotations

import pytest

from app.document_processing.embedder import DocumentEmbedder


def test_cosine_similarity():
    """Test cosine similarity calculation."""
    # Identical vectors
    vec1 = [1.0, 0.0, 0.0]
    vec2 = [1.0, 0.0, 0.0]
    similarity = DocumentEmbedder._cosine_similarity(vec1, vec2)
    assert abs(similarity - 1.0) < 0.001
    
    # Orthogonal vectors
    vec3 = [1.0, 0.0, 0.0]
    vec4 = [0.0, 1.0, 0.0]
    similarity = DocumentEmbedder._cosine_similarity(vec3, vec4)
    assert abs(similarity - 0.0) < 0.001
    
    # Opposite vectors
    vec5 = [1.0, 0.0, 0.0]
    vec6 = [-1.0, 0.0, 0.0]
    similarity = DocumentEmbedder._cosine_similarity(vec5, vec6)
    assert abs(similarity - (-1.0)) < 0.001


def test_cosine_similarity_dimension_mismatch():
    """Test cosine similarity with mismatched dimensions."""
    vec1 = [1.0, 0.0]
    vec2 = [1.0, 0.0, 0.0]
    
    with pytest.raises(ValueError, match="dimension mismatch"):
        DocumentEmbedder._cosine_similarity(vec1, vec2)


def test_cosine_similarity_zero_vector():
    """Test cosine similarity with zero vectors."""
    vec1 = [0.0, 0.0, 0.0]
    vec2 = [1.0, 0.0, 0.0]
    similarity = DocumentEmbedder._cosine_similarity(vec1, vec2)
    assert similarity == 0.0
