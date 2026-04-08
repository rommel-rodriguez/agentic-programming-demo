from common.auth.ports.key_set_provider import KeySetProviderPort


class StaticKeyProvider(KeySetProviderPort):
    def __init__(self, public_key_pem: str):
        self._public_key_pem = public_key_pem

    async def get_signing_key(self, kid: str | None) -> str | bytes:
        return self._public_key_pem
