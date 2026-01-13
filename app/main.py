import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from app.exception import AppException
from app.internal.redis import create_counter_redis
from .routers import urls, users
from dotenv import load_dotenv
from app.internal.range_counter import RangeCounter
from app.config import COUNTER_KEY, COUNTER_RANGE_SIZE

load_dotenv()


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
check_env_var("COUNTER_RANGE_SIZE")
check_env_var("COUNTER_KEY")
check_env_var("REDIS_URL")


@asynccontextmanager
async def lifespan(app: FastAPI):
    redis = create_counter_redis()
    counter = RangeCounter(redis, COUNTER_KEY, COUNTER_RANGE_SIZE)

    app.state.redis = redis
    app.state.counter = counter
    yield
    await app.state.redis.close()


app = FastAPI(lifespan=lifespan)


@app.exception_handler(AppException)
def app_exception_handler(_, exc: AppException):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


app.include_router(urls.router)
app.include_router(users.router)


# @app.get("/")
# async def root():
#     return {"message": "running"}
