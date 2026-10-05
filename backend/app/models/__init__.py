"""SQLAlchemy ORM models.

Importing this package registers every table on ``Base.metadata``.
"""
from app.models.document import Collection, Document, DocumentChunk, ProcessingStatus
from app.models.job import Job, JobStatus
from app.models.journal import Journal, JournalRequirement, JournalSource, JournalStyleProfile
from app.models.manuscript import (
    AnalysisStatus,
    Evaluation,
    EvaluationIssue,
    ExportJob,
    ImprovementSuggestion,
    ImprovementTrack,
    Manuscript,
    ManuscriptComment,
    ManuscriptVersion,
    PeerReviewResponseLetter,
    RequirementCheck,
    RequirementStatus,
    VersionTag,
)
from app.models.model_registry import ModelRecord
from app.models.project import Project

__all__ = [
    "Collection", "Document", "DocumentChunk", "ProcessingStatus",
    "Job", "JobStatus",
    "Journal", "JournalRequirement", "JournalSource", "JournalStyleProfile",
    "AnalysisStatus", "Evaluation", "EvaluationIssue", "ExportJob",
    "ImprovementSuggestion", "ImprovementTrack", "Manuscript", "ManuscriptComment",
    "ManuscriptVersion", "PeerReviewResponseLetter", "RequirementCheck",
    "RequirementStatus", "VersionTag",
    "ModelRecord", "Project",
]