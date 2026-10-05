"""Quick verification for Phase 4 - PDF Extraction."""
from __future__ import annotations

import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "backend"))


def main():
    print("=== PHASE 4 VERIFICATION ===")
    
    try:
        # 1. Import extractor
        from app.document_processing.extractor import DocumentExtractor
        print("✅ DocumentExtractor imported")
        
        # 2. Import processor
        from app.document_processing.processor import DocumentProcessor
        print("✅ DocumentProcessor imported")
        
        # 3. Test metadata extraction
        sample_text = """
        A Study on Machine Learning
        
        Authors: John Doe, Jane Smith
        DOI: 10.1234/example.2024
        
        This is the abstract.
        """
        metadata = DocumentExtractor.extract_metadata_from_text(sample_text)
        assert metadata["title"] == "A Study on Machine Learning"
        assert metadata["doi"] == "10.1234/example.2024"
        print("✅ Metadata extraction works")
        
        # 4. Test TXT extraction
        import tempfile
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False, encoding="utf-8") as f:
            f.write("Test content\nLine 2")
            temp_path = Path(f.name)
        
        text = DocumentExtractor.extract_text(temp_path, "txt")
        assert "Test content" in text
        temp_path.unlink()
        print("✅ TXT extraction works")
        
        # 5. Check pdfplumber
        import pdfplumber
        print(f"✅ pdfplumber {pdfplumber.__version__} available")
        
        # 6. Check python-docx
        import docx
        print(f"✅ python-docx available")
        
        print("\n[SUCCESS] PHASE 4 - All components working!")
        return 0
        
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
