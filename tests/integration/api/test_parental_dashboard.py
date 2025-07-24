import sys
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import AsyncMock, patch
from uuid import uuid4

from httpx import AsyncClient

from application.dto.child_data import ChildData

# Add src to path
src_path = Path(__file__).parent
while src_path.name != "backend" and src_path.parent != src_path:
    src_path = src_path.parent
src_path = src_path / "src"

if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

"""Integration tests for Parental Dashboard API endpoints."""

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


class TestParentalDashboardEndpoints:
    """Test Parental Dashboard API endpoints."""

    @pytest.fixture
    async def client(self):
        """Create test client."""
        from main import app

        async with AsyncClient(app=app, base_url="http://test") as ac:
            yield ac

    @pytest.fixture
    def auth_headers(self):
        """Mock authentication headers."""
        return {
            "Authorization": "Bearer mock_parent_token",
            "Content-Type": "application/json",
        }

    @pytest.fixture
    def child_data(self):
        """Mock child data."""
        return ChildData(
            id=uuid4(),
            name="Emma",
            age=7,
            preferences={
                "language": "en",
                "interests": ["animals", "stories", "music"],
                "safety_level": "safe",
                "voice_preference": "child-en-us",
            },
        )

    @pytest.mark.asyncio
    async def test_get_children_list(self, client, auth_headers, child_data):
        """Test getting list of children for parent."""
        with patch(
            "application.use_cases.manage_child_profile.ManageChildProfileUseCase"
        ) as mock_use_case:
            mock_use_case_instance = AsyncMock()
            mock_use_case_instance.get_children_for_parent.return_value = [child_data]
            mock_use_case.return_value = mock_use_case_instance

            response = await client.get(
                "/api/v1/dashboard/children", headers=auth_headers
            )

            assert response.status_code == 200
            data = response.json()
            assert len(data["children"]) == 1
            assert data["children"][0]["name"] == "Emma"
            assert data["children"][0]["age"] == 7

    @pytest.mark.asyncio
    async def test_create_child_profile(self, client, auth_headers):
        """Test creating a new child profile."""
        child_data_input = {
            "name": "Alex",
            "age": 5,
            "preferences": {
                "language": "es",
                "interests": ["dinosaurs", "space"],
                "voice_preference": "child-es-mx",
            },
        }

        with patch(
            "application.use_cases.manage_child_profile.ManageChildProfileUseCase"
        ) as mock_use_case:
            mock_use_case_instance = AsyncMock()
            created_child = ChildData(
                id=uuid4(),
                name="Alex",
                age=5,
                preferences=child_data_input["preferences"],
            )
            mock_use_case_instance.create_child_profile.return_value = created_child
            mock_use_case.return_value = mock_use_case_instance

            response = await client.post(
                "/api/v1/dashboard/children",
                json=child_data_input,
                headers=auth_headers,
            )

            assert response.status_code == 201
            data = response.json()
            assert data["name"] == "Alex"
            assert data["age"] == 5
            assert data["preferences"]["language"] == "es"

    @pytest.mark.asyncio
    async def test_update_child_profile(self, client, auth_headers, child_data):
        """Test updating child profile."""
        child_id = str(child_data.id)
        update_data = {
            "name": "Emma Rose",
            "age": 8,
            "preferences": {"interests": ["animals", "stories", "music", "art"]},
        }

        with patch(
            "application.use_cases.manage_child_profile.ManageChildProfileUseCase"
        ) as mock_use_case:
            mock_use_case_instance = AsyncMock()
            updated_child = ChildData(
                id=child_data.id,
                name="Emma Rose",
                age=8,
                preferences=update_data["preferences"],
            )
            mock_use_case_instance.update_child_profile.return_value = updated_child
            mock_use_case.return_value = mock_use_case_instance

            response = await client.put(
                f"/api/v1/dashboard/children/{child_id}",
                json=update_data,
                headers=auth_headers,
            )

            assert response.status_code == 200
            data = response.json()
            assert data["name"] == "Emma Rose"
            assert data["age"] == 8
            assert "art" in data["preferences"]["interests"]

    @pytest.mark.asyncio
    async def test_delete_child_profile(self, client, auth_headers, child_data):
        """Test deleting child profile."""
        child_id = str(child_data.id)

        with patch(
            "application.use_cases.manage_child_profile.ManageChildProfileUseCase"
        ) as mock_use_case:
            mock_use_case_instance = AsyncMock()
            mock_use_case_instance.delete_child_profile.return_value = True
            mock_use_case.return_value = mock_use_case_instance

            response = await client.delete(
                f"/api/v1/dashboard/children/{child_id}", headers=auth_headers
            )

            assert response.status_code == 204

    @pytest.mark.asyncio
    async def test_get_conversation_history(self, client, auth_headers, child_data):
        """Test getting conversation history for child."""
        child_id = str(child_data.id)
        mock_conversations = [
            {
                "id": str(uuid4()),
                "child_id": child_id,
                "started_at": datetime.utcnow().isoformat(),
                "ended_at": (datetime.utcnow() + timedelta(minutes=5)).isoformat(),
                "message_count": 8,
                "summary": "Conversation about favorite animals",
                "safety_score": 0.95,
                "emotions": ["happy", "curious", "excited"],
            },
            {
                "id": str(uuid4()),
                "child_id": child_id,
                "started_at": (datetime.utcnow() - timedelta(hours=2)).isoformat(),
                "ended_at": (
                    datetime.utcnow() - timedelta(hours=2) + timedelta(minutes=10)
                ).isoformat(),
                "message_count": 15,
                "summary": "Story time about brave knights",
                "safety_score": 0.98,
                "emotions": ["excited", "brave", "happy"],
            },
        ]

        with patch(
            "application.services.conversation_service.ConversationService"
        ) as mock_service:
            mock_service_instance = AsyncMock()
            mock_service_instance.get_conversation_history.return_value = (
                mock_conversations
            )
            mock_service.return_value = mock_service_instance

            response = await client.get(
                f"/api/v1/dashboard/children/{child_id}/conversations",
                headers=auth_headers,
            )

            assert response.status_code == 200
            data = response.json()
            assert len(data["conversations"]) == 2
            assert (
                data["conversations"][0]["summary"]
                == "Conversation about favorite animals"
            )
            assert data["conversations"][1]["message_count"] == 15

    @pytest.mark.asyncio
    async def test_get_safety_report(self, client, auth_headers, child_data):
        """Test getting safety report for child."""
        child_id = str(child_data.id)
        mock_safety_report = {
            "child_id": child_id,
            "report_period": "last_30_days",
            "total_interactions": 45,
            "safety_violations": 0,
            "average_safety_score": 0.96,
            "content_categories": {
                "educational": 25,
                "entertainment": 15,
                "social": 5,
            },
            "emotion_analysis": {
                "happy": 60,
                "curious": 25,
                "excited": 10,
                "neutral": 5,
            },
            "recommendations": [
                "Continue encouraging educational conversations",
                "Consider introducing more creative activities",
            ],
        }

        with patch(
            "infrastructure.security.safety_monitor_service.SafetyMonitorService"
        ) as mock_service:
            mock_service_instance = AsyncMock()
            mock_service_instance.generate_safety_report.return_value = (
                mock_safety_report
            )
            mock_service.return_value = mock_service_instance

            response = await client.get(
                f"/api/v1/dashboard/children/{child_id}/safety-report",
                headers=auth_headers,
            )

            assert response.status_code == 200
            data = response.json()
            assert data["total_interactions"] == 45
            assert data["safety_violations"] == 0
            assert data["average_safety_score"] == 0.96
            assert len(data["recommendations"]) == 2

    @pytest.mark.asyncio
    async def test_get_usage_analytics(self, client, auth_headers, child_data):
        """Test getting usage analytics for child."""
        child_id = str(child_data.id)
        mock_analytics = {
            "child_id": child_id,
            "daily_usage": [
                {"date": "2025-01-01", "minutes": 25, "interactions": 8},
                {"date": "2025-01-02", "minutes": 30, "interactions": 12},
                {"date": "2025-01-03", "minutes": 20, "interactions": 6},
            ],
            "weekly_summary": {
                "total_minutes": 175,
                "total_interactions": 52,
                "average_session_length": 3.4,
                "most_active_time": "16:00-17:00",
            },
            "learning_progress": {
                "vocabulary_growth": 15,
                "comprehension_improvement": 8,
                "engagement_level": "high",
            },
            "favorite_topics": [
                {"topic": "animals", "frequency": 35},
                {"topic": "stories", "frequency": 28},
                {"topic": "science", "frequency": 15},
            ],
        }

        with patch(
            "application.services.analytics_service.AnalyticsService"
        ) as mock_service:
            mock_service_instance = AsyncMock()
            mock_service_instance.get_child_analytics.return_value = mock_analytics
            mock_service.return_value = mock_service_instance

            response = await client.get(
                f"/api/v1/dashboard/children/{child_id}/analytics",
                headers=auth_headers,
            )

            assert response.status_code == 200
            data = response.json()
            assert data["weekly_summary"]["total_minutes"] == 175
            assert len(data["daily_usage"]) == 3
            assert data["learning_progress"]["engagement_level"] == "high"

    @pytest.mark.asyncio
    async def test_update_parental_controls(self, client, auth_headers, child_data):
        """Test updating parental controls."""
        child_id = str(child_data.id)
        controls_data = {
            "content_filtering": {
                "enabled": True,
                "strictness_level": "moderate",
                "blocked_categories": ["violence", "scary_content"],
                "allowed_topics": ["educational", "entertainment", "creative"],
            },
            "time_limits": {
                "daily_limit_minutes": 60,
                "session_limit_minutes": 20,
                "quiet_hours": {
                    "enabled": True,
                    "start_time": "20:00",
                    "end_time": "08:00",
                },
            },
            "interaction_settings": {
                "require_parent_approval": False,
                "allow_personal_info_sharing": False,
                "emergency_contact": "+1234567890",
            },
        }

        response = await client.put(
            f"/api/v1/dashboard/children/{child_id}/parental-controls",
            json=controls_data,
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "controls_updated" in data

    @pytest.mark.asyncio
    async def test_get_device_status(self, client, auth_headers):
        """Test getting ESP32 device status."""
        mock_device_status = {
            "devices": [
                {
                    "device_id": "esp32_001",
                    "child_id": str(uuid4()),
                    "status": "online",
                    "last_seen": datetime.utcnow().isoformat(),
                    "battery_level": 78,
                    "wifi_strength": -42,
                    "firmware_version": "2.1.0",
                    "location": "Emma's Room",
                }
            ],
            "total_devices": 1,
            "online_devices": 1,
            "offline_devices": 0,
        }

        with patch(
            "application.services.esp32_device_service.ESP32DeviceService"
        ) as mock_service:
            mock_service_instance = AsyncMock()
            mock_service_instance.get_device_status.return_value = mock_device_status
            mock_service.return_value = mock_service_instance

            response = await client.get(
                "/api/v1/dashboard/devices", headers=auth_headers
            )

            assert response.status_code == 200
            data = response.json()
            assert data["total_devices"] == 1
            assert data["online_devices"] == 1
            assert len(data["devices"]) == 1
            assert data["devices"][0]["battery_level"] == 78

    @pytest.mark.asyncio
    async def test_unauthorized_access(self, client):
        """Test unauthorized access to dashboard endpoints."""
        # Test without auth headers
        response = await client.get("/api/v1/dashboard/children")
        assert response.status_code == 401

        # Test with invalid token
        invalid_headers = {"Authorization": "Bearer invalid_token"}
        response = await client.get(
            "/api/v1/dashboard/children", headers=invalid_headers
        )
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_access_other_parent_child(self, client, auth_headers):
        """Test accessing another parent's child data."""
        other_child_id = str(uuid4())

        # Should not be able to access other parent's child
        response = await client.get(
            f"/api/v1/dashboard/children/{other_child_id}/conversations",
            headers=auth_headers,
        )

        assert response.status_code in [403, 404]  # Forbidden or Not Found

    @pytest.mark.asyncio
    async def test_input_validation(self, client, auth_headers):
        """Test input validation on dashboard endpoints."""
        # Test invalid child data
        invalid_child_data = {
            "name": "",  # Empty name
            "age": -5,  # Negative age
            "preferences": "invalid",  # Wrong type
        }

        response = await client.post(
            "/api/v1/dashboard/children",
            json=invalid_child_data,
            headers=auth_headers,
        )

        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_pagination(self, client, auth_headers, child_data):
        """Test pagination in conversation history."""
        child_id = str(child_data.id)

        response = await client.get(
            f"/api/v1/dashboard/children/{child_id}/conversations?page=1&limit=10",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert "page" in data
        assert "limit" in data
        assert "total" in data
        assert "conversations" in data

    @pytest.mark.asyncio
    async def test_filtering_and_sorting(self, client, auth_headers, child_data):
        """Test filtering and sorting in analytics."""
        child_id = str(child_data.id)

        response = await client.get(
            f"/api/v1/dashboard/children/{child_id}/conversations?start_date=2025-01-01&end_date=2025-01-31&sort=date&order=desc",
            headers=auth_headers,
        )

        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_export_data(self, client, auth_headers, child_data):
        """Test exporting child data."""
        child_id = str(child_data.id)

        response = await client.get(
            f"/api/v1/dashboard/children/{child_id}/export?format=json",
            headers=auth_headers,
        )

        assert response.status_code == 200
        assert response.headers["content-type"] == "application/json"

    @pytest.mark.asyncio
    async def test_real_time_notifications(self, client, auth_headers):
        """Test real-time notification settings."""
        notification_settings = {
            "safety_alerts": True,
            "usage_reminders": True,
            "device_status": False,
            "weekly_reports": True,
            "email_notifications": True,
            "push_notifications": False,
        }

        response = await client.put(
            "/api/v1/dashboard/notification-settings",
            json=notification_settings,
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
