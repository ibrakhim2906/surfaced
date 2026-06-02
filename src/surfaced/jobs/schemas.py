from collections.abc import Sequence
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class JobResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    title: str
    company: str
    location: str | None
    salary_min: int | None
    salary_max: int | None
    description: str
    stack: list[str]
    source: str
    source_url: str
    posted_at: datetime | None
    is_archived: bool


class JobFilters(BaseModel):
    q: str | None = Field(None, min_length=2, description="Full-text search string")

    location: str | None = Field(
        None, description="Filter jobs by specific location or remote status"
    )

    limit: int = Field(20, ge=1, le=100, description="Amount of jobs to be seen for user")

    cursor: str | None = Field(
        None,
        description="Base64 encoded bookmark ID pointer to the last seen job posting",
    )


class PaginatedJobResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    items: Sequence[JobResponse]
    next_cursor: str | None = None
    has_more: bool


class SavedJobResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    job_id: int
    saved_at: datetime

    job: JobResponse


class PaginatedSavedJobResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    items: Sequence[SavedJobResponse]
    next_cursor: str | None = None
    has_more: bool
