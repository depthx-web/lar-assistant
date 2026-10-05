"""Document processing service."""
from __future__ import annotations

import logging
from pathlib import Path

from sqlalchemy.orm import Session

from app.core.config import settings
from app.document_processing.extractor import DocumentExtractor
from app.models.document import Document, ProcessingStatus

logger = logging.getLogger(__name__)


class DocumentProcessor:
    """Process uploaded documents."""

    def __init__(self, db: Session):
        self.db = db
        self.extractor = DocumentExtractor()

    def process_document(self, document_id: int) -> None:
        """Process a document: extract text, tables, metadata.
        
        Args:
            document_id: Document ID to process
        """
        doc = self.db.query(Document).filter(Document.id == document_id).first()
        if not doc:
            logger.error(f"Document {document_id} not found")
            return

        logger.info(f"Processing document {document_id}: {doc.title}")

        try:
            # Update status
            doc.processing_status = ProcessingStatus.PROCESSING.value
            self.db.commit()

            # Get file path
            if not doc.local_path:
                raise ValueError("Document has no local_path")
            
            file_path = settings.resolved_storage_root / doc.local_path
            if not file_path.exists():
                raise FileNotFoundError(f"File not found: {file_path}")

            # Extract text
            logger.debug(f"Extracting text from {file_path}")
            text = self.extractor.extract_text(file_path, doc.document_type)
            
            if not text or len(text.strip()) < 10:
                logger.warning(f"Document {document_id} has very little text")
                doc.processing_status = ProcessingStatus.NEEDS_OCR.value
                self.db.commit()
                return

            # Extract metadata
            logger.debug(f"Extracting metadata from document {document_id}")
            metadata = self.extractor.extract_metadata_from_text(text)
            
            # Update document with extracted metadata
            if metadata.get("title"):
                # Always update title with extracted one (better than filename)
                doc.title = metadata["title"]
            if metadata.get("authors"):
                doc.authors = metadata["authors"]
            if metadata.get("doi"):
                doc.doi = metadata["doi"]

            # Store extracted text in metadata
            import json
            doc.doc_metadata = json.dumps({
                "text_length": len(text),
                "word_count": len(text.split()),
                "extracted": True,
            })

            # Extract tables (PDF only)
            if doc.document_type == "pdf":
                logger.debug(f"Extracting tables from document {document_id}")
                tables = self.extractor.extract_tables_from_pdf(file_path)
                if tables:
                    logger.info(f"Extracted {len(tables)} tables from document {document_id}")
                    # Store table count in metadata
                    meta = json.loads(doc.doc_metadata)
                    meta["table_count"] = len(tables)
                    doc.doc_metadata = json.dumps(meta)

            # Phase 5: Chunking and Embedding
            logger.debug(f"Chunking document {document_id}")
            from app.document_processing.chunker import TextChunker
            from app.document_processing.embedder import DocumentEmbedder
            from app.models.document import DocumentChunk
            
            chunker = TextChunker(chunk_size=512, chunk_overlap=50)
            chunk_dicts = chunker.chunk_text(text, document_id)
            
            # Delete existing chunks
            self.db.query(DocumentChunk).filter(DocumentChunk.document_id == document_id).delete()
            
            # Create new chunks
            chunk_ids = []
            for chunk_dict in chunk_dicts:
                chunk = DocumentChunk(**chunk_dict)
                self.db.add(chunk)
                self.db.flush()  # Get the ID
                chunk_ids.append(chunk.id)
            
            self.db.commit()
            logger.info(f"Created {len(chunk_ids)} chunks for document {document_id}")
            
            # Generate embeddings
            try:
                logger.debug(f"Generating embeddings for document {document_id}")
                embedder = DocumentEmbedder(self.db)
                embedded_count = embedder.embed_chunks(chunk_ids)
                logger.info(f"Embedded {embedded_count} chunks for document {document_id}")
                
                # Update metadata with chunk count
                meta = json.loads(doc.doc_metadata)
                meta["chunk_count"] = len(chunk_ids)
                meta["embedded_count"] = embedded_count
                doc.doc_metadata = json.dumps(meta)
                self.db.commit()
            except Exception as e:
                logger.warning(f"Embedding failed for document {document_id}: {e}")
                # Continue even if embedding fails

            # Mark as completed
            doc.processing_status = ProcessingStatus.COMPLETED.value
            self.db.commit()
            
            logger.info(
                f"Document {document_id} processed successfully: "
                f"{len(text)} chars, {len(text.split())} words"
            )

        except Exception as e:
            logger.exception(f"Failed to process document {document_id}")
            doc.processing_status = ProcessingStatus.FAILED.value
            self.db.commit()
            raise

    def reprocess_document(self, document_id: int) -> None:
        """Reprocess a document (e.g., after failed processing).
        
        Args:
            document_id: Document ID
        """
        doc = self.db.query(Document).filter(Document.id == document_id).first()
        if not doc:
            raise ValueError(f"Document {document_id} not found")
        
        doc.processing_status = ProcessingStatus.PENDING.value
        self.db.commit()
        
        self.process_document(document_id)
