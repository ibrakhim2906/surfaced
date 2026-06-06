from collections.abc import AsyncGenerator

import pytest
from httpx import ASGITransport, AsyncClient
from redis.asyncio import Redis
from sqlalchemy import insert, text
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from surfaced.auth.dependencies import get_redis
from surfaced.core.config import settings
from surfaced.core.database import Base, get_db
from surfaced.jobs.models import Job
from surfaced.main import app

TEST_DATABASE_URL = (
    f"postgresql+asyncpg://{settings.POSTGRES_USER}:"
    f"{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_SERVER}:"
    f"{settings.POSTGRES_PORT}/surfaced_test"
)


@pytest.fixture(scope="function")
async def test_engine():
    engine = create_async_engine(TEST_DATABASE_URL)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

        await conn.execute(
            text("""
                CREATE OR REPLACE FUNCTION jobs_search_vector_trigger()
                RETURNS TRIGGER AS $$
                BEGIN
                    NEW.search_vector :=
                        setweight(to_tsvector('english',
                        coalesce(NEW.title, '')), 'A') ||
                        setweight(to_tsvector('english',
                        coalesce(NEW.company, '')), 'B') ||
                        setweight(to_tsvector('english',
                        coalesce(array_to_string(NEW.stack, ' '), '')), 'B');
                    RETURN NEW;
                END;
                $$ LANGUAGE plpgsql;
            """)
        )

        await conn.execute(text("DROP TRIGGER IF EXISTS tsvectorupdate ON jobs;"))

        await conn.execute(
            text("""
                CREATE TRIGGER tsvectorupdate BEFORE INSERT OR UPDATE
                ON jobs FOR EACH ROW
                EXECUTE FUNCTION jobs_search_vector_trigger();
            """)
        )
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

        await conn.execute(text("DROP TRIGGER IF EXISTS vsvectorupdate ON jobs;"))

        await conn.execute(text("DROP FUNCTION IF EXISTS jobs_search_vector_trigger();"))
    await engine.dispose()


@pytest.fixture(scope="function")
async def db_session(test_engine):
    async_session_factory = async_sessionmaker(
        test_engine, expire_on_commit=False, class_=AsyncSession
    )

    async with async_session_factory() as session:
        yield session
        await session.rollback()


@pytest.fixture(scope="function")
async def redis_client() -> AsyncGenerator[Redis, None]:

    client = Redis(host="localhost", port=6379, db=1, decode_responses=True)

    await client.flushdb()

    yield client

    await client.close()


@pytest.fixture(scope="function")
async def client(
    db_session: AsyncSession, redis_client: Redis
) -> AsyncGenerator[AsyncClient, None]:

    async def override_get_db():
        yield db_session

    async def override_get_redis():
        return redis_client

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_redis] = override_get_redis
    async with AsyncClient(
        base_url="http://test", transport=ASGITransport(app=app)
    ) as async_client:
        yield async_client

    app.dependency_overrides.clear()


TEST_USER = {
    "email": "test@example.com",
    "password": "testpassword123",
    "full_name": "Test User",
}


@pytest.fixture(scope="function")
async def authenticated_client(
    client: AsyncClient,
):

    _ = await client.post("/api/v1/auth/register", json=TEST_USER)

    response = await client.post(
        "/api/v1/auth/login",
        json={"email": TEST_USER["email"], "password": TEST_USER["password"]},
    )

    token = response.json()["access_token"]

    client.headers["Authorization"] = f"Bearer {token}"

    yield client


TEST_JOBS_DATA = [
    {
        "title": "Junior Python Developer",
        "company": "PythonDevs",
        "location": "Remote",
        "description": "Know separate library for every case",
        "stack": ["Python", "FastAPI"],
        "source": "linkedin",
        "source_url": "https://linkedin.com/jobs/fake-python-123",
        "is_archived": False,
    },
    {
        "title": "Senior Go Developer",
        "company": "GoDevs",
        "location": "San Francisco",
        "description": "Go all the way",
        "stack": ["Go", "Postgres"],
        "source": "ycombinator",
        "source_url": "https://www.ycombinator.com/jobs/fake-go-id-456",
        "is_archived": False,
    },
]


@pytest.fixture(scope="function")
async def seed_jobs(db_session: AsyncSession) -> list[Job]:

    result = await db_session.execute(insert(Job).values(TEST_JOBS_DATA).returning(Job))

    await db_session.flush()

    return list(result.scalars().all())
