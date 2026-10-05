"""Integration tests for Ollama provider.

These tests require Ollama to be running on localhost:11434.
Skip if not available.
"""
from __future__ import annotations

import pytest

from app.ai.ollama_provider import OllamaProvider


@pytest.fixture
async def ollama_provider():
    """Ollama provider fixture."""
    provider = OllamaProvider()
    # Check if available
    is_available = await provider.health_check()
    if not is_available:
        pytest.skip("Ollama not available at localhost:11434")
    return provider


@pytest.mark.asyncio
async def test_ollama_health_check():
    """Test Ollama health check."""
    provider = OllamaProvider()
    result = await provider.health_check()
    # Can be True or False depending on whether Ollama is running
    assert isinstance(result, bool)


@pytest.mark.asyncio
async def test_ollama_list_models(ollama_provider: OllamaProvider):
    """Test listing models."""
    models = await ollama_provider.list_models()
    assert isinstance(models, list)
    # Should have at least one model if Ollama is set up
    # (test is skipped if Ollama not available)


@pytest.mark.asyncio
async def test_ollama_generate(ollama_provider: OllamaProvider):
    """Test text generation."""
    response = await ollama_provider.generate(
        prompt="Say 'test' and nothing else.",
        temperature=0.1,
        max_tokens=10,
    )
    assert isinstance(response, str)
    assert len(response) > 0


@pytest.mark.asyncio
async def test_ollama_stream(ollama_provider: OllamaProvider):
    """Test streaming generation."""
    chunks = []
    async for chunk in ollama_provider.stream(
        prompt="Count to 3.",
        temperature=0.1,
        max_tokens=20,
    ):
        chunks.append(chunk)
    
    assert len(chunks) > 0
    full_response = "".join(chunks)
    assert len(full_response) > 0


@pytest.mark.asyncio
async def test_ollama_embed(ollama_provider: OllamaProvider):
    """Test embeddings generation.
    
    This test requires nomic-embed-text model.
    Skip if model not available.
    """
    models = await ollama_provider.list_models()
    if "nomic-embed-text" not in models:
        pytest.skip("nomic-embed-text model not installed")
    
    embeddings = await ollama_provider.embed(
        texts=["Hello world", "Test embedding"],
        model="nomic-embed-text",
    )
    
    assert len(embeddings) == 2
    assert all(isinstance(emb, list) for emb in embeddings)
    assert all(len(emb) > 0 for emb in embeddings)
    # nomic-embed-text produces 768-dim vectors
    assert all(len(emb) == 768 for emb in embeddings)
