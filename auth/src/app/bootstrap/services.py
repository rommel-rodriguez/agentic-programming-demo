from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.adapters.filesystem_keys import FileSystemSigningKeyRepository
from app.adapters.jwt_signer import RS256JWTSigner
from app.adapters.password_hasher import BcryptPasswordHasher
from app.adapters.refresh_tokens import OpaqueRefreshTokenGenerator
from app.adapters.rsa_keys import RSAJWKBuilder, RSAKeyGenerator
from app.adapters.sqlalchemy_uow import SQLAlchemyUnitOfWork
from app.config import get_settings
from app.services.authentication import RefreshUserSession, SignInUser, SignOutUser, SignUpUser
from app.services.jwks import BuildJWKS
from app.services.keys import EnsureKeySet
from app.services.tokens import IssueAccessToken, IssueSessionTokens


def build_key_repository():
    settings = get_settings()
    return FileSystemSigningKeyRepository(keys_dir=settings.keys_dir)


def build_key_generator():
    return RSAKeyGenerator()


def build_uow_factory(session_factory: async_sessionmaker[AsyncSession]):
    def factory():
        return SQLAlchemyUnitOfWork(session_factory)

    return factory


def build_key_set():
    settings = get_settings()
    ensure_key_set = EnsureKeySet(
        repository=build_key_repository(),
        generator=build_key_generator(),
    )
    return ensure_key_set(
        active_kid=settings.active_kid,
        auto_generate_active_key=settings.auto_generate_active_key,
    )


def build_issue_access_token() -> IssueAccessToken:
    settings = get_settings()
    return IssueAccessToken(
        signer=RS256JWTSigner(),
        issuer=settings.issuer,
        default_audience=settings.default_audience,
        default_ttl_seconds=settings.access_token_ttl_seconds,
        max_ttl_seconds=settings.max_access_token_ttl_seconds,
    )


def build_issue_session_tokens() -> IssueSessionTokens:
    settings = get_settings()
    return IssueSessionTokens(
        access_token_issuer=build_issue_access_token(),
        refresh_token_generator=OpaqueRefreshTokenGenerator(),
        refresh_token_ttl_seconds=settings.refresh_token_ttl_seconds,
        access_token_ttl_seconds=settings.access_token_ttl_seconds,
    )


def build_signup_user(session_factory) -> SignUpUser:
    return SignUpUser(
        uow_factory=build_uow_factory(session_factory),
        password_hasher=BcryptPasswordHasher(),
        session_token_issuer=build_issue_session_tokens(),
    )


def build_signin_user(session_factory) -> SignInUser:
    return SignInUser(
        uow_factory=build_uow_factory(session_factory),
        password_hasher=BcryptPasswordHasher(),
        session_token_issuer=build_issue_session_tokens(),
    )


def build_refresh_user_session(session_factory) -> RefreshUserSession:
    return RefreshUserSession(
        uow_factory=build_uow_factory(session_factory),
        session_token_issuer=build_issue_session_tokens(),
    )


def build_signout_user(session_factory) -> SignOutUser:
    return SignOutUser(uow_factory=build_uow_factory(session_factory))


def build_jwks_document(key_set):
    return BuildJWKS(jwk_builder=RSAJWKBuilder())(key_set)
