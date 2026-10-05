"""Test PHASE 8: URL Ingestion

Tests URL fetching from different sources:
- DOI via CrossRef
- arXiv papers
- PubMed entries
- Generic URLs
"""
import asyncio
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.document_processing.url_fetcher import URLFetcher


async def test_url_fetcher():
    """Test URL fetcher with different sources."""
    print("=" * 60)
    print("PHASE 8: URL INGESTION - TEST")
    print("=" * 60)
    print()
    
    fetcher = URLFetcher()
    
    # Test cases
    test_urls = [
        ("DOI", "10.1038/nature12373"),
        ("arXiv", "https://arxiv.org/abs/1706.03762"),
        ("PubMed", "https://pubmed.ncbi.nlm.nih.gov/23223451/"),
    ]
    
    for source_type, url in test_urls:
        print(f"[TEST] Fetching {source_type}: {url}")
        print("-" * 60)
        
        try:
            metadata = await fetcher.fetch_paper(url)
            
            print(f"✓ Title: {metadata.title}")
            print(f"✓ Authors: {metadata.authors[:80] if metadata.authors else 'N/A'}...")
            print(f"✓ DOI: {metadata.doi or 'N/A'}")
            print(f"✓ Journal: {metadata.journal or 'N/A'}")
            print(f"✓ Year: {metadata.year or 'N/A'}")
            print(f"✓ Access Status: {metadata.access_status}")
            print(f"✓ PDF URL: {metadata.pdf_url or 'Not available'}")
            
            if metadata.abstract:
                print(f"✓ Abstract: {metadata.abstract[:100]}...")
            
            print()
            
        except Exception as e:
            print(f"✗ Failed: {e}")
            print()
    
    print("=" * 60)
    print("URL FETCHER TESTS COMPLETED")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_url_fetcher())
