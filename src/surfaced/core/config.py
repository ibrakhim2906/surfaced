import json
from pathlib import Path
from typing import Literal

from pydantic import Field, PostgresDsn, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT_DIR = Path(__file__).parent.parent.parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(ROOT_DIR / ".env"), env_ignore_empty=True, extra="ignore"
    )

    APP_NAME: str = "Surfaced"

    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str
    ALGORITHM: str = "HS256"

    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    ENVIRONMENT: Literal["local", "production"] = "local"

    POSTGRES_SERVER: str
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str = ""
    POSTGRES_DB: str = ""

    REDIS_URL: str

    @computed_field
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> PostgresDsn:  # noqa: N802
        return PostgresDsn.build(
            scheme="postgresql+asyncpg",
            username=self.POSTGRES_USER,
            password=self.POSTGRES_PASSWORD,
            host=self.POSTGRES_SERVER,
            port=self.POSTGRES_PORT,
            path=self.POSTGRES_DB,
        )

    HH_CLIENT_SECRET: str = ""
    HH_CLIENT_ID: str = ""
    HH_APPLICATION_TOKEN: str = ""
    YOUR_EMAIL: str = ""

    SENTRY_DSN: str = ""

    TELEGRAM_API_ID: int = 0
    TELEGRAM_API_HASH: str = ""
    TELEGRAM_SESSION_STRING: str = ""
    TELEGRAM_CHANNELS: list[str] = ["devkz_jobs", "workitkz"]

    CORS_ORIGINS_RAW: str = Field("http://localhost:3000", alias="CORS_ORIGINS")

    @computed_field
    @property
    def CORS_ORIGINS(self) -> list[str]:  # noqa: N802
        raw = self.CORS_ORIGINS_RAW
        try:
            parsed = json.loads(raw)
            if isinstance(parsed, list):
                return parsed
        except (json.JSONDecodeError, ValueError):
            pass
        return [o.strip() for o in raw.split(",") if o.strip()]


settings = Settings()
