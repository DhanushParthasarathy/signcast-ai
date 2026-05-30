from time import time

from fastapi import Depends, HTTPException, Request, status
from redis.exceptions import RedisError

from app.core.cache import RedisCache, get_cache
from app.core.config import Settings, get_settings


class RateLimiter:
    def __init__(self, cache: RedisCache, settings: Settings) -> None:
        self.cache = cache
        self.settings = settings

    def check(self, request: Request) -> None:
        client = request.client.host if request.client else "unknown"
        window = int(time() // self.settings.rate_limit_window_seconds)
        key = f"rate:{client}:{window}"
        try:
            current = self.cache.client.incr(key)
            if current == 1:
                self.cache.client.expire(key, self.settings.rate_limit_window_seconds)
        except RedisError:
            return

        if current > self.settings.rate_limit_requests:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded. Please retry shortly.",
            )


def rate_limit(
    request: Request,
    cache: RedisCache = Depends(get_cache),
    settings: Settings = Depends(get_settings),
) -> None:
    RateLimiter(cache, settings).check(request)
