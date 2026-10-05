from __future__ import annotations

import logging
from typing import List

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from app.ai.registry import get_provider
from app.core.config import settings
from app.schemas.chat import ChatMessage, ChatRequest, ChatResponse, ModelInfo

logger = logging.getLogger(__name__)

router = APIRouter(tags=["chat"])


@router.post("/chat", response_model=ChatResponse, summary="Chat completion (non-streaming)")
async def chat_completion(request: ChatRequest) -> ChatResponse:
    """Generate chat completion.
    
    Uses Ollama by default. Convert messages to prompt format.
    """
    if not request.messages:
        raise HTTPException(status_code=400, detail="messages cannot be empty")

    # Get provider
    try:
        provider = get_provider("ollama")(
            base_url=settings.ollama_base_url,
            default_model=settings.ollama_default_model,
        )
    except Exception as e:
        logger.error(f"Failed to initialize provider: {e}")
        raise HTTPException(status_code=500, detail="AI provider unavailable")

    # Convert messages to prompt (simple concatenation for now)
    system_msg = None
    user_msgs = []
    for msg in request.messages:
        if msg.role == "system":
            system_msg = msg.content
        elif msg.role == "user":
            user_msgs.append(msg.content)
        elif msg.role == "assistant":
            user_msgs.append(f"Assistant: {msg.content}")

    prompt = "\n".join(user_msgs)

    # Generate
    try:
        response_text = await provider.generate(
            prompt=prompt,
            model=request.model,
            system=system_msg,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
        )
    except Exception as e:
        logger.exception("Chat generation failed")
        raise HTTPException(status_code=500, detail=f"Generation failed: {str(e)}")

    return ChatResponse(
        message=ChatMessage(role="assistant", content=response_text),
        model=request.model or settings.ollama_default_model,
    )


@router.post("/chat/stream", summary="Chat completion (streaming)")
async def chat_completion_stream(request: ChatRequest):
    """Stream chat completion.
    
    Returns Server-Sent Events.
    """
    if not request.messages:
        raise HTTPException(status_code=400, detail="messages cannot be empty")

    try:
        provider = get_provider("ollama")(
            base_url=settings.ollama_base_url,
            default_model=settings.ollama_default_model,
        )
    except Exception as e:
        logger.error(f"Failed to initialize provider: {e}")
        raise HTTPException(status_code=500, detail="AI provider unavailable")

    # Convert messages
    system_msg = None
    user_msgs = []
    for msg in request.messages:
        if msg.role == "system":
            system_msg = msg.content
        elif msg.role == "user":
            user_msgs.append(msg.content)
        elif msg.role == "assistant":
            user_msgs.append(f"Assistant: {msg.content}")

    prompt = "\n".join(user_msgs)

    async def event_stream():
        try:
            async for chunk in provider.stream(
                prompt=prompt,
                model=request.model,
                system=system_msg,
                temperature=request.temperature,
                max_tokens=request.max_tokens,
            ):
                yield f"data: {chunk}\n\n"
            yield "data: [DONE]\n\n"
        except Exception as e:
            logger.exception("Stream failed")
            yield f"data: {{\"error\": \"{str(e)}\"}}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")


@router.get("/models", response_model=List[ModelInfo], summary="List available models")
async def list_models() -> List[ModelInfo]:
    """List models from all providers."""
    models: List[ModelInfo] = []

    # Ollama
    try:
        provider = get_provider("ollama")(
            base_url=settings.ollama_base_url,
            default_model=settings.ollama_default_model,
        )
        ollama_models = await provider.list_models()
        for name in ollama_models:
            models.append(ModelInfo(name=name, provider="ollama", available=True))
    except Exception as e:
        logger.warning(f"Failed to list Ollama models: {e}")

    return models
