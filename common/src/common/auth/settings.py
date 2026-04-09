from pydantic import BaseModel, SecretStr, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class JWTVerificationConfig(BaseModel):
    issuer: str
    audience: str | None = None
    jwks_url: str | None = None
    public_key_pem: SecretStr | None = None
    algorithms: tuple[str, ...] = ("RS256",)
    leeway_seconds: int = 0
    jwks_cache_ttl_seconds: int = 300
    subject_claim: str = "sub"
    tenant_id_claim: str = "tenant_id"
    scope_claim: str = "scope"

    @model_validator(mode="after")
    def validate_key_source(self) -> "JWTVerificationConfig":
        has_jwks = self.jwks_url is not None
        has_public_key = self.public_key_pem is not None
        if has_jwks == has_public_key:
            raise ValueError(
                "Exactly one of jwks_url or public_key_pem must be configured"
            )
        return self


class JWTVerificationSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="AUTH_",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    issuer: str
    audience: str | None = None
    jwks_url: str | None = None
    public_key_pem: SecretStr | None = None
    algorithms: tuple[str, ...] = ("RS256",)
    leeway_seconds: int = 0
    jwks_cache_ttl_seconds: int = 300
    subject_claim: str = "sub"
    tenant_id_claim: str = "tenant_id"
    scope_claim: str = "scope"

    def to_config(self) -> JWTVerificationConfig:
        return JWTVerificationConfig.model_validate(self.model_dump())
