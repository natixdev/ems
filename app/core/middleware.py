import logging
import time
from collections.abc import Callable

from fastapi import Request
from starlette.responses import Response

logger = logging.getLogger('app.request')


async def log_requests(request: Request, call_next: Callable) -> Response:
    """Логирует HTTP-запросы и время обработки."""
    start_time = time.perf_counter()
    response = await call_next(request)
    duration = time.perf_counter() - start_time

    logger.info(
        '%s %s -> %s in %.3fs',
        request.method,
        request.url.path,
        response.status_code,
        duration,
    )
    return response
