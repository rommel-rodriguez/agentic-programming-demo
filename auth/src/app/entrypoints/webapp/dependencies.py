from fastapi import Request

from app.services.authentication import (
    RefreshUserSession,
    SignInUser,
    SignOutUser,
    SignUpUser,
)


def get_key_set(request: Request):
    return request.app.state.key_set


def get_jwks_document(request: Request):
    return request.app.state.jwks_document


def get_signup_user(request: Request) -> SignUpUser:
    return request.app.state.signup_user


def get_signin_user(request: Request) -> SignInUser:
    return request.app.state.signin_user


def get_refresh_user_session(request: Request) -> RefreshUserSession:
    return request.app.state.refresh_user_session


def get_signout_user(request: Request) -> SignOutUser:
    return request.app.state.signout_user
