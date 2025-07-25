"""Centralized exception system for AI Teddy Bear.
All exceptions should be imported from this module.
"""

# Application exceptions
from .application_exceptions import (
    ApplicationException,
    InvalidInputError,
    ResourceNotFoundError,
    ServiceUnavailableError,
    StartupValidationException,
    TimeoutError,
)

# Base exceptions
from .base_exceptions import AITeddyBaseError, ErrorCategory

# Domain exceptions
from .domain_exceptions import (
    AgeRestrictionException,
    ChildSafetyException,
    ConsentException,
    DomainException,
)

# Infrastructure exceptions
from .infrastructure_exceptions import (
    ConfigurationError,
    DatabaseConnectionError,
    ExternalServiceError,
    InfrastructureException,
    RateLimitExceededError,
    SecurityError,
)

__all__ = [
    # Base
    "AITeddyBaseError",
    "ErrorCategory",
    # Domain
    "DomainException",
    "ChildSafetyException",
    "ConsentException",
    "AgeRestrictionException",
    # Application
    "ApplicationException",
    "ServiceUnavailableError",
    "InvalidInputError",
    "TimeoutError",
    "ResourceNotFoundError",
    "StartupValidationException",
    # Infrastructure
    "InfrastructureException",
    "DatabaseConnectionError",
    "ConfigurationError",
    "ExternalServiceError",
    "SecurityError",
    "RateLimitExceededError",
]
