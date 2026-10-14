import json
import redis.asyncio as aioredis
from typing import Dict, Any
import os

redis_client = aioredis.Redis.from_url(os.getenv("REDIS_URL", "redis://redis:6379/0"))

async def get_revenue_summary(property_id: str, tenant_id: str) -> Dict[str, Any]:
    """
    Fetches revenue summary, utilizing caching to improve performance.
    """
    cache_key = f"revenue:{tenant_id}:{property_id}"  # BUG FIX: tenant_id scopes the key

    cached = await redis_client.get(cache_key)
    if cached:
        return json.loads(cached)

    from app.services.reservations import calculate_total_revenue

    result = await calculate_total_revenue(property_id, tenant_id)

    await redis_client.setex(cache_key, 300, json.dumps(result))

    return result