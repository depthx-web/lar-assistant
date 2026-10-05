"""Tests for chat API endpoints."""
from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_chat_completion_validation():
    """Test chat request validation."""
    # Empty messages
    response = client.post("/api/v1/chat", json={"messages": []})
    assert response.status_code == 400

    # Invalid role
    response = client.post(
        "/api/v1/chat",
        json={
            "messages": [{"role": "invalid", "content": "test"}],
        },
    )
    # Should still process (we don't validate role strictly yet)
    # but will fail at provider level if provider unavailable


@pytest.mark.asyncio
async def test_chat_completion_mock():
    """Test chat completion with mocked provider."""
    mock_provider = AsyncMock()
    mock_provider.generate = AsyncMock(return_value="Mock response")

    with patch("app.api.routes.chat.get_provider") as mock_get:
        mock_get.return_value = lambda **kwargs: mock_provider

        response = client.post(
            "/api/v1/chat",
            json={
                "messages": [
                    {"role": "user", "content": "Hello"},
                ],
                "temperature": 0.5,
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["message"]["role"] == "assistant"
        assert data["message"]["content"] == "Mock response"
        assert "model" in data


def test_list_models():
    """Test models listing endpoint."""
    response = client.get("/api/v1/models")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    # May be empty if Ollama not running
