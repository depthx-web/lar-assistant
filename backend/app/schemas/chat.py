from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    """Single chat message."""
    role: str = Field(..., description="Message role: system, user, or assistant")
    content: str = Field(..., description="Message content")


class ChatRequest(BaseModel):
    """Chat completion request."""
    messages: List[ChatMessage] = Field(..., description="Conversation history")
    model: Optional[str] = Field(None, description="Model name (uses default if omitted)")
    temperature: float = Field(0.7, ge=0.0, le=2.0, description="Sampling temperature")
    max_tokens: Optional[int] = Field(None, ge=1, description="Max tokens to generate")
    stream: bool = Field(False, description="Stream response")


class ChatResponse(BaseModel):
    """Chat completion response (non-streaming)."""
    message: ChatMessage = Field(..., description="Assistant's response")
    model: str = Field(..., description="Model used")
    prompt_tokens: Optional[int] = Field(None, description="Tokens in prompt (if available)")
    completion_tokens: Optional[int] = Field(None, description="Tokens in completion (if available)")


class ModelInfo(BaseModel):
    """Model metadata."""
    name: str = Field(..., description="Model name")
    provider: str = Field(..., description="Provider (e.g., ollama)")
    available: bool = Field(..., description="Is model currently available")
