from fastapi import APIRouter, status
from sqlalchemy import except_, select
from sqlalchemy.exc import OperationalError, IntegrityError
from app.dependencies import DBDep
from app.models.user import User
from app.exception import BadRequestException, InternalServerError
from app.schemas.users import (
    UserCreateResponse,
    RegisterUserBody,
    UserLoginBody,
    UserLoginResponse,
)
from argon2 import PasswordHasher
from argon2.exceptions import (
    HashingError,
    VerifyMismatchError,
    InvalidHashError,
    VerificationError,
)

router = APIRouter(prefix="/users")


@router.post(
    "/register", response_model=UserCreateResponse, status_code=status.HTTP_201_CREATED
)
async def register_user(body: RegisterUserBody, db: DBDep):
    try:
        ph = PasswordHasher()
        hash = ph.hash(body.password)
        user = User(name=body.name, email=body.email, password_hash=hash)
        db.add(user)
        await db.commit()
        await db.refresh(user)

        return user

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
        ph = PasswordHasher()
        result = await db.execute(select(User).where(User.email == body.email))
        user = result.scalar_one_or_none()

        if not user:
            raise BadRequestException(detail="Email or password is incorrect")

        matches = ph.verify(user.password_hash, body.password)
        if matches:
            return {"access_token": "access_token", "refresh_token": "refresh_token"}

    except (VerifyMismatchError, VerificationError, InvalidHashError) as exc:
        raise BadRequestException(detail="Email or password is incorrect")
    except BadRequestException as exc:
        raise
    except Exception as exc:
        raise InternalServerError()
