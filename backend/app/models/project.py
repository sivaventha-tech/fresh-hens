import uuid
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    # User inputs
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    category: Mapped[str] = mapped_column(String(100), nullable=True)     # ML | FastAPI | React | etc.
    technologies: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)  # list of strings
    features: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)      # list of strings
    complexity: Mapped[str] = mapped_column(String(20), default="intermediate") # basic | intermediate | advanced

    # Generation state
    status: Mapped[str] = mapped_column(String(20), default="pending")
    # pending | generating | done | failed

    # AI output
    architecture: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    folder_structure: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    files: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)         # {path: content}
    readme: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    env_example: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Storage
    zip_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # Metadata
    llm_provider: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    tokens_used: Mapped[Optional[int]] = mapped_column(nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    def __repr__(self) -> str:
        return f"<Project {self.title!r} [{self.status}]>"
