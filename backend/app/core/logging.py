import logging
import time
from collections import Counter
from collections.abc import Awaitable, Callable

from fastapi import Request, Response

REQUEST_COUNTER: Counter[str] = Counter()


def configure_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )


async def request_logging_middleware(
    request: Request,
    call_next: Callable[[Request], Awaitable[Response]],
) -> Response:
    started = time.perf_counter()
    response = await call_next(request)
    elapsed_ms = round((time.perf_counter() - started) * 1000, 2)
    route = f"{request.method} {request.url.path}"
    REQUEST_COUNTER[route] += 1
    logging.getLogger("signcast.request").info(
        "method=%s path=%s status=%s duration_ms=%s",
        request.method,
        request.url.path,
        response.status_code,
        elapsed_ms,
    )
    return response
