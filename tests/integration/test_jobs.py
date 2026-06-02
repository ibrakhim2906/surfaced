import asyncio

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from surfaced.jobs.models import Job


async def test_job_search(client: AsyncClient, db_session: AsyncSession):

    test_job = Job(
        title="Senior Python Developer",
        company="Test Company",
        description="FastAPI role in almaty",
        location="Almaty",
        stack=["Python", "Postgres", "FastAPI"],
        source="random jobs",
        source_url="random.jobs.org",
        is_archived=False,
    )

    db_session.add(test_job)

    await db_session.commit()

    response = await client.get("/api/v1/jobs", params={"q": "python fastapi"})

    assert response.status_code == 200
    found_items = response.json()["items"]

    assert len(found_items) == 1
    assert found_items[0]["title"] == "Senior Python Developer"


async def test_job_access_control(client: AsyncClient, db_session: AsyncSession):

    test_job_a = Job(
        title="Senior Python Developer",
        company="Test Company",
        description="FastAPI role in almaty",
        location="Almaty",
        stack=["Python", "Postgres", "FastAPI"],
        source="random jobs",
        source_url="random.jobs.org",
        is_archived=False,
    )

    test_job_b = Job(
        title="Middle Go Developer",
        company="Test Company",
        description="Go Backend role in almaty",
        location="Almaty",
        stack=["Go", "Postgres"],
        source="random jobs",
        source_url="random.go.jobs.org",
        is_archived=True,
    )

    db_session.add_all([test_job_a, test_job_b])

    await db_session.commit()

    response = await client.get("/api/v1/jobs", params={"q": "GO"})  # case-insensetive

    assert response.status_code == 200
    found_items = response.json()["items"]

    assert len(found_items) == 0


async def test_cursor_pagination(client: AsyncClient, db_session: AsyncSession):

    test_job_a = Job(
        title="Senior Python Developer",
        company="Test Company",
        description="FastAPI role in almaty",
        location="Almaty",
        stack=["Python", "Postgres", "FastAPI"],
        source="random jobs",
        source_url="random.jobs.org",
        is_archived=False,
    )

    test_job_b = Job(
        title="Middle Go Developer",
        company="Test Company",
        description="Go Backend role in almaty",
        location="Almaty",
        stack=["Go", "Postgres"],
        source="random jobs",
        source_url="random.go.jobs.org",
        is_archived=False,
    )

    test_job_c = Job(
        title="Middle Ruby Developer",
        company="Test Company",
        description="Ruby Backend role in almaty",
        location="Almaty",
        stack=["Ruby", "Ruby on Rails"],
        source="random jobs",
        source_url="random.ruby.jobs.org",
        is_archived=False,
    )

    db_session.add_all((test_job_a, test_job_b, test_job_c))

    await db_session.commit()

    response = await client.get("api/v1/jobs", params={"limit": 2})
    assert response.status_code == 200

    found_items = response.json()["items"]

    assert len(found_items) == 2
    assert response.json()["next_cursor"] is not None
    assert response.json()["has_more"] is True

    await asyncio.sleep(1)

    response_2 = await client.get(
        "api/v1/jobs",
        params={"limit": 1, "cursor": response.json()["next_cursor"]},
    )
    assert response_2.status_code == 200

    found_items_2 = response_2.json()["items"]

    assert len(found_items_2) == 1
    assert response_2.json()["has_more"] is False
    assert response_2.json()["next_cursor"] is None
