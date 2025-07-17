"""Common Container - Production Only"""
from src.infrastructure.di.container import DIContainer as Container
from src.infrastructure.di.container import get_container

"""Common Container - Production Only"""

# NO FALLBACKS - PRODUCTION ONLY
# If this fails, dependencies must be installed

__all__ = ["Container", "get_container"]