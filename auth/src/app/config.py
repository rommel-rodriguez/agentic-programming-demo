from functools import lru_cache
from pathlib import Path

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="AUTH_", extra="ignore")

    env: str = "prod"
    issuer: str
    default_audience: str = "fapi-services"
    active_kid: str = "main"
    keys_dir: Path = Path("./.data/keys")
    auto_generate_active_key: bool = False
    db_url_sqlalchemy: str
    access_token_ttl_seconds: int = Field(default=900, ge=60)
    max_access_token_ttl_seconds: int = Field(default=3600, ge=60)
    refresh_token_ttl_seconds: int = Field(default=2592000, ge=300)

    @model_validator(mode="after")
    def validate_ttls(self) -> "Settings":
        if self.max_access_token_ttl_seconds < self.access_token_ttl_seconds:
            raise ValueError(
                "AUTH_MAX_ACCESS_TOKEN_TTL_SECONDS must be >= AUTH_ACCESS_TOKEN_TTL_SECONDS"
            )
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()
