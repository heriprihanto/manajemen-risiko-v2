"""Verifikasi Firebase ID token tanpa service account.

Token Firebase (Google Identity) ditandatangani RS256 oleh akun sistem Google.
Kunci publiknya tersedia sebagai JWKS, sehingga signature + klaim (iss/aud/exp)
dapat diverifikasi langsung tanpa firebase-admin / service account.
"""
import jwt
from fastapi import Depends, Header, HTTPException
from jwt import PyJWKClient

from app.core.config import settings

JWKS_URL = "https://www.googleapis.com/service_accounts/v1/jwk/securetoken@system.gserviceaccount.com"

_jwk_client = PyJWKClient(JWKS_URL)


def verify_id_token(token: str) -> dict:
    project = settings.FIREBASE_PROJECT_ID
    try:
        signing_key = _jwk_client.get_signing_key_from_jwt(token)
        claims = jwt.decode(
            token,
            signing_key.key,
            algorithms=["RS256"],
            audience=project,
            issuer=f"https://securetoken.google.com/{project}",
        )
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(401, f"Token tidak valid: {exc}") from exc

    if not claims.get("sub"):
        raise HTTPException(401, "Token tidak memiliki subject (uid)")
    return claims


def current_user(authorization: str = Header(default="")) -> dict:
    """Dependency FastAPI: ambil & verifikasi Bearer token, kembalikan klaim user."""
    if not authorization.lower().startswith("bearer "):
        raise HTTPException(401, "Authorization Bearer token diperlukan")
    token = authorization.split(" ", 1)[1].strip()
    claims = verify_id_token(token)
    return {
        "uid": claims.get("sub"),
        "email": claims.get("email"),
        "name": claims.get("name") or claims.get("email"),
        "email_verified": claims.get("email_verified", False),
        "picture": claims.get("picture"),
    }


UserDep = Depends(current_user)
