from fastapi import APIRouter, Depends, Request

from app.entrypoints.webapp.dependencies import get_jwks_document, get_key_set
from app.entrypoints.webapp.models import HealthOut, OpenIDConfigurationOut

router = APIRouter(tags=["openid"])


@router.get("/.well-known/jwks.json")
async def get_jwks(jwks_document=Depends(get_jwks_document)):
    return jwks_document


@router.get(
    "/.well-known/openid-configuration",
    response_model=OpenIDConfigurationOut,
)
async def get_openid_configuration(request: Request):
    issuer = request.app.state.settings.issuer.rstrip("/")
    return {
        "issuer": issuer,
        "jwks_uri": f"{issuer}/.well-known/jwks.json",
        # This service exposes a bootstrap-only issuance endpoint, not a public OAuth flow.
        "token_endpoint": None,
    }


@router.get("/health/live", response_model=HealthOut)
async def live():
    return {"status": "ok"}


@router.get("/health/ready", response_model=HealthOut)
async def ready(_=Depends(get_key_set)):
    return {"status": "ok"}
