from __future__ import annotations

from typing import Dict, Type

from app.ai.base import LLMProvider

# Provider registry: no business logic depends on concrete provider.
_REGISTRY: Dict[str, Type[LLMProvider]] = {}


def register_provider(name: str, cls: Type[LLMProvider]) -> None:
    _REGISTRY[name.lower()] = cls


def get_provider_class(name: str) -> Type[LLMProvider]:
    """Get provider class by name.
    
    Alias: get_provider
    """
    key = name.lower()
    if key not in _REGISTRY:
        raise KeyError(f"Unknown provider '{name}'. Available: {list(_REGISTRY.keys())}")
    return _REGISTRY[key]


# Alias for convenience
get_provider = get_provider_class


def list_providers() -> list[str]:
    return sorted(_REGISTRY.keys())
