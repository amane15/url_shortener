from fastapi import FastAPI
from fastapi.responses import JSONResponse

from app.exception import AppException
from .routers import urls, users
from dotenv import load_dotenv

import os

load_dotenv()

app = FastAPI()


def check_env_var(env):
    env_val = os.getenv(env)
    if not env_val:
        raise RuntimeError(f"{env} environment variable is missing")

    if env == "JWT_ACCESS_SECRET" or env == "JWT_REFRESH_SECRET":
        if len(env_val) < 64:
            raise RuntimeError(f"{env} too short")


check_env_var("JWT_ACCESS_SECRET")
check_env_var("JWT_REFRESH_SECRET")
check_env_var("DATABASE_URL")


@app.exception_handler(AppException)
def app_exception_handler(_, exc: AppException):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


app.include_router(urls.router)
app.include_router(users.router)


# @app.get("/")
# async def root():
#     return {"message": "running"}
