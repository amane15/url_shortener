from fastapi import Request
from app.config import REDIS_URL
from redis.asyncio import from_url, ConnectionError, TimeoutError, Redis
from redis.backoff import ExponentialBackoff
from redis.retry import Retry

from app.internal.range_counter import RangeCounter


def create_counter_redis() -> Redis:
    retry = Retry(
        ExponentialBackoff(), 5, supported_errors=(ConnectionError, TimeoutError)
    )

    return from_url(REDIS_URL, retry=retry, decode_responses=True)


def get_redis(request: Request) -> Redis:
    return request.app.state.redis


def get_counter(request: Request) -> RangeCounter:
    return request.app.state.counter
