from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True, slots=True)
class AuthenticatedPrincipal:
    user_id: int
    tenant_id: str


class AccessTokenVerifierPort(Protocol):
    async def verify(self, token: str) -> AuthenticatedPrincipal | None:
        ...


class WebSocketTicketStorePort(Protocol):
    async def store(
        self,
        *,
        ticket: str,
        principal: AuthenticatedPrincipal,
        ttl_seconds: int,
    ) -> None:
        ...

    async def consume(self, *, ticket: str) -> AuthenticatedPrincipal | None:
        ...
