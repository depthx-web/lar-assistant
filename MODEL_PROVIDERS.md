# MODEL PROVIDERS

Abstraction: `backend/app/ai/base.py` — `LLMProvider`

Methods: `generate`, `stream`, `embed`, `health_check`, `list_models`. Unsupported -> raises `NotImplementedError` with clear message.

Built-in:
- `OllamaProvider` (default, local, Qwen2.5 3B Q4) — Phase 2 implements real HTTP
- Future: `OpenAIProvider`, `AnthropicProvider`, `LocalTransformersProvider`

Register:
```python
from app.ai.registry import register_provider
register_provider("myprovider", MyProvider)
```

Roles (ModelRecord.role): general_chat, literature_analysis, academic_writing, summarization, embedding, classification, journal_evaluation — no single model assumed for all.
