from __future__ import annotations

import hashlib
import re
from pathlib import Path

ALLOWED_EXTENSIONS = {".pdf"}
MAX_FILENAME_LEN = 255


def sanitize_filename(filename: str) -> str:
    """Prevent path traversal and normalize filename."""
    name = Path(filename).name
    name = re.sub(r"[^\w\-. ]", "_", name)
    name = re.sub(r"\s+", "_", name)
    name = name.strip("._")
    if not name:
        name = "document.pdf"
    if len(name) > MAX_FILENAME_LEN:
        stem = Path(name).stem[:200]
        name = stem + Path(name).suffix
    return name


def is_allowed_file(filename: str) -> bool:
    return Path(filename).suffix.lower() in ALLOWED_EXTENSIONS


def file_hash_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


# Alias for convenience
file_hash = file_hash_bytes


def file_hash_path(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()