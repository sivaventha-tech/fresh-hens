import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Boolean, Integer, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=True)
    role: Mapped[str] = mapped_column(String(20), default="user")        # user | admin
    tier: Mapped[str] = mapped_column(String(20), default="free")        # free | student | pro | enterprise
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    api_calls_used: Mapped[int] = mapped_column(Integer, default=0)
    generations_used: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Tier limits
    TIER_LIMITS = {
        "free": 3,
        "student": 20,
        "pro": 100,
        "enterprise": 99999,
    }

    @property
    def generation_limit(self) -> int:
        return self.TIER_LIMITS.get(self.tier, 3)

    @property
    def can_generate(self) -> bool:
        return self.generations_used < self.generation_limit

    def __repr__(self) -> str:
        return f"<User {self.email} [{self.tier}]>"
