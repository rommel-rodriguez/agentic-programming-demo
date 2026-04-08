class AuthError(Exception):
    """Base exception for authentication and authorization failures."""


class MissingCredentialsError(AuthError):
    """No credential was supplied."""


class InvalidCredentialsError(AuthError):
    """The supplied credential could not be verified."""


class ForbiddenError(AuthError):
    """The principal is authenticated but not allowed to perform the action."""


class KeySetUnavailableError(AuthError):
    """The signing key set could not be loaded or did not contain the expected key."""
