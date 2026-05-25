from fastapi import APIRouter, Depends, status

import surfaced.jobs.services as service
from surfaced.auth.dependencies import DbSession
from surfaced.jobs.schemas import JobFilters, JobResponse, PaginatedJobResponse

router = APIRouter(prefix="/jobs")


@router.get("", status_code=status.HTTP_200_OK)
async def get_jobs(
    db: DbSession, filters: JobFilters = Depends()
) -> PaginatedJobResponse:
    items, next_cursor, has_more = await service.get_multi_jobs(db, filters)

    return PaginatedJobResponse.model_validate(
        {"items": items, "next_cursor": next_cursor, "has_more": has_more}
    )


@router.get("/{job_id}")
async def get_job(db: DbSession, job_id: int) -> JobResponse:
    response = await service.get_job_by_id(db, job_id)

    return JobResponse.model_validate(response)
