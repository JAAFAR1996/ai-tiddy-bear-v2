"""
Test Data Builders and Mock Factory - بناة بيانات الاختبار ومصنع المحاكيات
"""

import random
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Type, TypeVar
from unittest.mock import AsyncMock, Mock

from faker import Faker

from src.domain.entities.child import Child
from src.domain.entities.parent_profile.entities import Parent
from src.domain.value_objects import ChildAge, ParentId

T = TypeVar("T")

faker = Faker()


@dataclass
class TestChild:
    """Test data class for Child entity"""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = field(default_factory=faker.first_name)
    age: int = field(default_factory=lambda: random.randint(3, 12))
    parent_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    preferences: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)

    def to_domain(self) -> Child:
        """Convert to domain entity"""
        return Child(
            id=self.id,
            name=self.name,
            age=ChildAge(self.age),
            parent_id=ParentId(self.parent_id),
            preferences=self.preferences,
            created_at=self.created_at,
        )


@dataclass
class TestParent:
    """Test data class for Parent entity"""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = field(default_factory=faker.name)
    email: str = field(default_factory=faker.email)
    phone: str = field(default_factory=faker.phone_number)
    children_ids: List[str] = field(default_factory=list)
    settings: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)

    def to_domain(self) -> Parent:
        """Convert to domain entity"""
        return Parent(
            id=ParentId(self.id),
            name=self.name,
            email=self.email,
            phone=self.phone,
            children_ids=self.children_ids,
            settings=self.settings,
            created_at=self.created_at,
        )


class TestDataBuilder:
    """Builder for creating test data"""

    def __init__(self):
        self.faker = Faker()
        self._created_entities = {
            "children": [],
            "parents": [],
            "devices": [],
            "interactions": [],
        }

    def create_child(
        self,
        name: Optional[str] = None,
        age: Optional[int] = None,
        parent_id: Optional[str] = None,
        **kwargs,
    ) -> TestChild:
        """Create a test child"""
        child = TestChild(
            name=name or self.faker.first_name(),
            age=age or random.randint(3, 12),
            parent_id=parent_id or str(uuid.uuid4()),
            **kwargs,
        )
        self._created_entities["children"].append(child)
        return child

    def create_parent(
        self,
        name: Optional[str] = None,
        email: Optional[str] = None,
        children_count: int = 0,
        **kwargs,
    ) -> TestParent:
        """Create a test parent"""
        parent = TestParent(
            name=name or self.faker.name(),
            email=email or self.faker.email(),
            **kwargs,
        )

        # Create children if requested
        for _ in range(children_count):
            child = self.create_child(parent_id=parent.id)
            parent.children_ids.append(child.id)

        self._created_entities["parents"].append(parent)
        return parent

    def create_family(
        self, children_count: int = 2, parent_count: int = 2
    ) -> Dict[str, Any]:
        """Create a complete family unit"""
        parents = [self.create_parent() for _ in range(parent_count)]
        children = []

        for i in range(children_count):
            parent = parents[i % len(parents)]
            child = self.create_child(parent_id=parent.id)
            parent.children_ids.append(child.id)
            children.append(child)

        return {"parents": parents, "children": children}

    def create_interaction(
        self,
        child_id: Optional[str] = None,
        message: Optional[str] = None,
        response: Optional[str] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """Create a test interaction"""
        interaction = {
            "id": str(uuid.uuid4()),
            "child_id": child_id or str(uuid.uuid4()),
            "message": message or self.faker.sentence(),
            "response": response or self.faker.sentence(),
            "timestamp": datetime.utcnow(),
            "duration_seconds": random.uniform(1, 10),
            "safety_check_passed": True,
            **kwargs,
        }
        self._created_entities["interactions"].append(interaction)
        return interaction

    def create_device(
        self,
        device_id: Optional[str] = None,
        child_id: Optional[str] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """Create a test device"""
        device = {
            "id": device_id or f"ESP32_{uuid.uuid4().hex[:8]}",
            "child_id": child_id,
            "firmware_version": f"v{random.randint(1, 5)}.{random.randint(0, 9)}.{random.randint(0, 99)}",
            "last_seen": datetime.utcnow(),
            "battery_level": random.randint(20, 100),
            "is_online": True,
            **kwargs,
        }
        self._created_entities["devices"].append(device)
        return device

    def create_batch(
        self, entity_type: str, count: int, **kwargs
    ) -> List[Any]:
        """Create multiple entities of the same type"""
        creators = {
            "child": self.create_child,
            "parent": self.create_parent,
            "interaction": self.create_interaction,
            "device": self.create_device,
        }

        creator = creators.get(entity_type)
        if not creator:
            raise ValueError(f"Unknown entity type: {entity_type}")

        return [creator(**kwargs) for _ in range(count)]

    def cleanup(self):
        """Clean up all created entities"""
        self._created_entities = {
            "children": [],
            "parents": [],
            "devices": [],
            "interactions": [],
        }


class MockFactory:
    """Factory for creating mock objects"""

    @staticmethod
    def create_mock(
        spec: Optional[Type[T]] = None, async_mock: bool = False, **kwargs
    ) -> T:
        """Create a mock object"""
        mock_class = AsyncMock if async_mock else Mock
        return mock_class(spec=spec, **kwargs)

    @staticmethod
    def create_ai_service_mock(
        default_response: str = "This is a safe AI response for testing",
    ) -> AsyncMock:
        """Create a mock AI service"""
        mock = AsyncMock()
        mock.generate_response.return_value = default_response
        mock.check_content_safety.return_value = {
            "is_safe": True,
            "confidence": 0.95,
        }
        mock.get_model_info.return_value = {
            "model": "gpt-4",
            "version": "2024-01",
            "max_tokens": 4096,
        }
        return mock

    @staticmethod
    def create_database_mock() -> AsyncMock:
        """Create a mock database session"""
        mock = AsyncMock()
        mock.commit = AsyncMock()
        mock.rollback = AsyncMock()
        mock.close = AsyncMock()
        mock.execute = AsyncMock()
        mock.scalar = AsyncMock()
        mock.scalars = AsyncMock()

        # Context manager support
        mock.__aenter__ = AsyncMock(return_value=mock)
        mock.__aexit__ = AsyncMock(return_value=None)

        return mock

    @staticmethod
    def create_cache_mock() -> AsyncMock:
        """Create a mock cache service"""
        mock = AsyncMock()
        cache_data = {}

        async def get(key: str) -> Optional[Any]:
            return cache_data.get(key)

        async def set(key: str, value: Any, ttl: Optional[int] = None) -> None:
            cache_data[key] = value

        async def delete(key: str) -> None:
            cache_data.pop(key, None)

        mock.get = get
        mock.set = set
        mock.delete = delete
        mock.clear = AsyncMock(side_effect=cache_data.clear)

        return mock

    @staticmethod
    def create_notification_service_mock() -> AsyncMock:
        """Create a mock notification service"""
        mock = AsyncMock()
        notifications = []

        async def send_notification(notification: Dict[str, Any]) -> str:
            notification_id = str(uuid.uuid4())
            notifications.append({**notification, "id": notification_id})
            return notification_id

        mock.send_notification = send_notification
        mock.get_notifications = AsyncMock(return_value=notifications)
        mock.mark_as_read = AsyncMock()

        return mock

    @staticmethod
    def create_websocket_mock() -> Mock:
        """Create a mock WebSocket connection"""
        mock = Mock()
        mock.send_json = AsyncMock()
        mock.receive_json = AsyncMock()
        mock.close = AsyncMock()
        mock.accept = AsyncMock()

        return mock
