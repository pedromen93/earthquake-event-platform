"""Request context middleware for correlation and access logging."""

from time import perf_counter
from uuid import uuid4

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.types import ASGIApp

from app.infrastructure.logging.logger import get_logger
from app.infrastructure.logging.request_context import set_request_id


class RequestContextMiddleware(BaseHTTPMiddleware):
    """Attach a request identifier and emit request lifecycle logs."""

    def __init__(self, app: ASGIApp) -> None:
        """Initialize middleware with the target ASGI application."""

        super().__init__(app)

    async def dispatch(
        self,
        request: Request,
        call_next: RequestResponseEndpoint,
    ) -> Response:
        """Populate request context and log request boundaries."""

        request_id = request.headers.get("X-Request-ID", str(uuid4()))
        set_request_id(request_id)

        logger = get_logger(path=request.url.path, method=request.method)
        started_at = perf_counter()
        logger.info("request_started")

        response = await call_next(request)

        duration_ms = round((perf_counter() - started_at) * 1000, 2)
        response.headers["X-Request-ID"] = request_id
        get_logger(
            path=request.url.path,
            method=request.method,
            status_code=response.status_code,
            duration_ms=duration_ms,
        ).info("request_finished")
        return response
