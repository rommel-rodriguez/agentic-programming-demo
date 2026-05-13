class AuthServiceError(Exception):
    """Base exception for auth service failures."""


class SigningKeyNotFoundError(AuthServiceError):
    """Raised when the active signing key is not present."""


class InvalidTokenRequestError(AuthServiceError):
    """Raised when a token issuance request is invalid."""


class UserAlreadyExistsError(AuthServiceError):
    """Raised when a username is already registered."""


class InvalidCredentialsError(AuthServiceError):
    """Raised when supplied user credentials are invalid."""


class RefreshTokenInvalidError(AuthServiceError):
    """Raised when a refresh token is invalid, expired, or revoked."""
