from typing import Protocol


class RefreshTokenGeneratorPort(Protocol):
    def generate(self) -> str:
        ...
