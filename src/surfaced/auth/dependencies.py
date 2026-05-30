from collections.abc import Callable
from typing import Annotated, Any

from fastapi import Depends, Request
from fastapi.security import OAuth2PasswordBearer
from jwt import ExpiredSignatureError, InvalidTokenError
from redis.asyncio import Redis
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from surfaced.auth.constants import TOKEN_TYPE_ACCESS
from surfaced.auth.exceptions import (
    InactiveUserException,
    RateLimitExceededException,
    TokenExpiredException,
    TokenInvalidException,
    UserNotFoundException,
)
from surfaced.auth.models import User
from surfaced.auth.utilities import decode_token
from surfaced.core.database import get_db
from surfaced.core.redis import rate_limit_exceeded

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> User:
    try:
        payload = decode_token(token)
    except ExpiredSignatureError:
        raise TokenExpiredException
    except InvalidTokenError:
        raise TokenInvalidException

    if payload.type != TOKEN_TYPE_ACCESS:
        raise TokenInvalidException

    result = await db.execute(select(User).where(User.email == payload.sub))
    existing = result.scalar_one_or_none()

    if not existing:
        raise UserNotFoundException

    if not existing.is_active:
        raise InactiveUserException

    return existing


def get_redis(request: Request) -> Redis:

    state: Any = request.app.state
    return state.redis


DbSession = Annotated[AsyncSession, Depends(get_db)]
CurrentUser = Annotated[User, Depends(get_current_user)]
RedisClient = Annotated[Redis, Depends(get_redis)]


def get_auth_rate_limiter(
    max_requests: int,
    window_seconds,
    action_name: str,
) -> Callable[[Request, RedisClient], Any]:
    async def create_dependency(request: Request, redis_client: RedisClient):
        ip = request.client.host if request.client else "unknown"

        redis_key = f"ratelimit:{action_name}:{ip}"

        limited = await rate_limit_exceeded(
            redis_client=redis_client,
            key=redis_key,
            max_requests=max_requests,
            window_seconds=window_seconds,
        )

        if limited:
            raise RateLimitExceededException

    return create_dependency


LoginLimiter = Annotated[
    None,
    Depends(
        get_auth_rate_limiter(max_requests=5, window_seconds=60, action_name="login")
    ),
]

RegisterLimiter = Annotated[
    None,
    Depends(
        get_auth_rate_limiter(
            max_requests=3, window_seconds=3600, action_name="register"
        )
    ),
]
