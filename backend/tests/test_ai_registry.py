import pytest
from app.ai.registry import list_providers, get_provider_class
from app.ai.base import LLMProvider


def test_registry_has_ollama():
    assert "ollama" in list_providers()
    cls = get_provider_class("ollama")
    assert issubclass(cls, LLMProvider)


def test_unknown_provider_raises():
    with pytest.raises(KeyError):
        get_provider_class("does_not_exist")


@pytest.mark.asyncio
async def test_llmprovider_raises_when_not_implemented():
    class Dummy(LLMProvider):
        provider_name = "dummy"

        async def generate(self, prompt, **kwargs):  # type: ignore
            return await super().generate(prompt, **kwargs)

        async def stream(self, prompt, **kwargs):  # type: ignore
            async for x in super().stream(prompt, **kwargs):
                yield x

        async def embed(self, texts, **kwargs):  # type: ignore
            return await super().embed(texts, **kwargs)

        async def health_check(self):  # type: ignore
            return await super().health_check()

        async def list_models(self):  # type: ignore
            return await super().list_models()

    d = Dummy()
    with pytest.raises(NotImplementedError):
        await d.generate("hi")
    with pytest.raises(NotImplementedError):
        await d.embed(["hi"])
