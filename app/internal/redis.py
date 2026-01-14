from fastapi import Request
from redis.asyncio import from_url, ConnectionError, TimeoutError, Redis
from redis.backoff import ExponentialBackoff
from redis.retry import Retry

from app.internal.cache import RedisCache
from app.internal.range_counter import RangeCounter


def create_counter_redis(url: str) -> Redis:
    retry = Retry(
        ExponentialBackoff(), 5, supported_errors=(ConnectionError, TimeoutError)
    )

    return from_url(url, retry=retry, decode_responses=True)


def get_redis(request: Request) -> Redis:
    return request.app.state.redis


def get_counter(request: Request) -> RangeCounter:
    return request.app.state.counter


def get_cache(request: Request) -> RedisCache:
    return request.app.state.redis_cache
