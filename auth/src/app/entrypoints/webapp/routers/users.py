from fastapi import APIRouter, Depends, Response, status

from app.entrypoints.webapp.dependencies import (
    get_key_set,
    get_refresh_user_session,
    get_signin_user,
    get_signout_user,
    get_signup_user,
)
from app.entrypoints.webapp.models import RefreshTokenIn, SessionTokensOut, UserCredentialsIn
from app.services.authentication import RefreshUserSession, SignInUser, SignOutUser, SignUpUser

router = APIRouter(tags=["users"])


@router.post(
    "/users/signup",
    response_model=SessionTokensOut,
    status_code=status.HTTP_201_CREATED,
)
async def signup(
    payload: UserCredentialsIn,
    key_set=Depends(get_key_set),
    use_case: SignUpUser = Depends(get_signup_user),
):
    tokens = await use_case(
        key_set=key_set,
        username=payload.username,
        password=payload.password,
    )
    return tokens


@router.post("/users/signin", response_model=SessionTokensOut)
async def signin(
    payload: UserCredentialsIn,
    key_set=Depends(get_key_set),
    use_case: SignInUser = Depends(get_signin_user),
):
    tokens = await use_case(
        key_set=key_set,
        username=payload.username,
        password=payload.password,
    )
    return tokens


@router.post("/users/refresh", response_model=SessionTokensOut)
async def refresh(
    payload: RefreshTokenIn,
    key_set=Depends(get_key_set),
    use_case: RefreshUserSession = Depends(get_refresh_user_session),
):
    tokens = await use_case(key_set=key_set, refresh_token=payload.refresh_token)
    return tokens


@router.post("/users/signout", status_code=status.HTTP_204_NO_CONTENT)
async def signout(
    payload: RefreshTokenIn,
    use_case: SignOutUser = Depends(get_signout_user),
):
    await use_case(refresh_token=payload.refresh_token)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
