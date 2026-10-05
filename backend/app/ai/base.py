from __future__ import annotations

from abc import ABC, abstractmethod
from typing import AsyncIterator, List, Optional


class LLMProvider(ABC):
    """Unified abstraction for all LLM/embedding providers.

    Requirement 5: every provider exposes generate/stream/embed/health_check/list_models.
    If unsupported -> raise NotImplementedError with clear message.
    """

    provider_name: str = "base"

    @abstractmethod
    async def generate(self, prompt: str, **kwargs) -> str:  # type: ignore
        raise NotImplementedError(f"{self.provider_name}: generate() not supported")

    @abstractmethod
    async def stream(self, prompt: str, **kwargs) -> AsyncIterator[str]:  # type: ignore
        raise NotImplementedError(f"{self.provider_name}: stream() not supported")
        # keep as async generator for typing
        if False:  # pragma: no cover
            yield ""

    @abstractmethod
    async def embed(self, texts: List[str], **kwargs) -> List[List[float]]:  # type: ignore
        raise NotImplementedError(f"{self.provider_name}: embed() not supported")

    @abstractmethod
    async def health_check(self) -> bool:
        raise NotImplementedError(f"{self.provider_name}: health_check() not supported")

    @abstractmethod
    async def list_models(self) -> List[str]:
        raise NotImplementedError(f"{self.provider_name}: list_models() not supported")
