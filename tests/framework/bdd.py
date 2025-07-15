"""
BDD Test Helpers - أدوات اختبار BDD (Behavior-Driven Development)
"""

import asyncio
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional

import structlog

logger = structlog.get_logger(__name__)


@dataclass
class TestContext:
    """Context for BDD test execution"""

    given_descriptions: List[str] = field(default_factory=list)
    when_descriptions: List[str] = field(default_factory=list)
    then_descriptions: List[str] = field(default_factory=list)
    variables: Dict[str, Any] = field(default_factory=dict)

    def add_given(self, description: str):
        self.given_descriptions.append(description)

    def add_when(self, description: str):
        self.when_descriptions.append(description)

    def add_then(self, description: str):
        self.then_descriptions.append(description)

    def set_variable(self, name: str, value: Any):
        self.variables[name] = value

    def get_variable(self, name: str, default: Any = None) -> Any:
        return self.variables.get(name, default)

    def summary(self) -> str:
        """Get test summary in BDD format"""
        summary_parts = []

        if self.given_descriptions:
            summary_parts.append("Given:\n  " + "\n  ".join(self.given_descriptions))

        if self.when_descriptions:
            summary_parts.append("When:\n  " + "\n  ".join(self.when_descriptions))

        if self.then_descriptions:
            summary_parts.append("Then:\n  " + "\n  ".join(self.then_descriptions))

        return "\n\n".join(summary_parts)


class TestContextBuilder:
    """Builder for test context in BDD style"""

    def __init__(self, description: str):
        self.description = description
        self.context = TestContext()
        self.context.add_given(description)

    def and_given(self, description: str) -> "TestContextBuilder":
        """Add another given condition"""
        self.context.add_given(description)
        return self

    def with_value(self, name: str, value: Any) -> "TestContextBuilder":
        """Set a context variable"""
        self.context.set_variable(name, value)
        return self

    def build(self) -> TestContext:
        """Build the test context"""
        return self.context


class ActionExecutor:
    """Executor for test actions"""

    def __init__(self, action: Callable, context: Optional[TestContext] = None):
        self.action = action
        self.context = context or TestContext()
        self.result = None
        self.exception = None

    async def execute(self, *args, **kwargs) -> "ActionExecutor":
        """Execute the action"""
        try:
            if asyncio.iscoroutinefunction(self.action):
                self.result = await self.action(*args, **kwargs)
            else:
                self.result = self.action(*args, **kwargs)

            logger.debug(f"Action executed successfully: {self.action.__name__}")

        except Exception as e:
            self.exception = e
            logger.error(f"Action failed: {self.action.__name__}", error=str(e))

        return self

    def and_when(self, action: Callable) -> "ActionExecutor":
        """Chain another action"""
        return ActionExecutor(action, self.context)

    def then(self, assertion: Callable) -> None:
        """Execute assertion"""
        if self.exception:
            raise self.exception

        assertion(self.result)

    def then_expect_exception(self, exception_type: type) -> None:
        """Assert that exception was raised"""
        assert (
            self.exception is not None
        ), f"Expected {exception_type.__name__} but no exception was raised"
        assert isinstance(
            self.exception, exception_type
        ), f"Expected {exception_type.__name__} but got {type(self.exception).__name__}"


class BDDTestCase:
    """Base class for BDD-style tests"""

    def __init__(self):
        self.context = TestContext()
        self.steps_executed = []

    def given(
        self, description: str, setup_func: Optional[Callable] = None
    ) -> "BDDTestCase":
        """Define a given condition"""
        self.context.add_given(description)

        if setup_func:
            result = setup_func()
            if result:
                for key, value in result.items():
                    self.context.set_variable(key, value)

        self.steps_executed.append(("given", description))
        return self

    def when(self, description: str, action_func: Callable) -> "BDDTestCase":
        """Define a when action"""
        self.context.add_when(description)

        # Execute action and store result
        if asyncio.iscoroutinefunction(action_func):
            result = asyncio.run(action_func(**self.context.variables))
        else:
            result = action_func(**self.context.variables)

        self.context.set_variable("last_result", result)
        self.steps_executed.append(("when", description))
        return self

    def then(self, description: str, assertion_func: Callable) -> "BDDTestCase":
        """Define a then assertion"""
        self.context.add_then(description)

        # Execute assertion
        assertion_func(
            self.context.get_variable("last_result"), **self.context.variables
        )

        self.steps_executed.append(("then", description))
        return self

    def and_given(
        self, description: str, setup_func: Optional[Callable] = None
    ) -> "BDDTestCase":
        """Add another given condition"""
        return self.given(description, setup_func)

    def and_when(self, description: str, action_func: Callable) -> "BDDTestCase":
        """Add another when action"""
        return self.when(description, action_func)

    def and_then(self, description: str, assertion_func: Callable) -> "BDDTestCase":
        """Add another then assertion"""
        return self.then(description, assertion_func)

    def scenario(self, name: str) -> "BDDTestCase":
        """Start a new scenario"""
        logger.info(f"Starting scenario: {name}")
        self.context = TestContext()
        self.steps_executed = []
        return self

    def report(self) -> str:
        """Generate test report"""
        report_lines = ["BDD Test Report", "=" * 50]
        report_lines.append(self.context.summary())
        report_lines.append("\nExecution Steps:")

        for step_type, description in self.steps_executed:
            report_lines.append(f"✓ {step_type.capitalize()}: {description}")

        return "\n".join(report_lines)


# Decorators for BDD-style tests
def scenario(description: str):
    """Decorator to mark a test scenario"""

    def decorator(func):
        func.__scenario__ = description
        return func

    return decorator


def given(description: str):
    """Decorator for given steps"""

    def decorator(func):
        func.__given__ = description
        return func

    return decorator


def when(description: str):
    """Decorator for when steps"""

    def decorator(func):
        func.__when__ = description
        return func

    return decorator


def then(description: str):
    """Decorator for then steps"""

    def decorator(func):
        func.__then__ = description
        return func

    return decorator
