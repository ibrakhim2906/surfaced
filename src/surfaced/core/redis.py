from time import time

from redis import RedisError
from redis.asyncio.client import Redis

PossibleCacheValueTypes = str | float | int


async def get_cache(redis_client: Redis, key: str) -> str | None:
    try:
        return await redis_client.get(key)
    except RedisError:
        return None


async def set_cache(
    redis_client: Redis, key: str, value: PossibleCacheValueTypes, ttl: int
):

    _ = await redis_client.set(key, value, ex=ttl)


async def delete_cache(redis_client: Redis, key: str):

    _ = await redis_client.delete(key)


async def key_exists_cache(redis_client: Redis, key: str):

    result = await redis_client.exists(key)

    if result:
        return True
    else:
        return False


async def keys_delete_by_pattern(redis_client: Redis, pattern: str) -> None:
    keys = await redis_client.keys(pattern)

    if keys:
        await redis_client.delete(*keys)


async def rate_limit_exceeded(
    redis_client: Redis, key: str, max_requests: int, window_seconds: int
) -> bool:

    now = time()
    clear_before = now - window_seconds

    async with redis_client.pipeline(transaction=True) as pipe:
        pipe.zremrangebyscore(key, 0, clear_before)
        pipe.zcard(key)
        pipe.zadd(key, {str(now): now})
        pipe.expire(key, window_seconds + 10)

        _, current_request_count, _, _ = await pipe.execute()

    return current_request_count > max_requests
