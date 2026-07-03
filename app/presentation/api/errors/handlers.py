"""Centralized exception handlers for FastAPI."""

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.domain.exceptions.base import (
    ApplicationError,
    InfrastructureError,
    ResourceNotFoundError,
)
from app.infrastructure.logging.logger import get_logger
from app.infrastructure.logging.request_context import get_request_id


def register_exception_handlers(app: FastAPI) -> None:
    """Register all application-level exception handlers."""

    app.add_exception_handler(ApplicationError, application_error_handler)
    app.add_exception_handler(RequestValidationError, validation_error_handler)


async def application_error_handler(_: Request, exc: ApplicationError) -> JSONResponse:
    """Handle controlled application exceptions."""

    request_id = get_request_id()

    if isinstance(exc, ResourceNotFoundError):
        status_code = status.HTTP_404_NOT_FOUND
        error_code = "resource_not_found"
    elif isinstance(exc, InfrastructureError):
        status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        error_code = "infrastructure_error"
    else:
        status_code = status.HTTP_400_BAD_REQUEST
        error_code = "application_error"

    get_logger(error_code=error_code).warning(str(exc))
    return JSONResponse(
        status_code=status_code,
        content={
            "detail": str(exc),
            "error_code": error_code,
            "request_id": request_id,
        },
    )


async def validation_error_handler(_: Request, exc: RequestValidationError) -> JSONResponse:
    """Handle FastAPI request validation errors with a consistent schema."""

    request_id = get_request_id()
    get_logger(error_code="validation_error", errors=exc.errors()).warning("request_validation_failed")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": "Request validation failed.",
            "error_code": "validation_error",
            "request_id": request_id,
            "errors": exc.errors(),
        },
    )
