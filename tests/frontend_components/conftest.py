from unittest.mock import AsyncMock, Mock

import pytest

# Test configuration
TEST_CONFIG = {
    "base_url": "http://localhost:3000",
    "api_url": "http://localhost:8000/api/v1",
    "test_timeout": 30,
    "test_user": {
        "email": "test@example.com",
        "password": "Test123!@#",
        "role": "parent",
    },
}


@pytest.fixture
def auth_service():
    """Mock auth service"""
    service = Mock()
    service.login = AsyncMock()
    service.logout = AsyncMock()
    service.refresh_token = AsyncMock()
    service.is_authenticated = AsyncMock()
    return service


@pytest.fixture
def dashboard_service():
    """Mock dashboard service"""
    service = Mock()
    service.get_stats = AsyncMock()
    service.get_conversations = AsyncMock()
    service.get_emotion_data = AsyncMock()
    return service


@pytest.fixture
def conversation_service():
    """Mock conversation service"""
    service = Mock()
    service.get_conversations = AsyncMock()
    service.get_conversation_details = AsyncMock()
    service.start_conversation = AsyncMock()
    service.end_conversation = AsyncMock()
    service.search_conversations = AsyncMock()
    return service


@pytest.fixture
def child_service():
    """Mock child service"""
    service = Mock()
    service.get_children = AsyncMock()
    service.get_child = AsyncMock()
    service.create_child = AsyncMock()
    service.update_child = AsyncMock()
    service.delete_child = AsyncMock()
    service.get_child_statistics = AsyncMock()
    return service


@pytest.fixture
def report_service():
    """Mock report service"""
    service = Mock()
    service.generate_report = AsyncMock()
    service.get_reports = AsyncMock()
    service.export_report = AsyncMock()
    return service


@pytest.fixture
def websocket_service():
    """Mock WebSocket service"""
    service = Mock()
    service.connect = AsyncMock()
    service.disconnect = AsyncMock()
    service.send_message = AsyncMock()
    service.receive_message = AsyncMock()
    service.on_message = Mock()
    return service


@pytest.fixture
def emergency_service():
    """Mock emergency service"""
    service = Mock()
    service.get_alerts = AsyncMock()
    service.acknowledge_alert = AsyncMock()
    service.trigger_alert = AsyncMock()
    return service
