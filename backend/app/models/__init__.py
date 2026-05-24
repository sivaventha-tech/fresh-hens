# Models package — import all so SQLAlchemy registers them with Base.metadata
from app.models.user import User
from app.models.project import Project
from app.models.generation import GenerationLog

__all__ = ["User", "Project", "GenerationLog"]
