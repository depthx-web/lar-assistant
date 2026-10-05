"""Quick verification for Phase 5 - Text Chunking + Embeddings."""
from __future__ import annotations

import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "backend"))


def main():
    print("=== PHASE 5 VERIFICATION ===")
    
    try:
        # 1. Import chunker
        from app.document_processing.chunker import TextChunker
        print("✅ TextChunker imported")
        
        # 2. Import embedder
        from app.document_processing.embedder import DocumentEmbedder
        print("✅ DocumentEmbedder imported")
        
        # 3. Test chunking
        chunker = TextChunker(chunk_size=10, chunk_overlap=2)
        text = "This is a test sentence. " * 20
        chunks = chunker.chunk_text(text, document_id=1)
        assert len(chunks) > 0
        assert all("chunk_id" in c for c in chunks)
        print(f"✅ Chunking works ({len(chunks)} chunks created)")
        
        # 4. Test cosine similarity
        vec1 = [1.0, 0.0, 0.0]
        vec2 = [1.0, 0.0, 0.0]
        similarity = DocumentEmbedder._cosine_similarity(vec1, vec2)
        assert abs(similarity - 1.0) < 0.001
        print("✅ Cosine similarity works")
        
        # 5. Check schemas
        from app.schemas.search import SearchRequest, SearchResponse, ChunkResult
        print("✅ Search schemas imported")
        
        # 6. Check search endpoint
        from app.api.routes.search import router
        print("✅ Search router imported")
        
        # 7. Check model update
        from app.models.document import DocumentChunk
        assert hasattr(DocumentChunk, "embedding_vector")
        print("✅ DocumentChunk.embedding_vector field exists")
        
        print("\n[SUCCESS] PHASE 5 - All components working!")
        print("\nNote: Embedding generation requires Ollama with nomic-embed-text model.")
        print("      Run 'ollama pull nomic-embed-text' if not already installed.")
        return 0
        
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
