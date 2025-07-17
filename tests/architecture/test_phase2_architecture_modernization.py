from infrastructure.state.application_state_manager import (
    ApplicationStateManager,
    StateScope,
    create_state_manager,
)
from infrastructure.microservices.service_orchestrator import LoadBalancer
from infrastructure.security.plugin_architecture import (
    PluginType,
    create_plugin_manager,
    create_plugin_manifest,
)
from infrastructure.messaging.event_driven_architecture import (
    EventType,
    Command,
    Query,
    InMemoryCommandBus,
    InMemoryQueryBus,
    create_event,
    create_command,
    create_query,
)
from datetime import datetime, timezone, timedelta
import uuid
import time
import tempfile
import asyncio
import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent
while src_path.name != "backend" and src_path.parent != src_path:
    src_path = src_path.parent
src_path = src_path / "src"

if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

"""
Phase 2: Architecture Modernization Tests
Comprehensive test suite for dependency injection, event-driven architecture, plugin system, microservices, and state management
"""


try:
    import pytest
except ImportError:
    try:
        from common.mock_pytest import pytest
    except ImportError:
        pass

    # Mock pytest when not available
    class MockPytest:
        def fixture(self, *args, **kwargs):
            def decorator(func):
                return func

            return decorator

        def mark(self):
            class MockMark:
                def parametrize(self, *args, **kwargs):
                    def decorator(func):
                        return func

                    return decorator

                def asyncio(self, func):
                    return func

                def slow(self, func):
                    return func

                def skip(self, reason=""):
                    def decorator(func):
                        return func

                    return decorator

            return MockMark()

        def raises(self, exception):
            class MockRaises:
                def __enter__(self):
                    return self

                def __exit__(self, *args):
                    return False

            return MockRaises()

        def skip(self, reason=""):
            def decorator(func):
                return func

            return decorator

    pytest = MockPytest()


class TestDependencyInjection:
    """Test dependency injection system"""

    @pytest.mark.asyncio
    async def test_container_creation(self):
        """Test container creation"""
        container = create_container("test_container")
        assert container.name == "test_container"
        assert container.state.value == "initializing"

    @pytest.mark.asyncio
    async def test_dependency_registration(self):
        """Test dependency registration"""
        container = create_container()

        # Mock service classes
        class MockService:
            def __init__(self):
                self.initialized = False

            async def initialize(self):
                self.initialized = True

        class MockInterface:
            pass

        # Register dependency
        container.register_singleton(MockInterface, MockService)

        # Check registration
        assert "MockInterface" in container.registrations
        metadata = container.registrations["MockInterface"]
        assert metadata.scope == LifecycleScope.SINGLETON
        assert metadata.implementation == MockService

    @pytest.mark.asyncio
    async def test_dependency_resolution(self):
        """Test dependency resolution"""
        container = create_container()

        class MockService:
            def __init__(self):
                self.name = "test_service"

        class MockInterface:
            pass

        # Register and resolve
        container.register_singleton(MockInterface, MockService)
        await container.initialize()

        instance = await container.get(MockInterface)
        assert isinstance(instance, MockService)
        assert instance.name == "test_service"

    @pytest.mark.asyncio
    async def test_circular_dependency_detection(self):
        """Test circular dependency detection"""
        container = create_container()

        class ServiceA:
            pass

        class ServiceB:
            pass

        # Create circular dependency
        container.register(ServiceA, ServiceA, dependencies=["ServiceB"])
        container.register(ServiceB, ServiceB, dependencies=["ServiceA"])

        # Should detect circular dependency
        with pytest.raises(CircularDependencyError):
            await container.initialize()

    @pytest.mark.asyncio
    async def test_dependency_not_found(self):
        """Test dependency not found error"""
        container = create_container()
        await container.initialize()

        class NonExistentService:
            pass

        with pytest.raises(DependencyNotFoundError):
            await container.get(NonExistentService)

    @pytest.mark.asyncio
    async def test_lifecycle_scopes(self):
        """Test different lifecycle scopes"""
        container = create_container()

        class MockService:
            def __init__(self):
                self.id = str(uuid.uuid4())

        # Register with different scopes
        container.register_singleton(MockService, MockService)
        container.register_request_scoped(MockService, MockService)
        container.register_transient(MockService, MockService)

        await container.initialize()

        # Test singleton (same instance)
        instance1 = await container.get(MockService)
        instance2 = await container.get(MockService)
        assert instance1.id == instance2.id

    @pytest.mark.asyncio
    async def test_container_shutdown(self):
        """Test container shutdown"""
        container = create_container()

        class MockService:
            def __init__(self):
                self.cleaned_up = False

            async def cleanup(self):
                self.cleaned_up = True

        container.register_singleton(MockService, MockService)
        await container.initialize()

        instance = await container.get(MockService)
        await container.shutdown()

        assert instance.cleaned_up
        assert container.state.value == "shutdown"


class TestEventDrivenArchitecture:
    """Test event-driven architecture"""

    @pytest.mark.asyncio
    async def test_event_creation(self):
        """Test event creation"""
        event_data = {"message": "test event"}
        event = create_event(EventType.DOMAIN, event_data, user_id="test_user")

        assert event.metadata.event_type == EventType.DOMAIN
        assert event.data == event_data
        assert event.metadata.user_id == "test_user"
        assert event.metadata.event_id is not None

    @pytest.mark.asyncio
    async def test_command_creation(self):
        """Test command creation"""
        command_data = {"action": "test_action"}
        command = create_command(command_data, user_id="test_user")

        assert command.data == command_data
        assert command.user_id == "test_user"
        assert command.command_id is not None

    @pytest.mark.asyncio
    async def test_query_creation(self):
        """Test query creation"""
        query_params = {"filter": "test_filter"}
        query = create_query(query_params, user_id="test_user")

        assert query.parameters == query_params
        assert query.user_id == "test_user"
        assert query.query_id is not None

    @pytest.mark.asyncio
    async def test_in_memory_command_bus(self):
        """Test in-memory command bus"""
        command_bus = InMemoryCommandBus()

        class TestCommand(Command):
            pass

        class TestHandler:
            async def handle(self, command: TestCommand):
                return f"Handled: {command.data.get('message')}"

        # Register handler
        await command_bus.register_handler(TestCommand, TestHandler())

        # Send command
        command = TestCommand(data={"message": "test"})
        result = await command_bus.send(command)

        assert result == "Handled: test"

    @pytest.mark.asyncio
    async def test_in_memory_query_bus(self):
        """Test in-memory query bus"""
        query_bus = InMemoryQueryBus()

        class TestQuery(Query):
            pass

        class TestHandler:
            async def handle(self, query: TestQuery):
                return f"Query result: {query.parameters.get('filter')}"

        # Register handler
        await query_bus.register_handler(TestQuery, TestHandler())

        # Ask query
        query = TestQuery(parameters={"filter": "test_filter"})
        result = await query_bus.ask(query)

        assert result == "Query result: test_filter"

    @pytest.mark.asyncio
    async def test_query_bus_caching(self):
        """Test query bus caching"""
        query_bus = InMemoryQueryBus()

        class TestQuery(Query):
            pass

        call_count = 0

        class TestHandler:
            async def handle(self, query: TestQuery):
                nonlocal call_count
                call_count += 1
                return f"Result {call_count}"

        # Register handler
        await query_bus.register_handler(TestQuery, TestHandler())

        # First query (should call handler)
        query1 = TestQuery(parameters={"id": "1"})
        result1 = await query_bus.ask(query1)
        assert result1 == "Result 1"
        assert call_count == 1

        # Second query with same parameters (should use cache)
        query2 = TestQuery(parameters={"id": "1"})
        result2 = await query_bus.ask(query2)
        assert result2 == "Result 1"
        assert call_count == 1  # Should not increment


class TestPluginArchitecture:
    """Test plugin architecture"""

    @pytest.mark.asyncio
    async def test_plugin_manager_creation(self):
        """Test plugin manager creation"""
        with tempfile.TemporaryDirectory() as temp_dir:
            plugin_manager = create_plugin_manager(temp_dir)
            assert plugin_manager.plugins_directory == Path(temp_dir)

    @pytest.mark.asyncio
    async def test_plugin_manifest_creation(self):
        """Test plugin manifest creation"""
        manifest = create_plugin_manifest(
            name="test_plugin",
            version="1.0.0",
            description="Test plugin",
            author="Test Author",
            plugin_type=PluginType.AI_SERVICE,
            entry_point="test_plugin",
        )

        assert manifest.name == "test_plugin"
        assert manifest.version == "1.0.0"
        assert manifest.plugin_type == PluginType.AI_SERVICE

    @pytest.mark.asyncio
    async def test_plugin_manifest_validation(self):
        """Test plugin manifest validation"""
        # Test invalid name
        with pytest.raises(ValueError):
            create_plugin_manifest(
                name="invalid name!",
                version="1.0.0",
                description="Test",
                author="Test",
                plugin_type=PluginType.AI_SERVICE,
                entry_point="test",
            )

        # Test invalid version
        with pytest.raises(ValueError):
            create_plugin_manifest(
                name="test_plugin",
                version="invalid",
                description="Test",
                author="Test",
                plugin_type=PluginType.AI_SERVICE,
                entry_point="test",
            )

    @pytest.mark.asyncio
    async def test_plugin_discovery(self):
        """Test plugin discovery"""
        # Create test plugin directory
        plugin_dir = Path("temp_plugin_dir")
        plugin_dir.mkdir(exist_ok=True)

        # Create manifest
        manifest = create_plugin_manifest(
            name="test_plugin",
            version="1.0.0",
            description="Test plugin",
            author="Test Author",
            plugin_type=PluginType.AI_SERVICE,
            entry_point="test_plugin",
        )

        manifest_path = plugin_dir / "manifest.json"
        with open(manifest_path, "w") as f:
            f.write(manifest.json())

        # Discover plugins
        plugin_manager = create_plugin_manager(plugin_dir)
        plugins = await plugin_manager.discover_plugins()
        assert len(plugins) == 1
        assert plugins[0].name == "test_plugin"

        # Clean up
        import shutil

        shutil.rmtree(plugin_dir)


class TestMicroservicesOrchestrator:
    """Test microservices orchestrator"""

    @pytest.mark.asyncio
    async def test_service_instance_creation(self):
        """Test service instance creation"""
        instance = create_service_instance(
            id="test-instance-1", name="test-service", host="localhost", port=8080
        )

        assert instance.id == "test-instance-1"
        assert instance.name == "test-service"
        assert instance.host == "localhost"
        assert instance.port == 8080
        assert instance.status == ServiceStatus.UNKNOWN

    @pytest.mark.asyncio
    async def test_service_definition_creation(self):
        """Test service definition creation"""
        instances = [
            create_service_instance("1", "test", "localhost", 8080),
            create_service_instance("2", "test", "localhost", 8081),
        ]

        service = create_service_definition(
            name="test-service",
            version="1.0.0",
            instances=instances,
            load_balancing_strategy=LoadBalancingStrategy.ROUND_ROBIN,
        )

        assert service.name == "test-service"
        assert service.version == "1.0.0"
        assert len(service.instances) == 2
        assert service.load_balancing_strategy == LoadBalancingStrategy.ROUND_ROBIN

    @pytest.mark.asyncio
    async def test_load_balancer_round_robin(self):
        """Test load balancer round robin strategy"""
        from infrastructure.microservices.service_orchestrator import LoadBalancer

        load_balancer = LoadBalancer()

        # Mock service instances
        instances = [
            ServiceInstance("1", "test", "host1", 8080),
            ServiceInstance("2", "test", "host2", 8081),
            ServiceInstance("3", "test", "host3", 8082),
        ]

        # Test round robin selection
        selected1 = load_balancer._round_robin("test", instances)
        selected2 = load_balancer._round_robin("test", instances)
        selected3 = load_balancer._round_robin("test", instances)
        selected4 = load_balancer._round_robin("test", instances)

        # Should cycle through instances
        assert selected1 != selected2
        assert selected2 != selected3
        assert selected3 != selected4
        assert selected4 == selected1  # Back to first

    @pytest.mark.asyncio
    async def test_load_balancer_random(self):
        """Test load balancer random strategy"""
        from infrastructure.microservices.service_orchestrator import LoadBalancer

        load_balancer = LoadBalancer()

        instances = [
            ServiceInstance("1", "test", "host1", 8080),
            ServiceInstance("2", "test", "host2", 8081),
        ]

        # Test random selection (may not be deterministic)
        selected = load_balancer._random(instances)
        assert selected in instances


class TestApplicationStateManager:
    """Test application state manager"""

    @pytest.mark.asyncio
    async def test_state_manager_creation(self):
        """Test state manager creation"""
        state_manager = create_state_manager(use_redis=False)
        assert isinstance(state_manager, ApplicationStateManager)

    @pytest.mark.asyncio
    async def test_state_operations(self):
        """Test basic state operations"""
        state_manager = create_state_manager()

        # Set state
        await state_manager.set_state("test_key", "test_value", StateScope.REQUEST)

        # Get state
        value = await state_manager.get_state("test_key", StateScope.REQUEST)
        assert value == "test_value"

        # Check existence
        exists = await state_manager.has_state("test_key", StateScope.REQUEST)
        assert exists is True

        # Delete state
        await state_manager.delete_state("test_key", StateScope.REQUEST)

        # Check deletion
        exists = await state_manager.has_state("test_key", StateScope.REQUEST)
        assert exists is False

    @pytest.mark.asyncio
    async def test_request_scope_context(self):
        """Test request scope context manager"""
        state_manager = create_state_manager()

        async with state_manager.async_request_context("test_request"):
            # Set state in request scope
            await state_manager.set_state(
                "request_key", "request_value", StateScope.REQUEST
            )

            # Verify state exists
            value = await state_manager.get_state("request_key", StateScope.REQUEST)
            assert value == "request_value"

        # After context exit, request scope should be cleared
        value = await state_manager.get_state("request_key", StateScope.REQUEST)
        assert value is None

    @pytest.mark.asyncio
    async def test_session_scope_context(self):
        """Test session scope context manager"""
        state_manager = create_state_manager()

        with state_manager.session_context("test_session"):
            # Set state in session scope
            await state_manager.set_state(
                "session_key", "session_value", StateScope.SESSION
            )

            # Verify state exists
            value = await state_manager.get_state("session_key", StateScope.SESSION)
            assert value == "session_value"

    @pytest.mark.asyncio
    async def test_state_expiration(self):
        """Test state expiration"""
        state_manager = create_state_manager()

        # Set state with expiration
        expires_at = datetime.now(timezone.utc).replace(microsecond=0) + timedelta(
            seconds=1
        )
        await state_manager.set_state(
            "expiring_key", "expiring_value", StateScope.REQUEST, expires_at=expires_at
        )

        # State should exist initially
        value = await state_manager.get_state("expiring_key", StateScope.REQUEST)
        assert value == "expiring_value"

        # Wait for expiration
        await asyncio.sleep(1.1)

        # State should be expired
        value = await state_manager.get_state("expiring_key", StateScope.REQUEST)
        assert value is None


class TestIntegration:
    """Integration tests for Phase 2 components"""

    @pytest.mark.asyncio
    async def test_di_with_event_bus_integration(self):
        """Test DI container with event bus integration"""
        container = create_container()

        # Mock event bus
        class MockEventBus:
            def __init__(self):
                self.published_events = []

            async def publish(self, event):
                self.published_events.append(event)

        # Register event bus
        container.register_singleton(MockEventBus, MockEventBus)
        await container.initialize()

        # Get event bus and publish event
        event_bus = await container.get(MockEventBus)
        event = create_event(EventType.DOMAIN, {"test": "data"})
        await event_bus.publish(event)

        assert len(event_bus.published_events) == 1
        assert event_bus.published_events[0] == event

    @pytest.mark.asyncio
    async def test_plugin_with_state_integration(self):
        """Test plugin system with state management integration"""
        state_manager = create_state_manager()

        # Create plugin manifest
        manifest = create_plugin_manifest(
            name="state_plugin",
            version="1.0.0",
            description="State management plugin",
            author="Test",
            plugin_type=PluginType.CUSTOM,
            entry_point="state_plugin",
        )

        # Store plugin state
        await state_manager.set_state(
            f"plugin:{manifest.name}", manifest.dict(), StateScope.APPLICATION
        )

        # Retrieve plugin state
        plugin_state = await state_manager.get_state(
            f"plugin:{manifest.name}", StateScope.APPLICATION
        )

        assert plugin_state["name"] == manifest.name
        assert plugin_state["version"] == manifest.version

    @pytest.mark.asyncio
    async def test_microservices_with_di_integration(self):
        """Test microservices with DI integration"""
        container = create_container()

        # Mock service orchestrator
        class MockOrchestrator:
            def __init__(self):
                self.services = {}

            async def register_service(self, service):
                self.services[service.name] = service

        # Register orchestrator
        container.register_singleton(MockOrchestrator, MockOrchestrator)
        await container.initialize()

        # Get orchestrator and register service
        orchestrator = await container.get(MockOrchestrator)
        service = create_service_definition(
            "test-service",
            "1.0.0",
            [create_service_instance("1", "test", "localhost", 8080)],
        )

        await orchestrator.register_service(service)
        assert "test-service" in orchestrator.services


class TestPerformance:
    """Performance tests for Phase 2 components"""

    @pytest.mark.asyncio
    async def test_di_performance(self):
        """Test DI container performance"""
        container = create_container()

        class FastService:
            def __init__(self):
                self.id = str(uuid.uuid4())

        # Register many services
        for i in range(100):
            container.register_singleton(FastService, FastService)

        start_time = time.time()
        await container.initialize()
        init_time = time.time() - start_time

        # Should initialize quickly
        assert init_time < 1.0

        # Test resolution performance
        start_time = time.time()
        for _ in range(1000):
            await container.get(FastService)
        resolve_time = time.time() - start_time

        # Should resolve quickly
        assert resolve_time < 1.0

    @pytest.mark.asyncio
    async def test_state_manager_performance(self):
        """Test state manager performance"""
        state_manager = create_state_manager()

        # Test bulk operations
        start_time = time.time()
        for i in range(1000):
            await state_manager.set_state(f"key_{i}", f"value_{i}", StateScope.REQUEST)

        for i in range(1000):
            value = await state_manager.get_state(f"key_{i}", StateScope.REQUEST)
            assert value == f"value_{i}"

        operation_time = time.time() - start_time

        # Should handle bulk operations quickly
        assert operation_time < 5.0

    @pytest.mark.asyncio
    async def test_event_bus_performance(self):
        """Test event bus performance"""
        command_bus = InMemoryCommandBus()
        query_bus = InMemoryQueryBus()

        class TestCommand(Command):
            pass

        class TestQuery(Query):
            pass

        class FastHandler:
            async def handle(self, item):
                return "processed"

        # Register handlers
        await command_bus.register_handler(TestCommand, FastHandler())
        await query_bus.register_handler(TestQuery, FastHandler())

        # Test command performance
        start_time = time.time()
        for _ in range(1000):
            command = TestCommand(data={"test": "data"})
            await command_bus.send(command)
        command_time = time.time() - start_time

        # Test query performance
        start_time = time.time()
        for _ in range(1000):
            query = TestQuery(parameters={"test": "data"})
            await query_bus.ask(query)
        query_time = time.time() - start_time

        # Should process quickly
        assert command_time < 2.0
        assert query_time < 2.0


class TestSecurity:
    """Security tests for Phase 2 components"""

    @pytest.mark.asyncio
    async def test_plugin_sandboxing(self):
        """Test plugin sandboxing security"""
        from infrastructure.security.plugin_architecture import (
            PluginSandbox,
            SecurityError,
        )

        # Test dangerous operations
        sandbox = PluginSandbox("test_plugin", [])

        # Test dangerous import
        with pytest.raises(SecurityError):
            sandbox.secure_import("os")

        # Test dangerous code execution
        dangerous_code = "import os; os.system('rm -rf /')"
        with pytest.raises(SecurityError):
            sandbox.secure_exec(dangerous_code, {}, {})

    @pytest.mark.asyncio
    async def test_state_isolation(self):
        """Test state isolation between scopes"""
        state_manager = create_state_manager()

        # Set state in different scopes
        await state_manager.set_state("key", "request_value", StateScope.REQUEST)
        await state_manager.set_state("key", "session_value", StateScope.SESSION)
        await state_manager.set_state("key", "app_value", StateScope.APPLICATION)

        # Verify isolation
        request_value = await state_manager.get_state("key", StateScope.REQUEST)
        session_value = await state_manager.get_state("key", StateScope.SESSION)
        app_value = await state_manager.get_state("key", StateScope.APPLICATION)

        assert request_value == "request_value"
        assert session_value == "session_value"
        assert app_value == "app_value"
        assert request_value != session_value != app_value


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
