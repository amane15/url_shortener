from abc import ABC
from typing import Any

from fastapi import status


class AppException(Exception, ABC):
    status_code: int
    detail: Any

    def __init__(self, status_code: int | None = None, detail: Any | None = None):
        if type(self) is AppException:
            raise TypeError(
                "AppException is abstract and cannot be raised directly. Use concrete subclass instead."
            )

        if status_code is not None:
            self.status_code = status_code
        if detail is not None:
            self.detail = detail

        super().__init__(self.detail)

    def __init_subclass__(cls) -> None:
        if not hasattr(cls, "status_code"):
            raise TypeError(f"{cls.__name__} must define status_code")
        if not hasattr(cls, "detail"):
            raise TypeError(f"{cls.__name__} must define detail")


class BadRequestException(AppException):
    status_code = status.HTTP_400_BAD_REQUEST
    detail = "Bad request"


class UnAuthorizedException(AppException):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Unauthorized"


class NotFoundResponse(AppException):
    status_code = status.HTTP_404_NOT_FOUND
    detail = "The requested resource could not be found"


class InternalServerError(AppException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    detail = "Internal server error"


class ForbiddenException(AppException):
    status_code = status.HTTP_403_FORBIDDEN
    detail = "Forbidden"


class CounterUnavailable(AppException):
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    detail = "Service Unavailable"
