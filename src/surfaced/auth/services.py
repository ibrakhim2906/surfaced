from jwt import ExpiredSignatureError, InvalidTokenError
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

    if not existing:
        raise UserNotFoundException

    if not check_password:
        raise InvalidCredentialsException

    if not existing.is_active:
        raise InactiveUserException

    access_token = create_access_token(existing.email)
    refresh_token = create_refresh_token(existing.email)

    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


async def refresh_token(refresh_token: str) -> TokenResponse:
    try:
        payload = decode_token(refresh_token)
    except ExpiredSignatureError:
        raise TokenExpiredException
    except InvalidTokenError:
        raise TokenInvalidException

    if payload.type != "refresh":
        raise TokenInvalidException

    return TokenResponse(
        access_token=create_access_token(subject=payload.sub),
        refresh_token=refresh_token,
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


async def logout_user() -> None:
    return None  # TODO implement refresh token invalidation
