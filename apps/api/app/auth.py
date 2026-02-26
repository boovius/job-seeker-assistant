from __future__ import annotations

from fastapi import Depends, HTTPException, Request, status
import jwt

from app.config import settings


class AuthError(HTTPException):
    pass


def _get_bearer_token(request: Request) -> str:
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        raise AuthError(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing bearer token")
    return auth.split(" ", 1)[1].strip()


def require_user(request: Request) -> dict:
    token = _get_bearer_token(request)
    if not settings.supabase_jwt_secret:
        raise AuthError(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Missing SUPABASE_JWT_SECRET")

    try:
        payload = jwt.decode(token, settings.supabase_jwt_secret, algorithms=["HS256"])
    except jwt.PyJWTError as exc:
        raise AuthError(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token") from exc

    return payload


RequireUser = Depends(require_user)
