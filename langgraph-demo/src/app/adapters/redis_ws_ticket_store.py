from dataclasses import asdict

import orjson
from redis.asyncio import Redis

from app.ports.auth import AuthenticatedPrincipal, WebSocketTicketStorePort


class RedisWebSocketTicketStore(WebSocketTicketStorePort):
    def __init__(self, redis: Redis, *, key_prefix: str = "ws-ticket"):
        self._redis = redis
        self._key_prefix = key_prefix

    def _key(self, ticket: str) -> str:
        return f"{self._key_prefix}:{ticket}"

    async def store(
        self,
        *,
        ticket: str,
        principal: AuthenticatedPrincipal,
        ttl_seconds: int,
    ) -> None:
        payload = orjson.dumps(asdict(principal))
        await self._redis.set(self._key(ticket), payload, ex=ttl_seconds)

    async def consume(self, *, ticket: str) -> AuthenticatedPrincipal | None:
        raw_payload = await self._redis.getdel(self._key(ticket))
        if raw_payload is None:
            return None

        payload = orjson.loads(raw_payload)
        return AuthenticatedPrincipal(
            user_id=int(payload["user_id"]),
            tenant_id=str(payload["tenant_id"]),
        )
