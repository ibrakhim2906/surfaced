from contextlib import asynccontextmanager

import redis.asyncio as redis
from fastapi import FastAPI
from fastapi.responses import JSONResponse

from surfaced.auth.routers import router as auth_router
from surfaced.core.config import settings
from surfaced.jobs.routers import router as jobs_router


@asynccontextmanager
async def lifespan(app: FastAPI):

    app.state.redis = redis.from_url(settings.REDIS_URL, decode_responses=True)

    yield

    await app.state.redis.aclose()


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        debug=settings.ENVIRONMENT == "local",
        lifespan=lifespan,
    )

    @app.get("/health", include_in_schema=False)
    async def health() -> JSONResponse:
        return JSONResponse({"status": "ok"})

    app.include_router(auth_router, prefix=settings.API_V1_STR)
    app.include_router(jobs_router, prefix=settings.API_V1_STR)

    return app


app = create_app()
