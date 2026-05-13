import os
from pathlib import Path

from app.domain.models import ActiveSigningKey, PublicSigningKey
from app.ports.keys import SigningKeyRepositoryPort


class FileSystemSigningKeyRepository(SigningKeyRepositoryPort):
    def __init__(self, *, keys_dir: Path):
        self._keys_dir = keys_dir
        self._keys_dir.mkdir(parents=True, exist_ok=True)

    def get_active_key(self, *, active_kid: str) -> ActiveSigningKey | None:
        private_path = self._private_path(active_kid)
        public_path = self._public_path(active_kid)
        if not private_path.exists() or not public_path.exists():
            return None
        return ActiveSigningKey(
            kid=active_kid,
            private_key_pem=private_path.read_text(),
            public_key_pem=public_path.read_text(),
        )

    def list_public_keys(self) -> tuple[PublicSigningKey, ...]:
        keys: list[PublicSigningKey] = []
        for public_path in sorted(self._keys_dir.glob("*.public.pem")):
            kid = public_path.name.removesuffix(".public.pem")
            keys.append(
                PublicSigningKey(kid=kid, public_key_pem=public_path.read_text())
            )
        return tuple(keys)

    def save_active_key(self, key: ActiveSigningKey) -> None:
        self._write_text(self._private_path(key.kid), key.private_key_pem, mode=0o600)
        self._write_text(self._public_path(key.kid), key.public_key_pem, mode=0o644)

    def _private_path(self, kid: str) -> Path:
        return self._keys_dir / f"{kid}.private.pem"

    def _public_path(self, kid: str) -> Path:
        return self._keys_dir / f"{kid}.public.pem"

    @staticmethod
    def _write_text(path: Path, content: str, *, mode: int) -> None:
        path.write_text(content)
        os.chmod(path, mode)
