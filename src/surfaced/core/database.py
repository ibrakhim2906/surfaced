from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from surfaced.core.config import settings

engine = create_async_engine(
    str(settings.SQLALCHEMY_DATABASE_URI),
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    pool_recycle=3600,
)

async_session_factory = async_sessionmaker(
    engine, expire_on_commit=False, class_=AsyncSession
)


class Base(DeclarativeBase):
    pass


async def get_db() -> AsyncIterator[AsyncSession]:
    async with async_session_factory() as session:
        yield session
