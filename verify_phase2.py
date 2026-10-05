"""Quick verification script for Phase 2."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "backend"))

from app.ai.ollama_provider import OllamaProvider
from app.schemas.chat import ChatMessage, ChatRequest, ChatResponse, ModelInfo

print("[OK] OllamaProvider imported")
print("[OK] Chat schemas imported")

provider = OllamaProvider()
print(f"[OK] Provider initialized: {provider.provider_name} @ {provider.base_url}")
print(f"     Default model: {provider.default_model}")

# Test schemas
req = ChatRequest(messages=[ChatMessage(role="user", content="test")])
print(f"[OK] ChatRequest validated: {len(req.messages)} messages")

print("\n[SUCCESS] PHASE 2 - All imports and basic initialization working!")
