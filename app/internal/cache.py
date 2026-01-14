from redis.asyncio import Redis, ConnectionError, TimeoutError

from app.exception import CacheUnavailable, InternalServerError


class RedisCache:
    def __init__(self, redis: Redis) -> None:
        self._redis = redis

    async def get(self, key: str) -> str | None:
        try:
            value = await self._redis.get(key)
            return value
        except (ConnectionError, TimeoutError) as exc:
            raise CacheUnavailable()
        except Exeption as exc:
            raise InternalServerError()

    async def set(self, key: str, value: str, ttl: int):
        try:
            if ttl:
                await self._redis.setex(key, ttl, value)
            else:
                await self._redis.set(key, value)
        except (ConnectionError, TimeoutError) as exc:
            raise CacheUnavailable()
        except Exception as exc:
            raise InternalServerError()

    async def delete(self, key: str):
        try:
            await self._redis.delete(key)
        except (ConnectionError, TimeoutError) as exc:
            raise CacheUnavailable()
        except Exception as exc:
            raise InternalServerError()
