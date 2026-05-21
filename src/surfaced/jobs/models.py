from datetime import datetime
from typing import Any

from sqlalchemy import Index, String, func
from sqlalchemy.dialects.postgresql import ARRAY, TSVECTOR
from sqlalchemy.orm import Mapped, mapped_column

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
    posted_at: Mapped[datetime | None] = mapped_column()
    is_archived: Mapped[bool] = mapped_column(default=False)
    search_vector: Mapped[Any | None] = mapped_column(TSVECTOR, nullable=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    __table_args__ = (
        Index("idx_jobs_search_vector", "search_vector", postgresql_using="gin"),
    )
