from typing import Annotated

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jwt import ExpiredSignatureError, InvalidTokenError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.surfaced.auth.utilities import decode_token
from src.surfaced.core.database import get_db
from surfaced.auth.constants import TOKEN_TYPE_ACCESS
from surfaced.auth.exceptions import (
    InactiveUserException,
    TokenExpiredException,
    TokenInvalidException,
    UserNotFoundException,
)
from surfaced.auth.models import User

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


DbSession = Annotated[AsyncSession, Depends(get_db)]
CurrentUser = Annotated[User, Depends(get_current_user)]
