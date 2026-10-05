from pathlib import Path
from app.core.security import sanitize_filename, is_allowed_file, file_hash_bytes


def test_sanitize_traversal():
    assert sanitize_filename("../../etc/passwd.pdf") == "passwd.pdf"
    assert sanitize_filename("../../../a/b/c.pdf") == "c.pdf"


def test_sanitize_empty():
    assert sanitize_filename("...") == "document.pdf"


def test_is_allowed():
    assert is_allowed_file("paper.pdf")
    assert not is_allowed_file("paper.docx")
    assert not is_allowed_file("paper.PDF") is False  # case insensitive -> should be allowed
    assert is_allowed_file("paper.PDF")


def test_hash_deterministic():
    assert file_hash_bytes(b"hello") == file_hash_bytes(b"hello")
    assert file_hash_bytes(b"hello") != file_hash_bytes(b"world")
