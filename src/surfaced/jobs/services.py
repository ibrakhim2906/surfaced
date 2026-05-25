import base64
from collections.abc import Sequence

from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from surfaced.jobs.exceptions import JobNotFoundException
from surfaced.jobs.models import Job
from surfaced.jobs.schemas import JobFilters


async def get_multi_jobs(
    db: AsyncSession, filters: JobFilters
) -> tuple[Sequence[Job], str | None, bool]:

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
            last_seen_id = base64.b64decode(cursor_bytes).decode()

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

        next_cursor = base64.b64encode(last_seen_id.encode()).decode()

    return (items, next_cursor, has_more)


async def get_job_by_id(db: AsyncSession, job_id: int) -> Job:

    result = await db.execute(select(Job).where(Job.id == job_id))
    job = result.scalar_one_or_none()

    if not job:
        raise JobNotFoundException(None)

    if job.is_archived:
        raise JobNotFoundException(None)

    return job
