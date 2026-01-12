from datetime import datetime
from pydantic import BaseModel, EmailStr, ConfigDict, Field


class RegisterUserBody(BaseModel):
    name: str
    email: EmailStr
    password: str = Field(min_length=8)


class UserCreateResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    name: str
    created_at: datetime
    updated_at: datetime
    version: int


class UserLoginBody(BaseModel):
    email: EmailStr
    password: str


class UserLoginResponse(BaseModel):
    refresh_token: str
    access_token: str


class RefreshBody(BaseModel):
    refresh_token: str
