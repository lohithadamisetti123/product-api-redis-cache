import json
from typing import Optional
import redis
from src.config import settings
from src.models.product_schema import ProductOut

_redis_client: Optional[redis.Redis] = None


def get_redis_client() -> Optional[redis.Redis]:
    global _redis_client
    if _redis_client is None:
        try:
            _redis_client = redis.Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                decode_responses=True,
            )
            _redis_client.ping()
        except Exception:
            _redis_client = None
    return _redis_client


def _product_cache_key(product_id: str) -> str:
    return f"product:{product_id}"


def get_product_from_cache(product_id: str) -> Optional[ProductOut]:
    client = get_redis_client()
    if client is None:
        return None
    try:
        data = client.get(_product_cache_key(product_id))
        if not data:
            return None
        obj = json.loads(data)
        return ProductOut.model_validate(obj)
    except Exception:
        return None


def set_product_in_cache(product: ProductOut, ttl_seconds: int) -> None:
    client = get_redis_client()
    if client is None:
        return
    try:
        client.setex(
            _product_cache_key(product.id),
            ttl_seconds,
            json.dumps(product.model_dump()),
        )
    except Exception:
        pass


def invalidate_product_cache(product_id: str) -> None:
    client = get_redis_client()
    if client is None:
        return
    try:
        client.delete(_product_cache_key(product_id))
    except Exception:
        pass
