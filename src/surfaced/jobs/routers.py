from fastapi import APIRouter, Depends, status
from starlette.status import HTTP_200_OK

import surfaced.jobs.services as service
from surfaced.auth.dependencies import CurrentUser, DbSession, RedisClient
from surfaced.jobs.schemas import (
    JobFilters,
    JobResponse,
    ListSavedJobResponse,
    PaginatedJobResponse,
    SavedJobRequest,
    SavedJobResponse,
)

router = APIRouter(prefix="/jobs")


@router.get("", status_code=status.HTTP_200_OK)
async def get_jobs(
    db: DbSession, redis_client: RedisClient, filters: JobFilters = Depends()
) -> PaginatedJobResponse:
    items, next_cursor, has_more = await service.get_multi_jobs(db, redis_client, filters)

    return PaginatedJobResponse.model_validate(
        {"items": items, "next_cursor": next_cursor, "has_more": has_more}
    )


@router.get("/{job_id}", status_code=status.HTTP_200_OK)
async def get_job(db: DbSession, job_id: int) -> JobResponse:
    response = await service.get_job_by_id(db, job_id)
    return JobResponse.model_validate(response)


@router.post("/me/saved", status_code=HTTP_200_OK)
async def me_save_job(
    request: SavedJobRequest, db: DbSession, current_user: CurrentUser
) -> SavedJobResponse:
    response = await service.me_save_job(db, current_user, request)
    return SavedJobResponse.model_validate(response)


@router.delete("/me/saved", status_code=status.HTTP_204_NO_CONTENT)
async def me_unsave_job(
    request: SavedJobRequest, db: DbSession, current_user: CurrentUser
) -> None:
    _ = await service.me_unsave_job(db, current_user, request)


@router.get("/me/saved", status_code=status.HTTP_200_OK)
async def me_show_saved_jobs(
    db: DbSession, current_user: CurrentUser
) -> ListSavedJobResponse:
    response = await service.list_saved_jobs(db, current_user)

    return ListSavedJobResponse.model_validate(response)
