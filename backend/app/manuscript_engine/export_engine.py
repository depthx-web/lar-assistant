"""Export engine for Phase 13."""
from __future__ import annotations

import json
import logging
import os
from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from app.models.manuscript import ExportJob, Manuscript, ManuscriptVersion

logger = logging.getLogger(__name__)


class ExportEngine:
    """Generate manuscript exports in various formats."""

    SUPPORTED_FORMATS = {"markdown", "latex", "text"}

    def __init__(self, db: Session):
        self.db = db

    def create_export_job(
        self,
        manuscript_id: int,
        fmt: str,
        version_id: Optional[int] = None,
    ) -> ExportJob:
        if fmt not in self.SUPPORTED_FORMATS:
            raise ValueError(f"Unsupported format: {fmt}. Supported: {self.SUPPORTED_FORMATS}")

        manuscript = self.db.query(Manuscript).filter(Manuscript.id == manuscript_id).first()
        if not manuscript:
            raise ValueError(f"Manuscript {manuscript_id} not found")

        job = ExportJob(
            manuscript_id=manuscript_id,
            version_id=version_id,
            format=fmt,
            status="PENDING",
        )
        self.db.add(job)
        self.db.commit()
        self.db.refresh(job)
        return job

    def _get_version(self, manuscript: Manuscript, version_id: Optional[int] = None) -> ManuscriptVersion:
        if version_id:
            v = self.db.query(ManuscriptVersion).filter(
                ManuscriptVersion.id == version_id,
                ManuscriptVersion.manuscript_id == manuscript.id,
            ).first()
        else:
            v = self.db.query(ManuscriptVersion).filter(
                ManuscriptVersion.manuscript_id == manuscript.id,
            ).order_by(ManuscriptVersion.version.desc()).first()
        if not v:
            raise ValueError("No manuscript version found")
        return v

    def _load_content(self, version: ManuscriptVersion) -> str:
        if version.content_path:
            import sys
            sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
            try:
                from app.core.config import settings
                full = os.path.join(settings.resolved_storage_root, version.content_path)
                if os.path.isfile(full):
                    with open(full, "r", encoding="utf-8") as f:
                        return f.read()
            except Exception:
                pass
        return ""

    def _extract_sections(self, content: str) -> Dict[str, str]:
        sections: Dict[str, str] = {}
        current_section = "main"
        current_lines: List[str] = []
        for line in content.splitlines():
            stripped = line.strip().lower()
            if stripped.startswith("abstract") or stripped == "abstract:":
                if current_lines:
                    sections[current_section] = "\n".join(current_lines)
                current_section = "abstract"
                current_lines = []
            elif stripped.startswith("introduction") or stripped == "introduction:":
                if current_lines:
                    sections[current_section] = "\n".join(current_lines)
                current_section = "introduction"
                current_lines = []
            elif stripped.startswith("methods") or stripped.startswith("methodology"):
                if current_lines:
                    sections[current_section] = "\n".join(current_lines)
                current_section = "methods"
                current_lines = []
            elif stripped.startswith("results"):
                if current_lines:
                    sections[current_section] = "\n".join(current_lines)
                current_section = "results"
                current_lines = []
            elif stripped.startswith("discussion") or stripped.startswith("conclusions"):
                if current_lines:
                    sections[current_section] = "\n".join(current_lines)
                current_section = "discussion"
                current_lines = []
            elif stripped.startswith("conclusion") and not stripped.startswith("conclusions"):
                if current_lines:
                    sections[current_section] = "\n".join(current_lines)
                current_section = "conclusion"
                current_lines = []
            elif stripped.startswith("references"):
                if current_lines:
                    sections[current_section] = "\n".join(current_lines)
                current_section = "references"
                current_lines = []
            else:
                current_lines.append(line)
        if current_lines:
            sections[current_section] = "\n".join(current_lines)
        return sections

    def export_markdown(self, manuscript: Manuscript, version: ManuscriptVersion) -> str:
        content = self._load_content(version)
        sections = self._extract_sections(content)
        lines = [f"# {manuscript.title}", ""]
        if manuscript.journal_id:
            lines.append(f"**Target Journal**: {manuscript.journal_id}")
            lines.append("")
        for section_name in ["abstract", "introduction", "methods", "results", "discussion", "conclusion", "references"]:
            if section_name in sections:
                lines.append(f"## {section_name.capitalize()}")
                lines.append("")
                lines.append(sections[section_name])
                lines.append("")
        if "main" in sections:
            lines.append("## Main Text")
            lines.append("")
            lines.append(sections["main"])
            lines.append("")
        return "\n".join(lines)

    def export_latex(self, manuscript: Manuscript, version: ManuscriptVersion) -> str:
        content = self._load_content(version)
        sections = self._extract_sections(content)
        lines = [
            r"\\documentclass[12pt]{article}",
            r"\\usepackage{amsmath}",
            r"\\usepackage{graphicx}",
            "",
            r"\\title{" + manuscript.title.replace("{", "\\{").replace("}", "\\}") + "}",
            "",
            r"\\begin{document}",
            "",
            r"\\maketitle",
            "",
        ]
        for section_name in ["abstract", "introduction", "methods", "results", "discussion", "conclusion"]:
            if section_name in sections:
                lines.append(r"\\section{" + section_name.capitalize() + "}")
                lines.append("")
                lines.append(sections[section_name])
                lines.append("")
        if "references" in sections:
            lines.append(r"\\bibliography{references}")
            lines.append(r"\\bibliographystyle{plain}")
        lines.append("")
        lines.append(r"\\end{document}")
        return "\n".join(lines)

    def export_text(self, manuscript: Manuscript, version: ManuscriptVersion) -> str:
        return self._load_content(version) or manuscript.title

    def run_export(self, job: ExportJob) -> Dict[str, Any]:
        job.status = "PROCESSING"
        self.db.commit()

        manuscript = self.db.query(Manuscript).filter(Manuscript.id == job.manuscript_id).first()
        if not manuscript:
            raise ValueError(f"Manuscript {job.manuscript_id} not found")

        version = self._get_version(manuscript, job.version_id)
        try:
            if job.format == "markdown":
                output = self.export_markdown(manuscript, version)
            elif job.format == "latex":
                output = self.export_latex(manuscript, version)
            else:
                output = self.export_text(manuscript, version)

            output_filename = f"export_{job.manuscript_id}_{job.format}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.{job.format}"
            storage_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), "exports")
            os.makedirs(storage_dir, exist_ok=True)
            output_path = os.path.join(storage_dir, output_filename)
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(output)

            job.status = "COMPLETED"
            job.output_path = output_path
            job.completed_at = datetime.utcnow()
        except Exception as e:
            logger.exception("Export failed for job %d", job.id)
            job.status = "FAILED"
            job.error_message = str(e)

        self.db.commit()
        self.db.refresh(job)

        return {
            "job_id": job.id,
            "manuscript_id": job.manuscript_id,
            "format": job.format,
            "status": job.status,
            "output_path": job.output_path,
            "error_message": job.error_message,
        }
