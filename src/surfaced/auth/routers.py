from fastapi import APIRouter, status

import surfaced.auth.services as service
from surfaced.auth.dependencies import CurrentUser, DbSession
from surfaced.auth.schemas import (
    PasswordChange,
    TokenRefresh,
    TokenResponse,
    UserLogin,
    UserRegister,
    UserResponse,
    UserUpdate,
)

router = APIRouter(prefix="/auth")


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(db: DbSession, user_in: UserRegister) -> UserResponse:
    user = await service.register_user(db, user_in)
    return UserResponse.model_validate(user)


@router.post("/login")
async def login(db: DbSession, user_in: UserLogin) -> TokenResponse:
    return await service.login_user(db, user_in)


@router.post("/token/refresh")
async def refresh_token(token_in: TokenRefresh) -> TokenResponse:
    return await service.refresh_token(token_in.refresh_token)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout() -> None:
    await service.logout_user()


@router.patch("/password", status_code=status.HTTP_204_NO_CONTENT)
async def change_password(
    db: DbSession, current_user: CurrentUser, data: PasswordChange
) -> None:
    await service.change_password(db, current_user, data)


@router.get("/me")
async def get_me(current_user: CurrentUser) -> UserResponse:
    return UserResponse.model_validate(current_user)


@router.patch("/me", status_code=status.HTTP_200_OK)
async def change_me(
    db: DbSession, current_user: CurrentUser, data: UserUpdate
) -> UserResponse:
    updated_user = await service.update_user(db, current_user, data)
    return UserResponse.model_validate(updated_user)
