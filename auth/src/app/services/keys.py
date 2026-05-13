from app.domain.errors import SigningKeyNotFoundError
from app.domain.models import KeySet
from app.ports.keys import SigningKeyGeneratorPort, SigningKeyRepositoryPort


class EnsureKeySet:
    def __init__(
        self,
        *,
        repository: SigningKeyRepositoryPort,
        generator: SigningKeyGeneratorPort,
    ):
        self._repository = repository
        self._generator = generator

    def __call__(self, *, active_kid: str, auto_generate_active_key: bool) -> KeySet:
        active_key = self._repository.get_active_key(active_kid=active_kid)
        if active_key is None:
            if not auto_generate_active_key:
                raise SigningKeyNotFoundError(
                    f"Missing active signing key pair for kid={active_kid}"
                )
            active_key = self._generator.generate(kid=active_kid)
            self._repository.save_active_key(active_key)

        public_keys = self._repository.list_public_keys()
        if not any(key.kid == active_key.kid for key in public_keys):
            public_keys = (*public_keys, active_key)
        return KeySet(active_key=active_key, public_keys=tuple(public_keys))
