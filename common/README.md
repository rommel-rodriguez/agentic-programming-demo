# common

Shared authentication primitives for FastAPI microservices in this repository.

## Current scope

- RS256 access-token verification
- JWKS fetching and caching
- Authenticated principal models and auth errors
- FastAPI `Depends` helpers for required and optional bearer authentication

## Package layout

The package is intentionally capability-oriented rather than microservice-oriented:

- `common.auth.domain`: stable auth models and errors
- `common.auth.ports`: protocols for key retrieval, claims mapping, and token verification
- `common.auth.services`: application services/use-cases
- `common.auth.adapters`: JWT/JWKS implementations
- `common.auth.fastapi`: FastAPI boundary helpers

## Example usage

```python
from common.auth.factories import build_token_verifier
from common.auth.fastapi.dependencies import build_require_principal_dependency
from common.auth.settings import JWTVerificationSettings

settings = JWTVerificationSettings(
    issuer="https://auth.internal.example.com",
    audience="langgraph-demo",
    jwks_url="https://auth.internal.example.com/.well-known/jwks.json",
)

verifier = build_token_verifier(settings)
require_principal = build_require_principal_dependency(verifier)
```
