import json
from typing import Any

from redis import Redis
from redis.exceptions import RedisError

from app.core.config import get_settings


class RedisCache:
    def __init__(self, url: str, default_ttl_seconds: int) -> None:
        self.default_ttl_seconds = default_ttl_seconds
        self.client = Redis.from_url(url, decode_responses=True)

    def get_json(self, key: str) -> Any | None:
        try:
            value = self.client.get(key)
        except RedisError:
            return None
        return json.loads(value) if value else None

    def set_json(self, key: str, value: Any, ttl_seconds: int | None = None) -> None:
        try:
            self.client.setex(key, ttl_seconds or self.default_ttl_seconds, json.dumps(value, default=str))
        except RedisError:
            return

    def delete_prefix(self, prefix: str) -> None:
        try:
            for key in self.client.scan_iter(f"{prefix}*"):
                self.client.delete(key)
        except RedisError:
            return


def get_cache() -> RedisCache:
    settings = get_settings()
    return RedisCache(settings.redis_url, settings.redis_cache_ttl_seconds)
