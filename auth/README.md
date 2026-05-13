# auth

Authentication microservice for issuing RS256 access tokens and publishing public
verification keys through a JWKS endpoint.

## Scope

- publishes `/.well-known/jwks.json`
- publishes a minimal `/.well-known/openid-configuration`
- supports `POST /users/signup`
- supports `POST /users/signin`
- supports `POST /users/refresh`
- supports `POST /users/signout`
- signs tokens with an active RSA key identified by `kid`

## Key management model

This service supports two modes:

1. Production-oriented:
   - mount RSA key files into `AUTH_KEYS_DIR`
   - configure `AUTH_ACTIVE_KID`
   - keep `AUTH_AUTO_GENERATE_ACTIVE_KEY=false`

2. Development/bootstrap:
   - set `AUTH_AUTO_GENERATE_ACTIVE_KEY=true`
   - the service generates and persists the active RSA keypair under `AUTH_KEYS_DIR`

Best practice for production is to provision signing keys externally and mount them
or sync them into the service, rather than generating a brand-new keypair on every
startup.

## Important note on token issuance

This service intentionally implements a simpler first-party authentication model:
users sign up or sign in with username and password, then receive a short-lived
RS256 access token plus a server-revocable opaque refresh token. Other services
should validate access tokens against this service's issuer and JWKS endpoint.

Passwords are currently hashed with bcrypt. This is acceptable, though Argon2id
would be the preferred next upgrade when the dependency/runtime setup allows it.

## File naming convention

- active private key: `{kid}.private.pem`
- public key: `{kid}.public.pem`

Only the active key needs a private PEM file. Older rotated keys may remain as
public-only PEM files so they continue to appear in JWKS during token rollover.

## Example development run

```bash
AUTH_ENV=dev \
AUTH_ISSUER=http://localhost:8001 \
AUTH_AUTO_GENERATE_ACTIVE_KEY=true \
python -m uvicorn --app-dir src app.entrypoints.webapp.asgi:app --reload --port 8001
```

Before starting the app against a fresh database, run:

```bash
alembic upgrade head
```
