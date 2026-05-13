import jwt
import pytest

from app.domain.errors import InvalidCredentialsError, RefreshTokenInvalidError, UserAlreadyExistsError


@pytest.mark.asyncio
async def test_signup_returns_access_and_refresh_tokens(auth_services, key_set):
    tokens = await auth_services["signup"](
        key_set=key_set,
        username="Alice",
        password="correct horse battery staple",
    )

    claims = jwt.decode(
        tokens.access_token,
        key_set.active_key.public_key_pem,
        algorithms=["RS256"],
        audience="fapi-services",
        issuer="https://auth.example.com",
    )

    assert tokens.token_type == "Bearer"
    assert tokens.refresh_token
    assert claims["preferred_username"] == "Alice"


@pytest.mark.asyncio
async def test_duplicate_signup_is_rejected(auth_services, key_set):
    await auth_services["signup"](
        key_set=key_set,
        username="Alice",
        password="correct horse battery staple",
    )

    with pytest.raises(UserAlreadyExistsError):
        await auth_services["signup"](
            key_set=key_set,
            username="alice",
            password="correct horse battery staple",
        )


@pytest.mark.asyncio
async def test_signin_refresh_and_signout_flow(auth_services, key_set):
    await auth_services["signup"](
        key_set=key_set,
        username="Alice",
        password="correct horse battery staple",
    )

    signin_tokens = await auth_services["signin"](
        key_set=key_set,
        username="Alice",
        password="correct horse battery staple",
    )
    refreshed_tokens = await auth_services["refresh"](
        key_set=key_set,
        refresh_token=signin_tokens.refresh_token,
    )

    await auth_services["signout"](refresh_token=refreshed_tokens.refresh_token)

    with pytest.raises(RefreshTokenInvalidError):
        await auth_services["refresh"](
            key_set=key_set,
            refresh_token=refreshed_tokens.refresh_token,
        )


@pytest.mark.asyncio
async def test_signin_rejects_invalid_password(auth_services, key_set):
    await auth_services["signup"](
        key_set=key_set,
        username="Alice",
        password="correct horse battery staple",
    )

    with pytest.raises(InvalidCredentialsError):
        await auth_services["signin"](
            key_set=key_set,
            username="Alice",
            password="wrong password",
        )
