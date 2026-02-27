from __future__ import annotations

from fastapi import Depends, HTTPException, Request, status
import jwt

from app.config import settings


class AuthError(HTTPException):
    pass


def _jwks_url() -> str | None:
    if not settings.supabase_project_ref:
        return None
    return f"https://{settings.supabase_project_ref}.supabase.co/auth/v1/keys"


def _get_bearer_token(request: Request) -> str:
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        raise AuthError(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing bearer token")
    return auth.split(" ", 1)[1].strip()


def require_user(request: Request) -> dict:
    token = _get_bearer_token(request)
    jwks_url = _jwks_url()

    try:
        if jwks_url:
            jwk_client = jwt.PyJWKClient(jwks_url)
            signing_key = jwk_client.get_signing_key_from_jwt(token)
            payload = jwt.decode(token, signing_key.key, algorithms=["ES256"])
        else:
            if not settings.supabase_jwt_secret:
                raise AuthError(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Missing SUPABASE_PROJECT_REF or SUPABASE_JWT_SECRET",
                )
            payload = jwt.decode(token, settings.supabase_jwt_secret, algorithms=["HS256"])
    except jwt.PyJWTError as exc:
        raise AuthError(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token") from exc

    return payload


RequireUser = Depends(require_user)
