from datetime import datetime, timezone
import os
import uuid
import jwt
from uuid import UUID
from fastapi import APIRouter, status
from sqlalchemy import select, update
from sqlalchemy.exc import OperationalError, IntegrityError
from app.config import JWT_REFRESH_SECRET
from app.dependencies import DBDep
from app.internal.tokens import (
    generate_access_token,
    generate_refresh_token,
)
from app.models.refresh_token import RefreshToken
from app.models.user import User
from app.exception import (
    BadRequestException,
    InternalServerError,
    UnAuthorizedException,
)
from app.schemas.users import (
    RegisterUserBody,
    UserCreateResponse,
    UserLoginBody,
    UserLoginResponse,
    RefreshBody,
)
from argon2 import PasswordHasher
from argon2.exceptions import (
    HashingError,
    VerifyMismatchError,
    InvalidHashError,
    VerificationError,
)
from app.internal.get_current_user import CredentialsDep, CurrentUserDep

router = APIRouter(prefix="/users")
password_hasher = PasswordHasher()


@router.get("/me", response_model=UserCreateResponse, status_code=status.HTTP_200_OK)
async def me(current_user: CurrentUserDep):
    return current_user


@router.post(
    "/register", response_model=UserLoginResponse, status_code=status.HTTP_201_CREATED
)
async def register_user(body: RegisterUserBody, db: DBDep):
    try:
        hash = password_hasher.hash(body.password)
        user = User(name=body.name, email=body.email, password_hash=hash)
        db.add(user)
        await db.commit()
        await db.refresh(user)

        access_token = generate_access_token(user.id)
        refresh_token, jti, expires_at = generate_refresh_token(user.id)

        token_hash = password_hasher.hash(refresh_token)

        token = RefreshToken(
            id=jti, user_id=user.id, token_hash=token_hash, expires_at=expires_at
        )
        db.add(token)
        await db.commit()

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
        }

    # TODO: log error
    except HashingError as exc:
        raise InternalServerError()
    except IntegrityError as exc:
        await db.rollback()
        raise BadRequestException(detail="User already exist")
    except OperationalError as exc:
        await db.rollback()
        raise InternalServerError()
    except Exception as exc:
        await db.rollback()
        raise InternalServerError()


@router.post("/login", response_model=UserLoginResponse, status_code=status.HTTP_200_OK)
async def login(body: UserLoginBody, db: DBDep):
    try:
        result = await db.execute(select(User).where(User.email == body.email))
        user = result.scalar_one_or_none()

        if not user:
            raise BadRequestException(detail="Email or password is incorrect")

        matches = password_hasher.verify(user.password_hash, body.password)
        if not matches:
            raise BadRequestException(detail="Email or password is incorrect")

        access_token = generate_access_token(user.id)
        refresh_token, jti, expires_at = generate_refresh_token(user.id)
        token_hash = password_hasher.hash(refresh_token)

        rf_token = RefreshToken(
            id=jti, user_id=user.id, token_hash=token_hash, expires_at=expires_at
        )

        db.add(rf_token)
        await db.commit()

        return {"access_token": access_token, "refresh_token": refresh_token}

    except (VerifyMismatchError, VerificationError, InvalidHashError) as exc:
        raise BadRequestException(detail="Email or password is incorrect")
    except BadRequestException as exc:
        raise
    except Exception as exc:
        raise InternalServerError()


@router.post(
    "/refresh", response_model=UserLoginResponse, status_code=status.HTTP_200_OK
)
async def refresh_access(body: RefreshBody, db: DBDep):
    try:
        payload = jwt.decode(
            body.refresh_token,
            os.getenv("JWT_REFRESH_SECRET"),
            algorithms=["HS256"],
            issuer="urlshortenerapp.in",
            audience="urlshortenerapp.api",
        )

        # First check if it is a valid scope
        if payload["scope"] != "refresh":
            raise BadRequestException(detail="Invalid token scope")

        jti = UUID(payload["jti"])
        user_id = int(payload["sub"])

        # Fetch the token with jti
        result = await db.execute(select(RefreshToken).where(RefreshToken.id == jti))
        rf_token = result.scalar_one_or_none()

        if not rf_token:
            raise BadRequestException(detail="Invalid refresh token")

        # Then check for reuse detection
        # If detected stop the further processing raise exception
        if rf_token.revoked:
            result = await db.execute(
                update(RefreshToken)
                .where(RefreshToken.user_id == user_id)
                .values(revoked=True)
            )
            await db.commit()
            raise BadRequestException(
                detail="Invalid refresh token. Malicious activity detected."
            )

        # Check for expired token
        if rf_token.expires_at < datetime.now(timezone.utc):
            raise BadRequestException(detail="Invalid refresh token")

        # Verify the given token with stored hash
        # This method raises exception if verification fails
        password_hasher.verify(rf_token.token_hash, body.refresh_token)

        # At this point all verifcation is done.
        # Generate new access token
        # Rotate or generate new refresh token and revoke previous token
        access_token = generate_access_token(user_id)
        refresh_token, jti, expires_at = generate_refresh_token(user_id)
        token_hash = password_hasher.hash(refresh_token)
        new_rf_token = RefreshToken(
            id=jti, user_id=user_id, token_hash=token_hash, expires_at=expires_at
        )
        rf_token.revoked = True

        db.add(new_rf_token)
        await db.commit()

        return {"access_token": access_token, "refresh_token": refresh_token}

    # TODO: add logs later
    except jwt.InvalidTokenError as exc:
        # inspect decode error further
        raise BadRequestException()
    except ValueError as exc:
        # invalid uuid hence invalid jti
        raise BadRequestException()
    except (VerifyMismatchError, VerificationError, InvalidHashError) as exc:
        raise BadRequestException(detail="Invalid refresh token")


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(credentials: CredentialsDep, db: DBDep):
    scheme, token = credentials.scheme, credentials.credentials
    if scheme.lower() != "bearer":
        raise UnAuthorizedException(detail="Malformed authorization header")

    try:
        payload = jwt.decode(
            token,
            key=JWT_REFRESH_SECRET,
            algorithms=["HS256"],
            issuer="urlshortenerapp.in",
            audience="urlshortenerapp.api",
        )
        if payload.get("scope") != "refresh":
            raise UnAuthorizedException()
        jti = payload.get("jti")
        if not jti:
            raise UnAuthorizedException(detail="Invalid refresh token")

        jti = UUID(jti)
        result = await db.execute(select(RefreshToken).where(RefreshToken.id == jti))
        rf_token = result.scalar_one_or_none()

        if not rf_token:
            raise BadRequestException(detail="Refresh token does not exist")

        await db.delete(rf_token)
        await db.commit()
    except jwt.ExpiredSignatureError as exc:
        raise UnAuthorizedException(detail="Refresh token expired")
    except jwt.InvalidTokenError as exc:
        raise UnAuthorizedException(detail="Invalid refresh token")
    except ValueError as exc:
        raise UnAuthorizedException(detail="Invalid refresh token")
