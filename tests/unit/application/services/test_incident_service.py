"""
Tests for Incident Service
Testing incident reporting, tracking, and resolution functionality.
"""

import pytest
from datetime import datetime
from unittest.mock import patch

from src.application.services.incident_service import IncidentService


class TestIncidentService:
    """Test the Incident Service."""

    @pytest.fixture
    def service(self):
        """Create an incident service instance."""
        return IncidentService()

    def test_initialization(self, service):
        """Test service initialization."""
        assert isinstance(service, IncidentService)
        assert hasattr(service, "incidents")
        assert isinstance(service.incidents, list)
        assert len(service.incidents) == 0

    @pytest.mark.asyncio
    async def test_report_incident_basic(self, service):
        """Test basic incident reporting."""
        # Arrange
        incident_details = {
            "title": "System Error",
            "description": "Database connection timeout",
            "severity": "high",
            "reporter": "user_123",
        }

        with patch(
            "src.application.services.incident_service.datetime"
        ) as mock_datetime:
            mock_datetime.utcnow.return_value = datetime(
                2024, 1, 15, 10, 30, 0
            )

            # Act
            result = await service.report_incident(incident_details)

        # Assert
        assert result["id"] == "inc_1"
        assert result["status"] == "reported"
        assert result["timestamp"] == "2024-01-15T10:30:00"
        assert result["title"] == "System Error"
        assert result["description"] == "Database connection timeout"
        assert result["severity"] == "high"
        assert result["reporter"] == "user_123"

        # Check it's stored in incidents list
        assert len(service.incidents) == 1
        assert service.incidents[0] == result

    @pytest.mark.asyncio
    async def test_report_multiple_incidents(self, service):
        """Test reporting multiple incidents."""
        incidents_data = [
            {"title": "Error 1", "description": "First error"},
            {"title": "Error 2", "description": "Second error"},
            {"title": "Error 3", "description": "Third error"},
        ]

        results = []
        for incident_data in incidents_data:
            result = await service.report_incident(incident_data)
            results.append(result)

        # Check all incidents were created with unique IDs
        assert len(results) == 3
        assert len(service.incidents) == 3

        assert results[0]["id"] == "inc_1"
        assert results[1]["id"] == "inc_2"
        assert results[2]["id"] == "inc_3"

        # All should have "reported" status
        assert all(r["status"] == "reported" for r in results)

    @pytest.mark.asyncio
    async def test_report_incident_empty_details(self, service):
        """Test reporting incident with empty details."""
        result = await service.report_incident({})

        assert result["id"] == "inc_1"
        assert result["status"] == "reported"
        assert "timestamp" in result
        # Should not have any additional fields
        assert len(result) == 3  # Only id, status, timestamp

    @pytest.mark.asyncio
    async def test_report_incident_comprehensive_details(self, service):
        """Test reporting incident with comprehensive details."""
        incident_details = {
            "title": "Critical System Failure",
            "description": "Complete system shutdown occurred at 10:30 AM",
            "severity": "critical",
            "category": "system",
            "reporter": "admin_user",
            "affected_users": 150,
            "estimated_downtime": "2 hours",
            "error_code": "SYS_001",
            "stack_trace": "Error at line 245...",
            "environment": "production",
            "component": "database_service",
        }

        result = await service.report_incident(incident_details)

        # Check all details are preserved
        for key, value in incident_details.items():
            assert result[key] == value

        # Plus the added fields
        assert result["id"] == "inc_1"
        assert result["status"] == "reported"
        assert "timestamp" in result

    @pytest.mark.asyncio
    async def test_get_incident_existing(self, service):
        """Test retrieving an existing incident."""
        # First, report an incident
        incident_details = {
            "title": "Test Incident",
            "description": "Test description",
        }
        reported = await service.report_incident(incident_details)
        incident_id = reported["id"]

        # Then retrieve it
        result = await service.get_incident(incident_id)

        assert result is not None
        assert result == reported
        assert result["id"] == incident_id

    @pytest.mark.asyncio
    async def test_get_incident_non_existing(self, service):
        """Test retrieving a non-existing incident."""
        result = await service.get_incident("non_existing_id")

        assert result is None

    @pytest.mark.asyncio
    async def test_get_incident_from_multiple(self, service):
        """Test retrieving specific incident when multiple exist."""
        # Report multiple incidents
        incidents_data = [
            {"title": "Incident A", "type": "error"},
            {"title": "Incident B", "type": "warning"},
            {"title": "Incident C", "type": "info"},
        ]

        reported_incidents = []
        for data in incidents_data:
            incident = await service.report_incident(data)
            reported_incidents.append(incident)

        # Retrieve specific incident
        target_id = reported_incidents[1]["id"]  # Get the middle one
        result = await service.get_incident(target_id)

        assert result is not None
        assert result["title"] == "Incident B"
        assert result["type"] == "warning"
        assert result["id"] == target_id

    @pytest.mark.asyncio
    async def test_resolve_incident_existing(self, service):
        """Test resolving an existing incident."""
        # First, report an incident
        incident_details = {
            "title": "Bug Report",
            "description": "UI not responsive",
        }
        reported = await service.report_incident(incident_details)
        incident_id = reported["id"]

        # Then resolve it
        resolution_details = {
            "solution": "Updated CSS files",
            "resolved_by": "developer_123",
            "resolution_notes": "Fixed responsive design issues",
        }

        with patch(
            "src.application.services.incident_service.datetime"
        ) as mock_datetime:
            mock_datetime.utcnow.return_value = datetime(
                2024, 1, 15, 14, 45, 0
            )

            result = await service.resolve_incident(
                incident_id, resolution_details
            )

        # Check resolution
        assert result is not None
        assert result["status"] == "resolved"
        assert result["resolved_at"] == "2024-01-15T14:45:00"
        assert result["resolution_details"] == resolution_details

        # Original details should be preserved
        assert result["title"] == "Bug Report"
        assert result["description"] == "UI not responsive"

        # Check it's updated in the incidents list
        stored_incident = service.incidents[0]
        assert stored_incident["status"] == "resolved"

    @pytest.mark.asyncio
    async def test_resolve_incident_non_existing(self, service):
        """Test resolving a non-existing incident."""
        resolution_details = {"solution": "Fixed the issue"}

        result = await service.resolve_incident(
            "non_existing_id", resolution_details
        )

        assert result is None

    @pytest.mark.asyncio
    async def test_resolve_incident_empty_resolution(self, service):
        """Test resolving incident with empty resolution details."""
        # Report incident first
        reported = await service.report_incident({"title": "Test Incident"})
        incident_id = reported["id"]

        # Resolve with empty details
        result = await service.resolve_incident(incident_id, {})

        assert result is not None
        assert result["status"] == "resolved"
        assert result["resolution_details"] == {}
        assert "resolved_at" in result

    @pytest.mark.asyncio
    async def test_incident_workflow_complete(self, service):
        """Test complete incident workflow: report -> get -> resolve -> get."""
        # Step 1: Report incident
        incident_details = {
            "title": "Authentication Error",
            "description": "Users cannot log in",
            "severity": "high",
            "reporter": "support_team",
        }

        reported = await service.report_incident(incident_details)
        incident_id = reported["id"]

        # Step 2: Get incident (verify it exists)
        retrieved = await service.get_incident(incident_id)
        assert retrieved is not None
        assert retrieved["status"] == "reported"

        # Step 3: Resolve incident
        resolution_details = {
            "solution": "Restarted authentication service",
            "resolved_by": "ops_team",
            "root_cause": "Service memory leak",
        }

        resolved = await service.resolve_incident(
            incident_id, resolution_details
        )
        assert resolved is not None
        assert resolved["status"] == "resolved"

        # Step 4: Get resolved incident
        final_state = await service.get_incident(incident_id)
        assert final_state["status"] == "resolved"
        assert final_state["resolution_details"] == resolution_details
        assert "resolved_at" in final_state

    @pytest.mark.asyncio
    async def test_concurrent_incident_operations(self, service):
        """Test concurrent incident operations."""
        import asyncio

        # Create multiple incidents concurrently
        incident_tasks = [
            service.report_incident(
                {"title": f"Incident {i}", "description": f"Description {i}"}
            )
            for i in range(5)
        ]

        incidents = await asyncio.gather(*incident_tasks)

        # All should be created successfully
        assert len(incidents) == 5
        assert len(service.incidents) == 5

        # All should have unique IDs
        incident_ids = [inc["id"] for inc in incidents]
        assert len(set(incident_ids)) == 5

        # All should be in "reported" status
        assert all(inc["status"] == "reported" for inc in incidents)

    @pytest.mark.asyncio
    async def test_incident_id_generation(self, service):
        """Test incident ID generation pattern."""
        # Report several incidents
        incidents = []
        for i in range(10):
            incident = await service.report_incident({"title": f"Test {i}"})
            incidents.append(incident)

        # Check ID pattern
        expected_ids = [f"inc_{i+1}" for i in range(10)]
        actual_ids = [inc["id"] for inc in incidents]

        assert actual_ids == expected_ids

    @pytest.mark.asyncio
    async def test_incident_timestamp_format(self, service):
        """Test that incident timestamps are in correct ISO format."""
        incident_details = {"title": "Timestamp Test"}

        with patch(
            "src.application.services.incident_service.datetime"
        ) as mock_datetime:
            # Mock specific datetime
            mock_datetime.utcnow.return_value = datetime(
                2024, 3, 15, 9, 45, 30, 123456
            )

            incident = await service.report_incident(incident_details)

        # Check timestamp format
        assert incident["timestamp"] == "2024-03-15T09:45:30.123456"

        # Should be valid ISO format
        parsed_time = datetime.fromisoformat(incident["timestamp"])
        assert parsed_time.year == 2024
        assert parsed_time.month == 3
        assert parsed_time.day == 15

    @pytest.mark.asyncio
    async def test_resolution_timestamp_format(self, service):
        """Test that resolution timestamps are in correct ISO format."""
        # Report incident
        incident = await service.report_incident({"title": "Resolution Test"})

        with patch(
            "src.application.services.incident_service.datetime"
        ) as mock_datetime:
            # Mock specific resolution time
            mock_datetime.utcnow.return_value = datetime(
                2024, 3, 15, 11, 30, 45, 789012
            )

            resolved = await service.resolve_incident(
                incident["id"], {"solution": "Fixed"}
            )

        # Check resolution timestamp format
        assert resolved["resolved_at"] == "2024-03-15T11:30:45.789012"

        # Should be valid ISO format
        parsed_time = datetime.fromisoformat(resolved["resolved_at"])
        assert parsed_time.hour == 11
        assert parsed_time.minute == 30

    @pytest.mark.asyncio
    async def test_incident_data_persistence(self, service):
        """Test that incident data persists across operations."""
        # Report incident
        original_details = {
            "title": "Persistence Test",
            "description": "Testing data persistence",
            "priority": "medium",
            "custom_field": "custom_value",
        }

        incident = await service.report_incident(original_details)
        incident_id = incident["id"]

        # Resolve incident
        resolution = {"solution": "Resolved successfully"}
        resolved = await service.resolve_incident(incident_id, resolution)

        # Verify all original data is preserved
        for key, value in original_details.items():
            assert resolved[key] == value

        # Plus resolution data
        assert resolved["status"] == "resolved"
        assert resolved["resolution_details"] == resolution
        assert "resolved_at" in resolved

    @pytest.mark.asyncio
    async def test_edge_cases_special_characters(self, service):
        """Test incident handling with special characters."""
        special_details = {
            "title": "Special chars: !@#$%^&*()_+{}|:<>?",
            "description": "Testing with émojis 🚨 and ñoñó",
            "unicode_field": "测试中文字符",
            "newlines": "Line 1\nLine 2\nLine 3",
            "quotes": "Both \"double\" and 'single' quotes",
        }

        incident = await service.report_incident(special_details)

        # Should handle special characters without issues
        assert incident["title"] == special_details["title"]
        assert incident["description"] == special_details["description"]
        assert incident["unicode_field"] == special_details["unicode_field"]

        # Retrieve and verify
        retrieved = await service.get_incident(incident["id"])
        assert retrieved["title"] == special_details["title"]

    @pytest.mark.parametrize("incident_count", [1, 10, 50, 100])
    @pytest.mark.asyncio
    async def test_service_scalability(self, service, incident_count):
        """Test service performance with varying numbers of incidents."""
        # Create many incidents
        incidents = []
        for i in range(incident_count):
            incident = await service.report_incident(
                {
                    "title": f"Incident {i}",
                    "description": f"Description for incident {i}",
                }
            )
            incidents.append(incident)

        # Verify all were created
        assert len(service.incidents) == incident_count

        # Test retrieval performance
        middle_id = (
            incidents[incident_count // 2]["id"] if incidents else "inc_1"
        )
        retrieved = await service.get_incident(middle_id)

        if incident_count > 0:
            assert retrieved is not None
            assert retrieved["id"] == middle_id

    @pytest.mark.asyncio
    async def test_incident_state_isolation(self):
        """Test that different service instances maintain separate state."""
        service1 = IncidentService()
        service2 = IncidentService()

        # Add incident to first service
        await service1.report_incident({"title": "Service 1 Incident"})

        # Second service should be empty
        assert len(service1.incidents) == 1
        assert len(service2.incidents) == 0

        # Add incident to second service
        await service2.report_incident({"title": "Service 2 Incident"})

        # Each should have their own incident
        assert len(service1.incidents) == 1
        assert len(service2.incidents) == 1
        assert service1.incidents[0]["title"] == "Service 1 Incident"
        assert service2.incidents[0]["title"] == "Service 2 Incident"
