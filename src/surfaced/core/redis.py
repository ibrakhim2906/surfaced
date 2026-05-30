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
