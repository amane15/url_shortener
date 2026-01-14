import jwt
from sqlalchemy import select
from app.dependencies import DBDep
from app.config import JWT_ACCESS_SECRET

from app.exception import UnAuthorizedException
from app.models.user import User
from typing import Annotated
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Depends

CredentialsDep = Annotated[HTTPAuthorizationCredentials, Depends(HTTPBearer())]


async def get_current_user(credentials: CredentialsDep, db: DBDep):
    scheme, token = credentials.scheme, credentials.credentials
    if scheme.lower() != "bearer":
        raise UnAuthorizedException(detail="Malformed authorization header")

    try:
        payload = jwt.decode(
            token,
            key=JWT_ACCESS_SECRET,
            algorithms=["HS256"],
            issuer="urlshortenerapp.in",
            audience="urlshortenerapp.api",
        )
        if payload.get("scope") != "access":
            raise UnAuthorizedException(detail="Invalid access token")

        user_id = int(payload.get("sub"))
        if user_id is None:
            raise UnAuthorizedException(detail="Invalid access token")

        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()

        if not user:
            raise UnAuthorizedException(detail="Invalid access token")

        return user
    except jwt.ExpiredSignatureError as exc:
        raise UnAuthorizedException(detail="Access token is expired")
    except jwt.InvalidTokenError as exc:
        raise UnAuthorizedException(detail="Invalid access token")
    except ValueError as exc:
        raise UnAuthorizedException(detail="Invalid access token")


CurrentUserDep = Annotated[User, Depends(get_current_user)]
