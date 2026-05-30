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
    TokenExpiredException,
    TokenInvalidException,
    UserNotFoundException,
)
from surfaced.auth.models import User
from surfaced.auth.utilities import decode_token
from surfaced.core.database import get_db

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
