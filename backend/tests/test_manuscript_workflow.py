"""Comprehensive test for Phase 8 manuscript system."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient
from app.main import app
import tempfile

client = TestClient(app)

def test_full_workflow():
    """Test complete manuscript analysis workflow."""
    print("\n" + "="*60)
    print("PHASE 8: MANUSCRIPT ANALYSIS - COMPREHENSIVE TEST")
    print("="*60)
    
    # Step 1: Upload and process document
    print("\n[1/6] Uploading test document...")
    test_content = """Abstract
    
This is a comprehensive test paper about machine learning. It includes abstract, introduction, methods, results, and conclusion sections with proper structure.

Keywords: machine learning, testing, research, methodology

Introduction

Machine learning has revolutionized computational research. This paper explores novel approaches to testing methodologies.

Methods

We employed Python 3.9 for all analyses. Data was collected from three independent sources. Statistical analysis was performed using standard techniques.

Results

The results demonstrate significant improvements over baseline methods. Performance metrics showed a 25% increase in accuracy.

Discussion

These findings have important implications for future research directions.

Conclusion

This study contributes to the field by providing new insights into testing methodologies.

References

[1] Smith, J. (2020). Machine Learning Methods. Journal of AI Research, 15(2), 123-145.
[2] Doe, A. (2021). Testing Frameworks. Conference on Software Engineering, pp. 234-256.
[3] Johnson, M. (2019). Statistical Analysis Techniques. Data Science Quarterly, 8(4), 567-589.
"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write(test_content)
        test_file = f.name
    
    try:
        with open(test_file, 'rb') as f:
            response = client.post("/api/v1/documents", files={"file": ("test_paper.txt", f, "text/plain")})
        
        if response.status_code != 200:
            print(f"Upload failed: {response.status_code}")
            return False
        
        doc_data = response.json()
        document_id = doc_data["id"]
        print(f"Document uploaded: ID={document_id}")
        
        # Step 2: Process document
        print("\n[2/6] Processing document...")
        response = client.post(f"/api/v1/documents/{document_id}/process")
        if response.status_code != 200:
            print(f"Processing failed: {response.status_code}")
            return False
        print(f"Document processed")
        
        # Step 3: Load journals
        print("\n[3/6] Loading journal profiles...")
        response = client.post("/api/v1/journals/load")
        if response.status_code != 200:
            print(f"Journal loading failed: {response.status_code}")
            return False
        
        journals_loaded = response.json()
        print(f"Loaded {journals_loaded.get('loaded_count', 0)} journal(s)")
        
        # Step 4: Get journal list
        print("\n[4/6] Fetching journal list...")
        response = client.get("/api/v1/journals")
        if response.status_code != 200:
            print(f"Journal list failed: {response.status_code}")
            return False
        
        journals_data = response.json()
        if not journals_data["journals"]:
            print("No journals found")
            return False
        
        journal_id = journals_data["journals"][0]["id"]
        journal_name = journals_data["journals"][0]["name"]
        print(f"Found journal: {journal_name} (ID={journal_id})")
        
        # Step 5: Create manuscript
        print("\n[5/6] Creating manuscript...")
        response = client.post(
            "/api/v1/manuscripts",
            json={
                "title": "Comprehensive Test Manuscript",
                "document_id": document_id,
                "journal_id": journal_id,
            }
        )
        if response.status_code != 200:
            print(f"Manuscript creation failed: {response.status_code}")
            return False
        
        manuscript_data = response.json()
        manuscript_id = manuscript_data["id"]
        print(f"Manuscript created: ID={manuscript_id}")
        
        # Step 6: Analyze manuscript
        print("\n[6/6] Analyzing manuscript compliance...")
        response = client.post(f"/api/v1/manuscripts/{manuscript_id}/analyze")
        if response.status_code != 200:
            print(f"Analysis failed: {response.status_code}")
            return False
        
        analysis_data = response.json()
        
        print(f"\n{'='*60}")
        print("ANALYSIS RESULTS")
        print(f"{'='*60}")
        print(f"Status: {analysis_data.get('analysis_status')}")
        print(f"Overall Compliance: {analysis_data.get('overall_score', 0):.1%}")
        print(f"Requirements Checked: {len(analysis_data.get('requirement_checks', []))}")
        
        print(f"\n{'='*60}")
        print("ALL TESTS PASSED - PHASE 8 COMPLETE")
        print(f"{'='*60}\n")
        
        return True
        
    except Exception as e:
        print(f"\nTest failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        if os.path.exists(test_file):
            os.unlink(test_file)

if __name__ == "__main__":
    success = test_full_workflow()
    sys.exit(0 if success else 1)