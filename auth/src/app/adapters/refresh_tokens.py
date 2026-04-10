import secrets

from app.ports.refresh_tokens import RefreshTokenGeneratorPort


class OpaqueRefreshTokenGenerator(RefreshTokenGeneratorPort):
    def generate(self) -> str:
        return secrets.token_urlsafe(48)
