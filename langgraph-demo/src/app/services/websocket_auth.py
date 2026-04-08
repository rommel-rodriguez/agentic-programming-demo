import secrets

from app.ports.auth import (
    AccessTokenVerifierPort,
    AuthenticatedPrincipal,
    WebSocketTicketStorePort,
)


class WebSocketTicketService:
    def __init__(
        self,
        *,
        access_token_verifier: AccessTokenVerifierPort,
        ticket_store: WebSocketTicketStorePort,
        ttl_seconds: int,
    ):
        self._access_token_verifier = access_token_verifier
        self._ticket_store = ticket_store
        self._ttl_seconds = ttl_seconds

    async def issue_for_access_token(self, access_token: str) -> str | None:
        principal = await self._access_token_verifier.verify(access_token)
        if principal is None:
            return None

        ticket = secrets.token_urlsafe(32)
        await self._ticket_store.store(
            ticket=ticket,
            principal=principal,
            ttl_seconds=self._ttl_seconds,
        )
        return ticket

    async def consume(self, ticket: str) -> AuthenticatedPrincipal | None:
        return await self._ticket_store.consume(ticket=ticket)
