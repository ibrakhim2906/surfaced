from datetime import datetime
from typing import Any

from sqlalchemy import ForeignKey, Index, String, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import ARRAY, TSVECTOR
from sqlalchemy.orm import Mapped, mapped_column, relationship

from surfaced.core.database import Base


class Job(Base):
    __tablename__ = "jobs"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column()
    company: Mapped[str] = mapped_column()
    location: Mapped[str | None] = mapped_column()
    salary_min: Mapped[int | None] = mapped_column()
    salary_max: Mapped[int | None] = mapped_column()
    description: Mapped[str] = mapped_column()
    stack: Mapped[list[str]] = mapped_column(ARRAY(String), default=[])
    source: Mapped[str] = mapped_column()
    source_url: Mapped[str] = mapped_column(unique=True)
    source_id: Mapped[str | None] = mapped_column(nullable=True)
    posted_at: Mapped[datetime | None] = mapped_column()
    is_archived: Mapped[bool] = mapped_column(default=False)
    search_vector: Mapped[Any | None] = mapped_column(TSVECTOR, nullable=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    __table_args__ = (
        Index("idx_jobs_search_vector", "search_vector", postgresql_using="gin"),
    )


class SavedJob(Base):
    __tablename__ = "saved_jobs"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    job_id: Mapped[int] = mapped_column(ForeignKey("jobs.id", ondelete="CASCADE"))
    saved_at: Mapped[datetime] = mapped_column(server_default=func.now())

    job: Mapped["Job"] = relationship("Job", lazy="joined")

    __table_args__ = (UniqueConstraint("user_id", "job_id", name="uq_user_saved_jobs"),)
