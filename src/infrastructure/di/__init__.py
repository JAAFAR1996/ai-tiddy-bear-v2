"""Dependency Injection exports."""
from .application_container import ApplicationContainer
from .container import container

Container = ApplicationContainer  # Backward compatibility

__all__ = ['ApplicationContainer', 'Container', 'container']
