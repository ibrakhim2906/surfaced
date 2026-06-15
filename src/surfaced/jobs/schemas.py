from collections.abc import Sequence
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class JobResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    company: str
    location: str | None
    salary_min: int | None
    salary_max: int | None
    salary_currency: str
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

    source: str | None = Field(
        None, description="Filter by source: headhunter or telegram"
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


class SavedJobRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    job_id: int


class SavedJobResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    job_id: int
    saved_at: datetime

    job: JobResponse


class ListSavedJobResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    items: Sequence[SavedJobResponse]


class HHScrapeVacancySchema(BaseModel):
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    source_id: str = Field(alias="id")
    title: str = Field(alias="name")
    source_url: str = Field(alias="alternate_url")

    employer: dict[str, Any] = {}
    area: dict[str, Any] = {}
    salary: dict[str, Any] | None = None

    def to_db_dict(self) -> dict[str, Any]:

        initial_stack_check = [
            "Python",
            "JavaScript",
            "Java",
            "C++",
            "C#",
            "TypeScript",
            "Go",
            "Rust",
            "PHP",
            "Swift",
            "Kotlin",
            "Ruby",
        ]

        salary_min = None
        salary_max = None
        salary_currency = "KZT"

        if self.salary:
            salary_min = self.salary.get("from")
            salary_max = self.salary.get("to")
            salary_currency = self.salary.get("currency", "KZT")

        company_name = self.employer.get("name", "Unknown Company")
        location_name = self.area.get("name", "Unknown Location")

        fallback_description = (
            f"Вакансия {self.title} в компании {company_name} ({location_name}). "
            f"Полное описание будет загружено в ближайшее время."
        )

        detected_stack = []

        for skill in initial_stack_check:
            if skill.lower() in self.title.lower():
                detected_stack.append(skill)

        return {
            "source_id": self.source_id,
            "title": self.title,
            "company": company_name,
            "location": location_name,
            "salary_min": salary_min,
            "salary_max": salary_max,
            "salary_currency": salary_currency,
            "description": fallback_description,
            "stack": detected_stack,
            "source": "headhunter",
            "source_url": self.source_url,
            "is_archived": False,
        }
