from __future__ import annotations

import json
import logging
from typing import Any, AsyncIterator, Dict, List, Optional

import httpx

from app.ai.base import LLMProvider
from app.ai.registry import register_provider

logger = logging.getLogger(__name__)


class OllamaProvider(LLMProvider):
    """Ollama API provider (localhost:11434).
    
    API reference: https://github.com/ollama/ollama/blob/main/docs/api.md
    """
    provider_name = "ollama"

    def __init__(self, base_url: str = "http://localhost:11434", default_model: str = "qwen2.5:3b-instruct"):
        self.base_url = base_url.rstrip("/")
        self.default_model = default_model

    async def generate(
        self,
        prompt: str,
        model: Optional[str] = None,
        system: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs: Any,
    ) -> str:
        """Generate completion (non-streaming).
        
        Args:
            prompt: User prompt
            model: Model name (defaults to self.default_model)
            system: System prompt
            temperature: Sampling temperature
            max_tokens: Max tokens (maps to num_predict)
            **kwargs: Additional Ollama options
        
        Returns:
            Generated text
        
        Raises:
            httpx.HTTPError: On connection/HTTP errors
        """
        model = model or self.default_model
        payload: Dict[str, Any] = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
            },
        }
        if system:
            payload["system"] = system
        if max_tokens:
            payload["options"]["num_predict"] = max_tokens
        # Merge additional options
        if kwargs:
            payload["options"].update(kwargs)

        logger.debug(f"Ollama generate: model={model}, prompt_len={len(prompt)}")
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(f"{self.base_url}/api/generate", json=payload)
            response.raise_for_status()
            data = response.json()
            return data.get("response", "")

    async def stream(
        self,
        prompt: str,
        model: Optional[str] = None,
        system: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs: Any,
    ) -> AsyncIterator[str]:
        """Generate completion (streaming).
        
        Yields:
            Incremental text chunks
        """
        model = model or self.default_model
        payload: Dict[str, Any] = {
            "model": model,
            "prompt": prompt,
            "stream": True,
            "options": {
                "temperature": temperature,
            },
        }
        if system:
            payload["system"] = system
        if max_tokens:
            payload["options"]["num_predict"] = max_tokens
        if kwargs:
            payload["options"].update(kwargs)

        logger.debug(f"Ollama stream: model={model}, prompt_len={len(prompt)}")
        async with httpx.AsyncClient(timeout=120.0) as client:
            async with client.stream("POST", f"{self.base_url}/api/generate", json=payload) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if line.strip():
                        try:
                            chunk = json.loads(line)
                            if "response" in chunk:
                                yield chunk["response"]
                        except json.JSONDecodeError:
                            logger.warning(f"Invalid JSON chunk: {line}")
                            continue

    async def embed(
        self,
        texts: List[str],
        model: str = "nomic-embed-text",
        **kwargs: Any,
    ) -> List[List[float]]:
        """Generate embeddings.
        
        Args:
            texts: List of texts to embed
            model: Embedding model (default: nomic-embed-text)
            **kwargs: Additional options
        
        Returns:
            List of embedding vectors
        """
        logger.debug(f"Ollama embed: model={model}, count={len(texts)}")
        embeddings: List[List[float]] = []
        async with httpx.AsyncClient(timeout=60.0) as client:
            for text in texts:
                payload = {"model": model, "input": text}
                if kwargs:
                    payload.update(kwargs)
                response = await client.post(f"{self.base_url}/api/embed", json=payload)
                response.raise_for_status()
                data = response.json()
                # Ollama returns {"embeddings": [[...]]} or {"embedding": [...]}
                if "embeddings" in data and data["embeddings"]:
                    embeddings.append(data["embeddings"][0])
                elif "embedding" in data:
                    embeddings.append(data["embedding"])
                else:
                    raise ValueError(f"Unexpected embed response: {data}")
        return embeddings

    async def health_check(self) -> bool:
        """Check if Ollama is reachable."""
        try:
            async with httpx.AsyncClient(timeout=2.0) as client:
                r = await client.get(f"{self.base_url}/api/tags")
                return r.status_code == 200
        except Exception as e:
            logger.debug(f"Ollama health_check failed: {e}")
            return False

    async def list_models(self) -> List[str]:
        """List installed models.
        
        Returns:
            List of model names (e.g., ["qwen2.5:3b-instruct", "nomic-embed-text"])
        """
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.base_url}/api/tags")
                response.raise_for_status()
                data = response.json()
                # Response: {"models": [{"name": "...", ...}, ...]}
                models = data.get("models", [])
                return [m["name"] for m in models if "name" in m]
        except Exception as e:
            logger.warning(f"Failed to list Ollama models: {e}")
            return []


register_provider("ollama", OllamaProvider)
