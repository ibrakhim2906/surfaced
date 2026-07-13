from datetime import UTC, datetime

from jwt import ExpiredSignatureError, InvalidTokenError
from redis.asyncio import Redis
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from surfaced.auth.constants import TOKEN_TYPE_BEARER
from surfaced.auth.exceptions import (
    EmailExistsException,
    InactiveUserException,
    InvalidCredentialsException,
    TokenExpiredException,
    TokenInvalidException,
    UserNotFoundException,
)
from surfaced.auth.models import User
from surfaced.auth.schemas import (
    PasswordChange,
    TokenRefresh,
    TokenResponse,
    UserLogin,
    UserRegister,
    UserUpdate,
)
from surfaced.auth.utilities import (
    DUMMY_HASH,
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from surfaced.core.redis import get_cache, set_cache


async def register_user(db: AsyncSession, user_in: UserRegister) -> User:
    result = await db.execute(select(User).where(User.email == user_in.email))
    existing = result.scalar_one_or_none()

    if existing:
        raise EmailExistsException

    password_hash = hash_password(user_in.password)

    new_user = User(
        email=user_in.email, full_name=user_in.full_name, password_hash=password_hash
    )

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    return new_user


async def login_user(db: AsyncSession, user_in: UserLogin) -> TokenResponse:
    result = await db.execute(select(User).where(User.email == user_in.email))
    existing = result.scalar_one_or_none()

    check_password = verify_password(
        user_in.password, existing.password_hash if existing else DUMMY_HASH
    )

    if not existing or not check_password:
        raise InvalidCredentialsException

    if not existing.is_active:
        raise InactiveUserException

    access_token = create_access_token(existing.email)
    refresh_token = create_refresh_token(existing.email)

    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


async def refresh_token(
    db: AsyncSession, redis_client: Redis, token_in: TokenRefresh
) -> TokenResponse:
    try:
        payload = decode_token(token_in.refresh_token)
    except ExpiredSignatureError:
        raise TokenExpiredException
    except InvalidTokenError:
        raise TokenInvalidException

    if payload.type != "refresh":
        raise TokenInvalidException

    is_blocked = await get_cache(redis_client, f"blocklist:{payload.jti}")
    if is_blocked:
        raise TokenInvalidException

    result = await db.execute(select(User).where(User.email == payload.sub))
    user = result.scalar_one_or_none()
    if not user:
        raise UserNotFoundException
    if not user.is_active:
        raise InactiveUserException

    now = datetime.now(UTC)
    seconds_left = int((payload.exp - now).total_seconds())
    if seconds_left > 0:
        await set_cache(redis_client, f"blocklist:{payload.jti}", "revoked", seconds_left)

    return TokenResponse(
        access_token=create_access_token(subject=user.email),
        refresh_token=create_refresh_token(subject=user.email),
        token_type=TOKEN_TYPE_BEARER,
    )


async def change_password(
    db: AsyncSession, current_user: User, data: PasswordChange
) -> None:

    check_password = verify_password(data.old_password, current_user.password_hash)

    if not check_password:
        raise InvalidCredentialsException

    current_user.password_hash = hash_password(data.new_password)

    await db.commit()


async def update_user(db: AsyncSession, current_user: User, data: UserUpdate) -> User:
    if data.full_name is not None:
        current_user.full_name = data.full_name
    await db.commit()
    return current_user


async def logout_user(redis_client: Redis, token_in: TokenRefresh) -> None:
    try:
        payload = decode_token(token_in.refresh_token)
    except (ExpiredSignatureError, InvalidTokenError):
        return

    now = datetime.now(UTC)

    time_remaining = payload.exp - now

    seconds_left = int(time_remaining.total_seconds())

    if seconds_left > 0:
        await set_cache(redis_client, f"blocklist:{payload.jti}", "revoked", seconds_left)
