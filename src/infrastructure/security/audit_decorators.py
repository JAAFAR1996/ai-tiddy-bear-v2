from datetime import datetime
from typing import Callable, Any, Optional, Dict
import asyncio
import functools
import inspect
import logging

from src.infrastructure.security.comprehensive_audit_integration import get_audit_integration
from src.infrastructure.logging_config import get_logger

"""Audit Decorators for Automatic Audit Trail Creation
Provides decorators to automatically add audit logging to functions and methods.
"""

logger = get_logger(__name__, component="security")


def audit_authentication(
    operation_type: str,
    extract_email: Optional[Callable[[Any], str]] = None,
    extract_ip: Optional[Callable[[Any], str]] = None,
):
    """Decorator to automatically audit authentication operations.
    Args: operation_type: Type of operation(login, logout, password_change)
        extract_email: Function to extract email from arguments
        extract_ip: Function to extract IP address from arguments.
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = datetime.utcnow()
            success = False
            error_message = None
            try:
                # Execute the original function
                result = await func(*args, **kwargs)
                success = True
                return result
            except Exception as e:
                error_message = str(e)
                raise
            finally:
                # Extract audit information
                try:
                    email = None
                    ip_address = None
                    if extract_email:
                        email = extract_email(*args, **kwargs)
                    elif args and hasattr(args[0], "email"):
                        email = args[0].email
                    elif "email" in kwargs:
                        email = kwargs["email"]
                    elif args and len(args) > 1 and hasattr(args[1], "email"):
                        email = args[1].email

                    if extract_ip:
                        ip_address = extract_ip(*args, **kwargs)
                    elif "ip_address" in kwargs:
                        ip_address = kwargs["ip_address"]

                    # Log the audit event
                    audit_integration = get_audit_integration()
                    details = {
                        "function": func.__name__,
                        "duration_ms": (
                            datetime.utcnow() - start_time
                        ).total_seconds()
                        * 1000,
                        "error": error_message,
                    }
                    await audit_integration.log_authentication_event(
                        event_type=operation_type,
                        user_email=email or "unknown",
                        success=success,
                        ip_address=ip_address,
                        details=details,
                    )
                except Exception as audit_error:
                    logger.error(
                        f"Failed to log audit event for {func.__name__}: {audit_error}",
                    )

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            # For sync functions, we need to run the audit in the background
            start_time = datetime.utcnow()
            success = False
            error_message = None
            try:
                result = func(*args, **kwargs)
                success = True
                return result
            except Exception as e:
                error_message = str(e)
                raise
            finally:
                # Schedule audit logging asynchronously
                try:
                    email = None
                    ip_address = None
                    if extract_email:
                        email = extract_email(*args, **kwargs)
                    elif args and hasattr(args[0], "email"):
                        email = args[0].email
                    elif "email" in kwargs:
                        email = kwargs["email"]

                    if extract_ip:
                        ip_address = extract_ip(*args, **kwargs)
                    elif "ip_address" in kwargs:
                        ip_address = kwargs["ip_address"]

                    async def log_audit():
                        try:
                            audit_integration = get_audit_integration()
                            details = {
                                "function": func.__name__,
                                "duration_ms": (
                                    datetime.utcnow() - start_time
                                ).total_seconds()
                                * 1000,
                                "error": error_message,
                            }
                            await audit_integration.log_authentication_event(
                                event_type=operation_type,
                                user_email=email or "unknown",
                                success=success,
                                ip_address=ip_address,
                                details=details,
                            )
                        except Exception as audit_error:
                            logger.error(
                                f"Failed to log audit event for {func.__name__}: {audit_error}",
                            )

                    # Try to schedule the audit task
                    try:
                        loop = asyncio.get_event_loop()
                        loop.create_task(log_audit())
                    except RuntimeError:
                        # No event loop, skip audit (dev/test mode)
                        pass
                except Exception as audit_error:
                    logger.error(
                        f"Failed to schedule audit for {func.__name__}: {audit_error}",
                    )

        # Return appropriate wrapper based on function type
        if inspect.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper

    return decorator


def audit_data_access(
    operation: str,
    data_type: str,
    extract_child_id: Optional[Callable[[Any], str]] = None,
    extract_user_id: Optional[Callable[[Any], str]] = None,
    extract_ip: Optional[Callable[[Any], str]] = None,
):
    """Decorator to automatically audit data access operations.
    Args: operation: Type of operation(create, read, update, delete)
        data_type: Type of data being accessed
        extract_child_id: Function to extract child ID from arguments
        extract_user_id: Function to extract user ID from arguments
        extract_ip: Function to extract IP address from arguments.
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = datetime.utcnow()
            success = False
            error_message = None
            try:
                result = await func(*args, **kwargs)
                success = True
                return result
            except Exception as e:
                error_message = str(e)
                raise
            finally:
                # Extract audit information
                try:
                    child_id = None
                    user_id = None
                    ip_address = None

                    if extract_child_id:
                        child_id = extract_child_id(*args, **kwargs)
                    elif "child_id" in kwargs:
                        child_id = kwargs["child_id"]
                    elif args and len(args) > 1:
                        child_id = str(args[1])

                    if extract_user_id:
                        user_id = extract_user_id(*args, **kwargs)
                    elif "user_id" in kwargs:
                        user_id = kwargs["user_id"]
                    elif hasattr(args[0], "current_user"):
                        user_id = getattr(
                            args[0].current_user, "id", "unknown"
                        )

                    if extract_ip:
                        ip_address = extract_ip(*args, **kwargs)
                    elif "ip_address" in kwargs:
                        ip_address = kwargs["ip_address"]

                    # Log the audit event
                    if child_id and user_id:
                        audit_integration = get_audit_integration()
                        details = {
                            "function": func.__name__,
                            "duration_ms": (
                                datetime.utcnow() - start_time
                            ).total_seconds()
                            * 1000,
                            "success": success,
                            "error": error_message,
                        }
                        await audit_integration.log_child_data_operation(
                            operation=operation,
                            child_id=child_id,
                            user_id=user_id,
                            data_type=data_type,
                            ip_address=ip_address,
                            details=details,
                        )
                except Exception as audit_error:
                    logger.error(
                        f"Failed to log data access audit for {func.__name__}: {audit_error}",
                    )

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = datetime.utcnow()
            success = False
            error_message = None
            try:
                result = func(*args, **kwargs)
                success = True
                return result
            except Exception as e:
                error_message = str(e)
                raise
            finally:
                # Schedule audit logging asynchronously
                try:
                    child_id = None
                    user_id = None
                    ip_address = None

                    if extract_child_id:
                        child_id = extract_child_id(*args, **kwargs)
                    elif "child_id" in kwargs:
                        child_id = kwargs["child_id"]

                    if extract_user_id:
                        user_id = extract_user_id(*args, **kwargs)
                    elif "user_id" in kwargs:
                        user_id = kwargs["user_id"]

                    if extract_ip:
                        ip_address = extract_ip(*args, **kwargs)
                    elif "ip_address" in kwargs:
                        ip_address = kwargs["ip_address"]

                    async def log_audit():
                        try:
                            if child_id and user_id:
                                audit_integration = get_audit_integration()
                                details = {
                                    "function": func.__name__,
                                    "duration_ms": (
                                        datetime.utcnow() - start_time
                                    ).total_seconds()
                                    * 1000,
                                    "success": success,
                                    "error": error_message,
                                }
                                await audit_integration.log_child_data_operation(
                                    operation=operation,
                                    child_id=child_id,
                                    user_id=user_id,
                                    data_type=data_type,
                                    ip_address=ip_address,
                                    details=details,
                                )
                        except Exception as audit_error:
                            logger.error(
                                f"Failed to log audit event for {func.__name__}: {audit_error}",
                            )

                    # Try to schedule the audit task
                    try:
                        loop = asyncio.get_event_loop()
                        loop.create_task(log_audit())
                    except RuntimeError:
                        # No event loop, skip audit (dev/test mode)
                        pass
                except Exception as audit_error:
                    logger.error(
                        f"Failed to schedule data access audit for {func.__name__}: {audit_error}",
                    )

        # Return appropriate wrapper based on function type
        if inspect.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper

    return decorator


def audit_security_event(
    event_type: str,
    severity: str = "info",
    extract_user_id: Optional[Callable[[Any], str]] = None,
    extract_ip: Optional[Callable[[Any], str]] = None,
):
    """Decorator to automatically audit security events.
    Args: event_type: Type of security event
        severity: Event severity level
        extract_user_id: Function to extract user ID from arguments
        extract_ip: Function to extract IP address from arguments.
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = datetime.utcnow()
            success = False
            error_message = None
            try:
                result = await func(*args, **kwargs)
                success = True
                return result
            except Exception as e:
                error_message = str(e)
                raise
            finally:
                # Extract audit information
                try:
                    user_id = None
                    ip_address = None

                    if extract_user_id:
                        user_id = extract_user_id(*args, **kwargs)
                    elif "user_id" in kwargs:
                        user_id = kwargs["user_id"]

                    if extract_ip:
                        ip_address = extract_ip(*args, **kwargs)
                    elif "ip_address" in kwargs:
                        ip_address = kwargs["ip_address"]

                    # Log the audit event
                    audit_integration = get_audit_integration()
                    details = {
                        "function": func.__name__,
                        "duration_ms": (
                            datetime.utcnow() - start_time
                        ).total_seconds()
                        * 1000,
                        "success": success,
                        "error": error_message,
                    }
                    description = (
                        f"Security event in {func.__name__}: {event_type}"
                    )
                    if error_message:
                        description += f" (Error: {error_message})"

                    await audit_integration.log_security_event(
                        event_type=event_type,
                        severity=severity if success else "error",
                        description=description,
                        user_id=user_id,
                        ip_address=ip_address,
                        details=details,
                    )
                except Exception as audit_error:
                    logger.error(
                        f"Failed to log security audit for {func.__name__}: {audit_error}",
                    )

        # Return appropriate wrapper based on function type
        if inspect.iscoroutinefunction(func):
            return async_wrapper

        # For sync functions, create a similar wrapper
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = datetime.utcnow()
            success = False
            error_message = None
            try:
                result = func(*args, **kwargs)
                success = True
                return result
            except Exception as e:
                error_message = str(e)
                raise
            finally:
                # Schedule audit logging asynchronously
                async def log_audit():
                    try:
                        user_id = None
                        ip_address = None

                        if extract_user_id:
                            user_id = extract_user_id(*args, **kwargs)
                        elif "user_id" in kwargs:
                            user_id = kwargs["user_id"]

                        if extract_ip:
                            ip_address = extract_ip(*args, **kwargs)
                        elif "ip_address" in kwargs:
                            ip_address = kwargs["ip_address"]

                        audit_integration = get_audit_integration()
                        details = {
                            "function": func.__name__,
                            "duration_ms": (
                                datetime.utcnow() - start_time
                            ).total_seconds()
                            * 1000,
                            "success": success,
                            "error": error_message,
                        }
                        description = (
                            f"Security event in {func.__name__}: {event_type}"
                        )
                        if error_message:
                            description += f" (Error: {error_message})"

                        await audit_integration.log_security_event(
                            event_type=event_type,
                            severity=severity if success else "error",
                            description=description,
                            user_id=user_id,
                            ip_address=ip_address,
                            details=details,
                        )
                    except Exception as audit_error:
                        logger.error(
                            f"Failed to log security audit for {func.__name__}: {audit_error}",
                        )

                # Try to schedule the audit task
                try:
                    loop = asyncio.get_event_loop()
                    loop.create_task(log_audit())
                except RuntimeError:
                    # No event loop, skip audit (dev/test mode)
                    pass

        return sync_wrapper

    return decorator


# Convenience decorators for common operations
def audit_login(
    extract_email: Optional[Callable] = None,
    extract_ip: Optional[Callable] = None,
):
    """Decorator for login operations."""
    return audit_authentication("login", extract_email, extract_ip)


def audit_logout(
    extract_email: Optional[Callable] = None,
    extract_ip: Optional[Callable] = None,
):
    """Decorator for logout operations."""
    return audit_authentication("logout", extract_email, extract_ip)


def audit_child_create(
    extract_child_id: Optional[Callable] = None,
    extract_user_id: Optional[Callable] = None,
):
    """Decorator for child creation operations."""
    return audit_data_access(
        "create",
        "child_profile",
        extract_child_id,
        extract_user_id,
    )


def audit_child_update(
    extract_child_id: Optional[Callable] = None,
    extract_user_id: Optional[Callable] = None,
):
    """Decorator for child update operations."""
    return audit_data_access(
        "update",
        "child_profile",
        extract_child_id,
        extract_user_id,
    )


def audit_child_delete(
    extract_child_id: Optional[Callable] = None,
    extract_user_id: Optional[Callable] = None,
):
    """Decorator for child deletion operations."""
    return audit_data_access(
        "delete",
        "child_profile",
        extract_child_id,
        extract_user_id,
    )
