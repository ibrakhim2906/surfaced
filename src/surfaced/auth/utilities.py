import uuid
from datetime import UTC, datetime, timedelta
from typing import Any

import jwt
from passlib.context import CryptContext

from surfaced.auth.schemas import TokenPayload
from surfaced.core.config import settings

crypt_context = CryptContext(schemes=["argon2"], deprecated="auto")

DUMMY_HASH: str = crypt_context.hash("dummy")


def hash_password(password: str) -> str:
    password_hash: str = crypt_context.hash(password)
    return password_hash


def verify_password(password: str, password_hash: str) -> bool:
    return bool(crypt_context.verify(password, password_hash))


def create_access_token(subject: str) -> str:
    payload = TokenPayload(
        sub=subject,
        exp=datetime.now(UTC) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        type="access",
        jti=str(uuid.uuid4()),
    )

    token = jwt.encode(
        payload=payload.model_dump(),
        key=settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )

    return token


def create_refresh_token(subject: str) -> str:
    payload = TokenPayload(
        sub=subject,
        exp=datetime.now(UTC) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
        type="refresh",
        jti=str(uuid.uuid4()),
    )

    token = jwt.encode(
        payload=payload.model_dump(),
        key=settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )

    return token


def decode_token(token: str) -> TokenPayload:
    payload: dict[str, Any] = jwt.decode(
        token, key=settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
    )

    return TokenPayload(**payload)
