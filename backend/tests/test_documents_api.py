"""Tests for document upload API."""
from __future__ import annotations

import io
import tempfile
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.main import app

# Use main app's TestClient which uses the real database setup
client = TestClient(app)


def test_upload_pdf():
    """Test uploading a PDF file."""
    import time
    pdf_content = f"%PDF-1.4 fake pdf content {time.time()}".encode()
    files = {"file": ("test.pdf", io.BytesIO(pdf_content), "application/pdf")}
    
    response = client.post("/api/v1/documents", files=files)
    
    assert response.status_code == 200
    data = response.json()
    assert data["filename"] == "test.pdf"
    assert data["document_type"] == "pdf"
    assert data["size_bytes"] == len(pdf_content)
    assert data["processing_status"] == "PENDING"
    assert "file_hash" in data
    assert "id" in data


def test_():
    """Test uploading the same file twice (deduplication)."""
    content = b"test content for duplicate check"
    files = {"file": ("test.txt", io.BytesIO(content), "text/plain")}
    
    # First upload
    response1 = client.post("/api/v1/documents", files=files)
    assert response1.status_code == 200
    data1 = response1.json()
    doc_id_1 = data1["id"]
    file_hash_1 = data1["file_hash"]
    
    # Second upload (duplicate)
    files = {"file": ("test.txt", io.BytesIO(content), "text/plain")}
    response2 = client.post("/api/v1/documents", files=files)
    assert response2.status_code == 200
    data2 = response2.json()
    
    # Should return same document
    assert data2["id"] == doc_id_1
    assert data2["file_hash"] == file_hash_1
    assert data2["is_duplicate"] is True


def test_():
    """Test uploading unsupported file type."""
    files = {"file": ("test.zip", io.BytesIO(b"fake zip"), "application/zip")}
    
    response = client.post("/api/v1/documents", files=files)
    
    assert response.status_code == 400
    assert "Unsupported file type" in response.json()["detail"]


def test_():
    """Test uploading empty file."""
    files = {"file": ("empty.txt", io.BytesIO(b""), "text/plain")}
    
    response = client.post("/api/v1/documents", files=files)
    
    assert response.status_code == 400
    assert "Empty file" in response.json()["detail"]


def test_():
    """Test uploading file exceeding size limit."""
    # Create content larger than 20MB
    large_content = b"x" * (21 * 1024 * 1024)
    files = {"file": ("large.txt", io.BytesIO(large_content), "text/plain")}
    
    response = client.post("/api/v1/documents", files=files)
    
    assert response.status_code == 413
    assert "File too large" in response.json()["detail"]


def test_():
    """Test listing documents."""
    # Upload some documents
    for i in range(3):
        content = f"test content {i}".encode()
        files = {"file": (f"test{i}.txt", io.BytesIO(content), "text/plain")}
        client.post("/api/v1/documents", files=files)
    
    # List documents
    response = client.get("/api/v1/documents")
    
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 3
    assert len(data["documents"]) == 3


def test_():
    """Test getting document by ID."""
    # Upload
    content = b"test content"
    files = {"file": ("test.txt", io.BytesIO(content), "text/plain")}
    upload_response = client.post("/api/v1/documents", files=files)
    doc_id = upload_response.json()["id"]
    
    # Get
    response = client.get(f"/api/v1/documents/{doc_id}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == doc_id
    assert data["title"] == "test.txt"


def test_():
    """Test getting nonexistent document."""
    response = client.get("/api/v1/documents/9999")
    assert response.status_code == 404


def test_():
    """Test deleting document."""
    # Upload
    content = b"test content"
    files = {"file": ("test.txt", io.BytesIO(content), "text/plain")}
    upload_response = client.post("/api/v1/documents", files=files)
    doc_id = upload_response.json()["id"]
    
    # Delete
    response = client.delete(f"/api/v1/documents/{doc_id}")
    assert response.status_code == 200
    assert response.json()["deleted_id"] == doc_id
    
    # Verify deleted
    get_response = client.get(f"/api/v1/documents/{doc_id}")
    assert get_response.status_code == 404
