from common.auth.adapters.jwks_provider import AsyncJWKSKeyProvider
from common.auth.adapters.jwt_claims_mapper import JWTClaimsPrincipalMapper
from common.auth.adapters.rs256_jwt_verifier import RS256JWTVerifier
from common.auth.adapters.static_key_provider import StaticKeyProvider
from common.auth.ports.token_verifier import TokenVerifierPort
from common.auth.settings import JWTVerificationConfig, JWTVerificationSettings


def build_token_verifier(
    settings: JWTVerificationConfig | JWTVerificationSettings,
) -> TokenVerifierPort:
    config = (
        settings.to_config()
        if isinstance(settings, JWTVerificationSettings)
        else settings
    )
    key_provider = (
        AsyncJWKSKeyProvider(
            jwks_url=config.jwks_url,
            cache_ttl_seconds=config.jwks_cache_ttl_seconds,
        )
        if config.jwks_url is not None
        else StaticKeyProvider(config.public_key_pem.get_secret_value())
    )
    principal_mapper = JWTClaimsPrincipalMapper(
        subject_claim=config.subject_claim,
        tenant_id_claim=config.tenant_id_claim,
        scope_claim=config.scope_claim,
    )
    return RS256JWTVerifier(
        key_provider=key_provider,
        principal_mapper=principal_mapper,
        issuer=config.issuer,
        audience=config.audience,
        algorithms=config.algorithms,
        leeway_seconds=config.leeway_seconds,
    )
