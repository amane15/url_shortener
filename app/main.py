import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from app.exception import AppException
from app.internal import redis
from app.internal.cache import RedisCache
from app.internal.redis import create_counter_redis
from .routers import urls, users
from dotenv import load_dotenv
from app.internal.range_counter import RangeCounter
from app.config import (
    COUNTER_KEY,
    COUNTER_RANGE_SIZE,
    REDIS_COUNTER_URL,
    REDIS_CACHE_URL,
)

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
    redis_counter = create_counter_redis(REDIS_COUNTER_URL)
    counter = RangeCounter(redis_counter, COUNTER_KEY, COUNTER_RANGE_SIZE)

    redis_cache_instance = create_counter_redis(REDIS_CACHE_URL)

    app.state.redis = redis_counter
    app.state.counter = counter

    app.state.redis_cache_instance = redis_cache_instance
    app.state.redis_cache = RedisCache(redis_cache_instance)
    yield
    await app.state.redis.close()
    await app.state.redis_cache_instance.close()


app = FastAPI(lifespan=lifespan)


@app.exception_handler(AppException)
def app_exception_handler(_, exc: AppException):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


app.include_router(urls.router)
app.include_router(users.router)


# @app.get("/")
# async def root():
#     return {"message": "running"}
