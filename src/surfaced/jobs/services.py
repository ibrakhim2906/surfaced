import json
from collections.abc import Sequence
from typing import Any

from fastapi import HTTPException, status
from redis.asyncio import Redis
from sqlalchemy import delete, desc, func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from surfaced.auth.dependencies import CurrentUser
from surfaced.core.redis import get_cache, set_cache
from surfaced.jobs.constants import JOB_CACHE_TTL
from surfaced.jobs.exceptions import JobNotFoundException
from surfaced.jobs.models import Job, SavedJob
from surfaced.jobs.schemas import JobFilters, JobResponse, SavedJobRequest
from surfaced.jobs.utilities import (
    create_cache_key,
    create_cache_payload,
    next_cursor_b64_decode,
    next_cursor_b64_encode,
)


async def get_multi_jobs(
    db: AsyncSession, redis_client: Redis, filters: JobFilters
) -> tuple[Sequence[dict[str, Any]] | list[Any], str | None, bool]:

    cache_key = create_cache_key(filters)

    cached_data = await get_cache(redis_client, cache_key)

    if cached_data is not None:
        try:
            json_cached_data = json.loads(cached_data)

            return (
                json_cached_data["items"],
                json_cached_data["next_cursor"],
                json_cached_data["has_more"],
            )

        except (json.JSONDecodeError, KeyError, TypeError):
            pass

    query = select(Job).where(~Job.is_archived)

    if filters.q:
        tokens = func.plainto_tsquery("english", filters.q)
        query = query.where(Job.search_vector.op("@@")(tokens)).order_by(
            desc(func.ts_rank(Job.search_vector, tokens)),
            desc(Job.id),  # Tie-breaker
        )
    else:
        query = query.order_by(desc(Job.id))

    if filters.location:
        query = query.where(func.lower(Job.location) == (func.lower(filters.location)))

    if filters.cursor:
        try:
            cursor_bytes = filters.cursor.encode()
            last_seen_id = next_cursor_b64_decode(cursor_bytes)

            last_seen_id = int(last_seen_id)

            query = query.where(Job.id < last_seen_id)
        except (ValueError, TypeError, Exception):
            pass

    if filters.limit:
        query = query.limit(filters.limit + 1)

    result = await db.execute(query)

    result = result.scalars().all()

    has_more = False
    next_cursor = None
    items = result

    if len(result) > filters.limit:
        has_more = True

        items = result[: filters.limit]

        last_seen_id = items[-1].id
        last_seen_id = str(last_seen_id)

        next_cursor = next_cursor_b64_encode(last_seen_id)

    serialized_items = [
        JobResponse.model_validate(item).model_dump(mode="json") for item in items
    ]

    payload = create_cache_payload(
        serialized_items=serialized_items, next_cursor=next_cursor, has_more=has_more
    )

    await set_cache(redis_client, cache_key, json.dumps(payload), ttl=JOB_CACHE_TTL)

    return (serialized_items, next_cursor, has_more)


async def get_job_by_id(db: AsyncSession, job_id: int) -> Job:

    result = await db.execute(select(Job).where(Job.id == job_id))
    job = result.scalar_one_or_none()

    if not job:
        raise JobNotFoundException(None)

    if job.is_archived:
        raise JobNotFoundException(None)

    return job


async def me_save_job(
    db: AsyncSession, current_user: CurrentUser, saved_job: SavedJobRequest
):

    new_save = SavedJob(user_id=current_user.id, job_id=saved_job.job_id)
    db.add(new_save)

    try:
        await db.commit()
        await db.refresh(new_save)
        return new_save
    except IntegrityError:
        await db.rollback()

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="you have already saved this job",
        )


async def me_unsave_job(
    db: AsyncSession, current_user: CurrentUser, saved_job: SavedJobRequest
):

    query = (
        delete(SavedJob)
        .where(SavedJob.user_id == current_user.id, SavedJob.job_id == saved_job.job_id)
        .returning(SavedJob.id)
    )

    result = await db.execute(query)
    await db.commit()

    result = result.scalar_one_or_none()
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="saved job record not found"
        )


async def list_saved_jobs(db: AsyncSession, current_user: CurrentUser):
    query = (
        select(SavedJob)
        .where(SavedJob.user_id == current_user.id, ~Job.is_archived)
        .order_by(SavedJob.saved_at)
    )

    result = await db.execute(query)

    return result.scalars().all()
