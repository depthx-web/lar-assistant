"""Initialize database tables."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.db.base import Base
from app.db.session import engine
from app.models.manuscript import Manuscript, ManuscriptVersion, Evaluation, EvaluationIssue, RequirementCheck
from app.models.journal import Journal, JournalRequirement
from app.models.document import Document, DocumentChunk

def init_db():
    """Create all tables."""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully!")

if __name__ == "__main__":
    init_db()