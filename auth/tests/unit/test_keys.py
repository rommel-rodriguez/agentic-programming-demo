from pathlib import Path

from app.adapters.filesystem_keys import FileSystemSigningKeyRepository
from app.adapters.rsa_keys import RSAKeyGenerator
from app.services.keys import EnsureKeySet


def test_ensure_key_set_generates_and_persists_active_key(tmp_path: Path):
    repository = FileSystemSigningKeyRepository(keys_dir=tmp_path)
    service = EnsureKeySet(repository=repository, generator=RSAKeyGenerator())

    key_set = service(active_kid="main", auto_generate_active_key=True)

    assert key_set.active_key.kid == "main"
    assert (tmp_path / "main.private.pem").exists()
    assert (tmp_path / "main.public.pem").exists()
    assert any(key.kid == "main" for key in key_set.public_keys)
