from typing import Protocol

from app.domain.models import ActiveSigningKey, PublicSigningKey


class SigningKeyRepositoryPort(Protocol):
    def get_active_key(self, *, active_kid: str) -> ActiveSigningKey | None:
        ...

    def list_public_keys(self) -> tuple[PublicSigningKey, ...]:
        ...

    def save_active_key(self, key: ActiveSigningKey) -> None:
        ...


class SigningKeyGeneratorPort(Protocol):
    def generate(self, *, kid: str) -> ActiveSigningKey:
        ...
