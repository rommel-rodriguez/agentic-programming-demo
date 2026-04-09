from typing import Protocol


class KeySetProviderPort(Protocol):
    async def get_signing_key(self, kid: str | None) -> str | bytes:
        ...
