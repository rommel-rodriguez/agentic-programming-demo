import jwt
import pytest

from app.adapters.jwt_access_token_verifier import JWTAccessTokenVerifier
from app.ports.auth import AuthenticatedPrincipal
from app.services.websocket_auth import WebSocketTicketService


class InMemoryTicketStore:
    def __init__(self):
        self._tickets: dict[str, AuthenticatedPrincipal] = {}

    async def store(
        self,
        *,
        ticket: str,
        principal: AuthenticatedPrincipal,
        ttl_seconds: int,
    ) -> None:
        self._tickets[ticket] = principal

    async def consume(self, *, ticket: str) -> AuthenticatedPrincipal | None:
        return self._tickets.pop(ticket, None)


class StubAccessTokenVerifier:
    def __init__(self, principal: AuthenticatedPrincipal | None):
        self._principal = principal

    async def verify(self, token: str) -> AuthenticatedPrincipal | None:
        return self._principal


@pytest.mark.asyncio
async def test_issue_and_consume_ticket_is_single_use():
    principal = AuthenticatedPrincipal(user_id=7, tenant_id="tenant-7")
    service = WebSocketTicketService(
        access_token_verifier=StubAccessTokenVerifier(principal),
        ticket_store=InMemoryTicketStore(),
        ttl_seconds=30,
    )

    ticket = await service.issue_for_access_token("valid-token")

    assert ticket is not None
    assert await service.consume(ticket) == principal
    assert await service.consume(ticket) is None


@pytest.mark.asyncio
async def test_issue_ticket_returns_none_for_invalid_access_token():
    service = WebSocketTicketService(
        access_token_verifier=StubAccessTokenVerifier(None),
        ticket_store=InMemoryTicketStore(),
        ttl_seconds=30,
    )

    assert await service.issue_for_access_token("invalid-token") is None


@pytest.mark.asyncio
async def test_jwt_access_token_verifier_extracts_principal():
    token = jwt.encode(
        {"sub": "42", "tenant_id": "tenant-42"},
        "secret",
        algorithm="HS256",
    )
    verifier = JWTAccessTokenVerifier(secret="secret", algorithm="HS256")

    principal = await verifier.verify(token)

    assert principal == AuthenticatedPrincipal(user_id=42, tenant_id="tenant-42")


@pytest.mark.asyncio
async def test_jwt_access_token_verifier_rejects_invalid_token():
    verifier = JWTAccessTokenVerifier(secret="secret", algorithm="HS256")

    principal = await verifier.verify("not-a-jwt")

    assert principal is None
