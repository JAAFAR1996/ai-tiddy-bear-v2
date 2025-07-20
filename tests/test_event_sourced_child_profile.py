"""Test event sourced child profile functionality"""

import asyncio
import sys
from pathlib import Path
from uuid import uuid4

from domain.entities.child_profile import ChildProfile
from domain.events.child_profile_updated import ChildProfileUpdated
from domain.repositories.event_store import InMemoryEventStore
from infrastructure.repositories.event_sourced_child_repository import (
    EventSourcedChildRepository,
)

# Add src to path
src_path = Path(__file__).parent
while src_path.name != "backend" and src_path.parent != src_path:
    src_path = src_path.parent
src_path = src_path / "src"

if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

# Import after path setup

try:
    import pytest
except ImportError:
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

        def main(self, args):
            return 0

    pytest = MockPytest()


@pytest.fixture
def in_memory_event_store():
    return InMemoryEventStore()


@pytest.fixture
def event_sourced_child_repository(in_memory_event_store):
    return EventSourcedChildRepository(in_memory_event_store)


@pytest.fixture
def sample_child_profile():
    return ChildProfile.create_new("Test Child", 5, {"toy": "bear"})


class TestChildProfileEventSourcing:
    def test_child_profile_update_dispatches_event(self):
        async def _test():
            child = ChildProfile.create_new("Test Child", 5, {"toy": "bear"})
            # Clear any initial events (like ChildRegistered) from creation
            child.get_uncommitted_events()

            # Now update the profile
            child.update_profile(name="Updated Child")
            events = child.get_uncommitted_events()

            assert len(events) == 1  # Only the ChildProfileUpdated event
            assert isinstance(events[0], ChildProfileUpdated)
            assert events[0].name == "Updated Child"

        asyncio.run(_test())

    def test_child_profile_reconstructs_from_events(self):
        async def _test():
            child_id = uuid4()
            initial_profile = ChildProfile.create_new("Initial", 5, {})
            initial_profile.id = child_id  # Set ID for consistent event stream

            # Simulate events being loaded from an event store
            events = [
                ChildProfileUpdated.create(child_id=child_id, name="First Update"),
                ChildProfileUpdated.create(child_id=child_id, age=4),
                ChildProfileUpdated.create(
                    child_id=child_id, preferences={"color": "blue"}
                ),
            ]

            reconstructed_child = ChildProfile.create_new("", 5, {})
            reconstructed_child.id = child_id
            for event in events:
                reconstructed_child.apply(event)

            assert reconstructed_child.name == "First Update"
            assert reconstructed_child.age == 4
            assert reconstructed_child.preferences == {"color": "blue"}

        asyncio.run(_test())


class TestEventSourcedChildRepository:
    def test_save_and_load_child_profile(
        self, event_sourced_child_repository, sample_child_profile
    ):
        async def _test():
            # Create and save a child profile, which dispatches a ChildRegistered event (implicitly from create_new)
            # and then an update event
            sample_child_profile.update_profile(name="New Name", age=6)
            await event_sourced_child_repository.save(sample_child_profile)

            # Load the child profile from the repository
            loaded_child = await event_sourced_child_repository.get_by_id(
                sample_child_profile.id
            )

            assert loaded_child is not None
            assert loaded_child.id == sample_child_profile.id
            assert loaded_child.name == "New Name"
            assert loaded_child.age == 6

        asyncio.run(_test())

    def test_load_non_existent_child(self, event_sourced_child_repository):
        async def _test():
            non_existent_id = uuid4()
            loaded_child = await event_sourced_child_repository.get_by_id(
                non_existent_id
            )
            assert loaded_child is None

        asyncio.run(_test())

    def test_get_all_not_implemented(self, event_sourced_child_repository):
        async def _test():
            with pytest.raises(NotImplementedError):
                await event_sourced_child_repository.get_all()

        asyncio.run(_test())

    def test_delete_not_implemented(self, event_sourced_child_repository):
        async def _test():
            with pytest.raises(NotImplementedError):
                await event_sourced_child_repository.delete(uuid4())

        asyncio.run(_test())
