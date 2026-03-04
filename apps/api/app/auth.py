from __future__ import annotations

import logging

from fastapi import Depends, HTTPException, Request, status
import jwt

from app.config import settings


class AuthError(HTTPException):
    pass


logger = logging.getLogger("app.auth")


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
    if settings.api_local_debug:
        return {"sub": settings.api_local_debug_user_id, "role": "local-debug"}

    token = _get_bearer_token(request)
    jwks_url = _jwks_url()

    try:
        if jwks_url:
            jwk_client = jwt.PyJWKClient(jwks_url)
            signing_key = jwk_client.get_signing_key_from_jwt(token)
            payload = jwt.decode(
                token,
                signing_key.key,
                algorithms=["ES256"],
                audience=settings.supabase_jwt_audience,
            )
        else:
            if not settings.supabase_jwt_secret:
                raise AuthError(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Missing SUPABASE_PROJECT_REF or SUPABASE_JWT_SECRET",
                )
            payload = jwt.decode(
                token,
                settings.supabase_jwt_secret,
                algorithms=["HS256"],
                audience=settings.supabase_jwt_audience,
            )
    except jwt.PyJWTError as exc:
        try:
            header = jwt.get_unverified_header(token)
            kid = header.get("kid")
        except jwt.PyJWTError:
            kid = None
        logger.warning("JWT verification failed", extra={"kid": kid, "jwks_url": jwks_url, "error": str(exc)})
        detail = "Invalid token"
        if settings.api_env != "production":
            detail = f"Invalid token: {exc}"
        raise AuthError(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail) from exc

    return payload


RequireUser = Depends(require_user)
