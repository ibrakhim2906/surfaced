from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from surfaced.auth.exceptions import (
    EmailExistsException,
    InactiveUserException,
    InvalidCredentialsException,
)
from surfaced.auth.models import User
from surfaced.auth.schemas import TokenResponse, UserLogin, UserRegister
from surfaced.auth.utilities import (
    DUMMY_HASH,
    create_access_token,
    create_refresh_token,
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

    if not existing or not check_password:
        raise InvalidCredentialsException

    if not existing.is_active:
        raise InactiveUserException

    access_token = create_access_token(existing.email)
    refresh_token = create_refresh_token(existing.email)

    return TokenResponse(access_token=access_token, refresh_token=refresh_token)
