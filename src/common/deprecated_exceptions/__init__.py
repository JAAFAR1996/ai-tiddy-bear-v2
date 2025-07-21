"""Centralized exception system for AI Teddy Bear.
All exceptions should be imported from this module.
"""

# Base exceptions
from .base_exceptions import (
    AITeddyBaseError,
    ErrorCategory,
)

# Domain exceptions
from .domain_exceptions import (
    DomainException,
    ChildSafetyException,
    ConsentException,
    AgeRestrictionException,
)

# Application exceptions  
from .application_exceptions import (
    ApplicationException,
    ServiceUnavailableError,
    InvalidInputError,
    TimeoutError,
    ResourceNotFoundError,
    StartupValidationException,
)

# Infrastructure exceptions
from .infrastructure_exceptions import (
    InfrastructureException,
    DatabaseConnectionError,
    ConfigurationError,
    ExternalServiceError,
    SecurityError,
    RateLimitExceededError,
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
