"""Quick verification for Phase 6 - RAG Pipeline."""
from __future__ import annotations

import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "backend"))


def main():
    print("=== PHASE 6 VERIFICATION ===")
    
    try:
        # 1. Import RAG engine
        from app.rag.engine import RAGEngine
        print("✅ RAGEngine imported")
        
        # 2. Test prompt building
        class MockDB:
            pass
        
        engine = RAGEngine(MockDB())
        prompt = engine._build_prompt("Test question?", "Test context")
        assert "Test question" in prompt
        assert "Test context" in prompt
        assert "cite sources" in prompt.lower()
        print("✅ Prompt building works")
        
        # 3. Check schemas
        from app.schemas.rag import RAGRequest, RAGResponse, SourceInfo
        print("✅ RAG schemas imported")
        
        # 4. Check API routes
        from app.api.routes.rag import router
        print("✅ RAG router imported")
        
        # 5. Verify schema validation
        request = RAGRequest(
            question="What is machine learning?",
            top_k=5,
            temperature=0.7,
        )
        assert request.question == "What is machine learning?"
        assert request.top_k == 5
        print("✅ Schema validation works")
        
        print("\n[SUCCESS] PHASE 6 - All components working!")
        print("\nUsage:")
        print("  1. Upload document: POST /api/v1/documents")
        print("  2. Process: POST /api/v1/documents/{id}/process")
        print("  3. Ask question: POST /api/v1/rag/ask")
        print("\nRequirements:")
        print("  - Ollama with qwen2.5:3b-instruct and nomic-embed-text")
        return 0
        
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
