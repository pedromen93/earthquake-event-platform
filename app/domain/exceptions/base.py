"""Base domain and application exceptions."""


class ApplicationError(Exception):
    """Base exception for controlled application errors."""


class DomainError(ApplicationError):
    """Raised when a domain rule is violated."""


class InfrastructureError(ApplicationError):
    """Raised when an infrastructure dependency fails in a controlled way."""


class ResourceNotFoundError(ApplicationError):
    """Raised when a requested resource cannot be found."""
