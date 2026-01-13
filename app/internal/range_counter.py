import asyncio
from redis.asyncio import Redis, ConnectionError, TimeoutError
from app.exception import InternalServerError, CounterUnavailable


class RangeCounter:
    def __init__(self, redis: Redis, key: str, range_size: int) -> None:
        self._redis = redis
        self._key = key
        self._range_size = range_size

        self._current = 0
        self._max = -1

        self._lock = asyncio.Lock()

    async def next(self) -> int:
        async with self._lock:
            if self._current > self._max:
                await self._aquire_range()

            value = self._current
            self._current += 1
            return value

    async def _aquire_range(self) -> None:
        try:
            end = await self._redis.incrby(self._key, self._range_size)
            self._current = end - self._range_size + 1
            self._max = end
        # Log error later
        except (ConnectionError, TimeoutError) as exc:
            raise CounterUnavailable()
        except Exception as exc:
            print(exc)
            raise InternalServerError()
