from __future__ import annotations

import base64
import hashlib
import hmac
import json
import time
from typing import Literal

from fastapi import Depends, Header, HTTPException, status

from .settings import settings

Role = Literal["readonly", "admin"]


def _b64(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode("ascii").rstrip("=")


def _unb64(data: str) -> bytes:
    return base64.urlsafe_b64decode(data + "=" * (-len(data) % 4))


def create_token(role: Role) -> str:
    payload = {"role": role, "exp": int(time.time()) + settings.token_ttl_seconds}
    body = _b64(json.dumps(payload, separators=(",", ":")).encode("utf-8"))
    sig = hmac.new(settings.jwt_secret.encode("utf-8"), body.encode("ascii"), hashlib.sha256).digest()
    return f"{body}.{_b64(sig)}"


def verify_token(token: str) -> Role:
    try:
        body, sig = token.split(".", 1)
        expected = _b64(hmac.new(settings.jwt_secret.encode("utf-8"), body.encode("ascii"), hashlib.sha256).digest())
        if not hmac.compare_digest(sig, expected):
            raise ValueError("bad signature")
        payload = json.loads(_unb64(body))
        if int(payload.get("exp", 0)) < int(time.time()):
            raise ValueError("expired")
        role = payload.get("role")
        if role not in {"readonly", "admin"}:
            raise ValueError("bad role")
        return role
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token") from exc


def role_from_password(password: str) -> Role | None:
    if password and hmac.compare_digest(password, settings.admin_password):
        return "admin"
    if password and hmac.compare_digest(password, settings.readonly_password):
        return "readonly"
    return None


def current_role(authorization: str | None = Header(default=None)) -> Role:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing bearer token")
    return verify_token(authorization.removeprefix("Bearer ").strip())


def require_readonly(role: Role = Depends(current_role)) -> Role:
    return role


def require_admin(role: Role = Depends(current_role)) -> Role:
    if role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    return role
