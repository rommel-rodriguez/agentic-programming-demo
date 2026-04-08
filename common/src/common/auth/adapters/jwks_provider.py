import asyncio
import json
import time

import httpx
import jwt

from common.auth.domain.errors import KeySetUnavailableError
from common.auth.ports.key_set_provider import KeySetProviderPort


class AsyncJWKSKeyProvider(KeySetProviderPort):
    def __init__(
        self,
        *,
        jwks_url: str,
        cache_ttl_seconds: int = 300,
        client: httpx.AsyncClient | None = None,
    ):
        self._jwks_url = jwks_url
        self._cache_ttl_seconds = cache_ttl_seconds
        self._client = client or httpx.AsyncClient(timeout=5.0)
        self._owns_client = client is None
        self._lock = asyncio.Lock()
        self._cached_keys: dict[str, str | bytes] = {}
        self._expires_at = 0.0

    async def get_signing_key(self, kid: str | None) -> str | bytes:
        keys = await self._get_keys()
        if kid is None:
            if len(keys) == 1:
                return next(iter(keys.values()))
            raise KeySetUnavailableError("JWT header did not include kid")

        key = keys.get(kid)
        if key is not None:
            return key

        keys = await self._get_keys(force_refresh=True)
        key = keys.get(kid)
        if key is None:
            raise KeySetUnavailableError(f"No signing key found for kid={kid}")
        return key

    async def aclose(self) -> None:
        if self._owns_client:
            await self._client.aclose()

    async def _get_keys(self, *, force_refresh: bool = False) -> dict[str, str | bytes]:
        if not force_refresh and self._cached_keys and time.monotonic() < self._expires_at:
            return self._cached_keys

        async with self._lock:
            if (
                not force_refresh
                and self._cached_keys
                and time.monotonic() < self._expires_at
            ):
                return self._cached_keys

            try:
                response = await self._client.get(self._jwks_url)
                response.raise_for_status()
            except httpx.HTTPError as exc:
                raise KeySetUnavailableError("Failed to load JWKS") from exc

            payload = response.json()
            keys = payload.get("keys")
            if not isinstance(keys, list):
                raise KeySetUnavailableError("JWKS payload is missing a valid keys list")

            parsed_keys: dict[str, str | bytes] = {}
            for key_data in keys:
                if not isinstance(key_data, dict):
                    continue
                kid = key_data.get("kid")
                if not isinstance(kid, str) or not kid:
                    continue
                parsed_keys[kid] = jwt.algorithms.RSAAlgorithm.from_jwk(
                    json.dumps(key_data)
                )

            if not parsed_keys:
                raise KeySetUnavailableError("JWKS did not contain any usable RSA keys")

            self._cached_keys = parsed_keys
            self._expires_at = time.monotonic() + self._cache_ttl_seconds
            return self._cached_keys
