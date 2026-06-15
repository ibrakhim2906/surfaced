from contextlib import asynccontextmanager

import redis.asyncio as redis
import sentry_sdk
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from surfaced.auth.routers import router as auth_router
from surfaced.core.config import settings
from surfaced.core.logging import setup_logging
from surfaced.jobs.routers import router as jobs_router

setup_logging()

if settings.SENTRY_DSN:
    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        environment=settings.ENVIRONMENT,
        traces_sample_rate=0.1,
    )


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

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/health", include_in_schema=False)
    async def health() -> JSONResponse:
        return JSONResponse({"status": "ok"})

    app.include_router(auth_router, prefix=settings.API_V1_STR)
    app.include_router(jobs_router, prefix=settings.API_V1_STR)

    return app


app = create_app()
