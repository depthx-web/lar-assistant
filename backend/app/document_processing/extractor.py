"""Document text extraction."""
from __future__ import annotations

import logging
import re
from pathlib import Path
from typing import Dict, List, Optional

import pdfplumber
from docx import Document as DocxDocument

logger = logging.getLogger(__name__)


class DocumentExtractor:
    """Extract text, tables, and metadata from documents."""

    @staticmethod
    def extract_text_from_pdf(file_path: Path) -> str:
        """Extract text from PDF.
        
        Args:
            file_path: Path to PDF file
        
        Returns:
            Extracted text
        """
        try:
            text_parts = []
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text_parts.append(page_text)
            return "\n\n".join(text_parts)
        except Exception as e:
            logger.exception(f"Failed to extract text from PDF: {file_path}")
            raise ValueError(f"PDF extraction failed: {str(e)}")

    @staticmethod
    def extract_tables_from_pdf(file_path: Path) -> List[List[List[str]]]:
        """Extract tables from PDF.
        
        Args:
            file_path: Path to PDF file
        
        Returns:
            List of tables (each table is list of rows, each row is list of cells)
        """
        try:
            all_tables = []
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    tables = page.extract_tables()
                    if tables:
                        all_tables.extend(tables)
            return all_tables
        except Exception as e:
            logger.warning(f"Failed to extract tables from PDF: {e}")
            return []

    @staticmethod
    def extract_text_from_docx(file_path: Path) -> str:
        """Extract text from DOCX.
        
        Args:
            file_path: Path to DOCX file
        
        Returns:
            Extracted text
        """
        try:
            doc = DocxDocument(file_path)
            paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
            return "\n\n".join(paragraphs)
        except Exception as e:
            logger.exception(f"Failed to extract text from DOCX: {file_path}")
            raise ValueError(f"DOCX extraction failed: {str(e)}")

    @staticmethod
    def extract_text_from_txt(file_path: Path) -> str:
        """Extract text from TXT.
        
        Args:
            file_path: Path to TXT file
        
        Returns:
            File content
        """
        try:
            return file_path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            # Try with latin-1 as fallback
            return file_path.read_text(encoding="latin-1")
        except Exception as e:
            logger.exception(f"Failed to read TXT file: {file_path}")
            raise ValueError(f"TXT read failed: {str(e)}")

    @classmethod
    def extract_text(cls, file_path: Path, document_type: str) -> str:
        """Extract text based on document type.
        
        Args:
            file_path: Path to document
            document_type: Type (pdf, docx, txt)
        
        Returns:
            Extracted text
        """
        if document_type == "pdf":
            return cls.extract_text_from_pdf(file_path)
        elif document_type == "docx":
            return cls.extract_text_from_docx(file_path)
        elif document_type == "txt":
            return cls.extract_text_from_txt(file_path)
        else:
            raise ValueError(f"Unsupported document type: {document_type}")

    @staticmethod
    def extract_metadata_from_text(text: str) -> Dict[str, Optional[str]]:
        """Extract metadata from text (simple heuristics).
        
        Args:
            text: Document text
        
        Returns:
            Dict with title, authors, doi
        """
        metadata: Dict[str, Optional[str]] = {
            "title": None,
            "authors": None,
            "doi": None,
        }

        # Extract DOI (10.xxxx/yyyy pattern)
        doi_match = re.search(r"10\.\d{4,}/[\w\-\.]+", text)
        if doi_match:
            metadata["doi"] = doi_match.group(0)

        # Extract title (first non-empty line, max 200 chars)
        lines = [line.strip() for line in text.split("\n") if line.strip()]
        if lines:
            title = lines[0][:200]
            # Skip if looks like a header/footer
            if len(title.split()) > 2:
                metadata["title"] = title

        # Extract authors (look for "Author" or "by" patterns)
        author_patterns = [
            r"(?:Authors?|By)\s*:?\s*([^\n]{10,100})",
            r"^([A-Z][a-z]+ [A-Z][a-z]+(?:,\s*[A-Z][a-z]+ [A-Z][a-z]+)*)",
        ]
        for pattern in author_patterns:
            match = re.search(pattern, text, re.MULTILINE)
            if match:
                metadata["authors"] = match.group(1).strip()
                break

        return metadata
