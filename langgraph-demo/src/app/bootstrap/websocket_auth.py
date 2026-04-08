from redis.asyncio import Redis

from app.adapters.jwt_access_token_verifier import JWTAccessTokenVerifier
from app.adapters.redis_ws_ticket_store import RedisWebSocketTicketStore
from app.config import get_settings
from app.ports.auth import AccessTokenVerifierPort, WebSocketTicketStorePort
from app.services.websocket_auth import WebSocketTicketService


def build_redis_client(redis_url: str | None = None) -> Redis:
    settings = get_settings()
    return Redis.from_url(redis_url or settings.redis_url)


def build_access_token_verifier() -> AccessTokenVerifierPort:
    settings = get_settings()
    return JWTAccessTokenVerifier(
        secret=settings.auth_access_token_secret.get_secret_value(),
        algorithm=settings.auth_access_token_algorithm,
        audience=settings.auth_access_token_audience,
        issuer=settings.auth_access_token_issuer,
    )


def build_websocket_ticket_store(redis: Redis) -> WebSocketTicketStorePort:
    return RedisWebSocketTicketStore(redis)


def build_websocket_ticket_service(
    *,
    access_token_verifier: AccessTokenVerifierPort,
    ticket_store: WebSocketTicketStorePort,
) -> WebSocketTicketService:
    settings = get_settings()
    return WebSocketTicketService(
        access_token_verifier=access_token_verifier,
        ticket_store=ticket_store,
        ttl_seconds=settings.ws_ticket_ttl_seconds,
    )
