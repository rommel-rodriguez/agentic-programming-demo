from typing import Literal

from pydantic import BaseModel, Field


class UserCredentialsIn(BaseModel):
    username: str = Field(min_length=3, max_length=255)
    password: str = Field(min_length=8, max_length=256)


class RefreshTokenIn(BaseModel):
    refresh_token: str = Field(min_length=32)


class SessionTokensOut(BaseModel):
    token_type: Literal["Bearer"]
    access_token: str
    refresh_token: str
    expires_in: int


class OpenIDConfigurationOut(BaseModel):
    issuer: str
    jwks_uri: str
    token_endpoint: str | None = None


class HealthOut(BaseModel):
    status: Literal["ok"]
