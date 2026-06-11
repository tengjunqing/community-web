"""Redis 连接配置"""

import redis.asyncio as redis
from app.config import settings

# 创建 Redis 连接池
redis_pool = redis.ConnectionPool.from_url(
    settings.REDIS_URL,
    decode_responses=True,
    max_connections=20,
)


async def get_redis() -> redis.Redis:
    """获取 Redis 连接"""
    return redis.Redis(connection_pool=redis_pool)


async def close_redis():
    """关闭 Redis 连接"""
    await redis_pool.aclose()
