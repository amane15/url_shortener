import jwt
import os
from uuid import uuid4, UUID
from datetime import datetime, timedelta, timezone
from typing import TypedDict


ACCESS_TOKEN_EXPIRY_IN_MINUTES = 10
REFRESH_TOKEN_EXPIRY_IN_DAYS = 7


class TokenPair(TypedDict):
    access_token: str
    refresh_token: str
    jti: UUID
    refresh_token_expiry: datetime


def generate_access_token(user_id: int) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(user_id),
        "exp": now + timedelta(minutes=ACCESS_TOKEN_EXPIRY_IN_MINUTES),
        "iat": now,
        "nbf": now,
        "iss": "urlshortenerapp.in",
        "aud": "urlshortenerapp.api",
        "scope": "access",
    }

    return jwt.encode(payload, os.getenv("JWT_ACCESS_SECRET"), algorithm="HS256")


def generate_refresh_token(user_id: int) -> tuple[str, UUID, datetime]:
    now = datetime.now(timezone.utc)
    expires_at = now + timedelta(days=REFRESH_TOKEN_EXPIRY_IN_DAYS)
    jti = uuid4()
    payload = {
        "sub": str(user_id),
        "exp": expires_at,
        "iat": now,
        "nbf": now,
        "iss": "urlshortenerapp.in",
        "aud": "urlshortenerapp.api",
        "scope": "refresh",
        "jti": str(jti),
    }

    return (
        jwt.encode(payload, os.getenv("JWT_REFRESH_SECRET"), algorithm="HS256"),
        jti,
        expires_at,
    )


def generate_tokens(user_id: int) -> TokenPair:
    access_token = generate_access_token(user_id)
    refresh_token, jti, refresh_token_expiry = generate_refresh_token(user_id)

    return TokenPair(
        access_token=access_token,
        refresh_token=refresh_token,
        jti=jti,
        refresh_token_expiry=refresh_token_expiry,
    )
