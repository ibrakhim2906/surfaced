from fastapi import FastAPI

from surfaced.auth.routers import router as auth_router
from surfaced.core.config import settings


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        debug=settings.ENVIRONMENT == "local",
    )

    app.include_router(auth_router, prefix=settings.API_V1_STR)

    return app


app = create_app()
