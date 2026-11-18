from __future__ import annotations

import base64
import hashlib
import hmac
import json
import time

from .settings import settings


def _b64(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode("ascii").rstrip("=")


def _unb64(data: str) -> bytes:
    return base64.urlsafe_b64decode(data + "=" * (-len(data) % 4))


def create_session_token(subject: str = "owner") -> str:
    now = int(time.time())
    payload = {
        "sub": subject,
        "iat": now,
        "exp": now + settings.session_days * 86400,
        "scope": "owner",
    }
    body = _b64(json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8"))
    signature = hmac.new(
        settings.session_secret.encode("utf-8"),
        body.encode("ascii"),
        hashlib.sha256,
    ).digest()
    return f"{body}.{_b64(signature)}"


def verify_session_token(token: str) -> bool:
    try:
        body, sig = token.split(".", 1)
        expected = hmac.new(
            settings.session_secret.encode("utf-8"),
            body.encode("ascii"),
            hashlib.sha256,
        ).digest()
        if not hmac.compare_digest(_unb64(sig), expected):
            return False
        payload = json.loads(_unb64(body))
        return (
            payload.get("scope") == "owner"
            and int(payload.get("exp", 0)) >= int(time.time())
        )
    except (ValueError, TypeError, json.JSONDecodeError):
        return False
