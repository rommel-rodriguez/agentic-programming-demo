from app.adapters.rsa_keys import RSAJWKBuilder, RSAKeyGenerator
from app.domain.models import KeySet
from app.services.jwks import BuildJWKS


def test_build_jwks_includes_public_key_metadata():
    active_key = RSAKeyGenerator().generate(kid="main")
    key_set = KeySet(active_key=active_key, public_keys=(active_key,))

    document = BuildJWKS(jwk_builder=RSAJWKBuilder())(key_set)

    assert len(document["keys"]) == 1
    assert document["keys"][0]["kid"] == "main"
    assert document["keys"][0]["alg"] == "RS256"
    assert document["keys"][0]["use"] == "sig"
