"""
Integration Tests for Pagination and Monitoring Systems

Tests the complete integration of pagination and monitoring features
with child safety compliance.
"""

import pytest
from datetime import datetime, timedelta
from typing import List, Dict

from src.infrastructure.pagination import (
    PaginationService,
    PaginationRequest,
    SortOrder,
)
from src.infrastructure.monitoring import (
    monitoring_service,
    AlertSeverity,
)
from src.presentation.api.endpoints.conversations_paginated import (
    ConversationPaginationService,
)
from src.presentation.api.endpoints.monitoring_dashboard import (
    MonitoringDashboardService,
)


class TestPaginationIntegration:
    """Integration tests for pagination system."""

    @pytest.fixture
    def pagination_service(self):
        """Create pagination service for testing."""
        return PaginationService()

    @pytest.fixture
    def sample_data(self):
        """Create sample data for pagination testing."""
        return [
            {
                "id": i,
                "name": f"Item {i}",
                "created_at": datetime.utcnow() - timedelta(days=i),
            }
            for i in range(1, 101)  # 100 items
        ]

    def test_basic_pagination(self, pagination_service, sample_data):
        """Test basic pagination functionality."""
        request = PaginationRequest(page=1, size=10)
        result = pagination_service.paginate_list(sample_data, request)

        assert len(result.items) == 10
        assert result.metadata.page == 1
        assert result.metadata.size == 10
        assert result.metadata.total_items == 100
        assert result.metadata.total_pages == 10
        assert result.metadata.has_next is True
        assert result.metadata.has_previous is False

    def test_child_safe_pagination_limits(self, pagination_service):
        """Test that child-safe pagination enforces limits."""
        # Try to request large page size
        request = PaginationRequest(page=1, size=200)
        safe_request = pagination_service.create_child_safe_pagination(request)

        assert safe_request.size <= 50  # Child-safe maximum
        assert safe_request.page <= 1000  # Reasonable page limit

    def test_pagination_with_search(self, pagination_service, sample_data):
        """Test pagination with search functionality."""
        request = PaginationRequest(page=1, size=5, search="Item 1")
        result = pagination_service.paginate_list(sample_data, request)

        # Should find items containing "Item 1" (Item 1, Item 10, Item 11,
        # etc.)
        assert len(result.items) > 0
        for item in result.items:
            assert "1" in str(item["name"])

    def test_pagination_with_sorting(self, pagination_service, sample_data):
        """Test pagination with sorting."""
        request = PaginationRequest(
            page=1, size=5, sort_by="id", sort_order=SortOrder.DESC
        )
        result = pagination_service.paginate_list(sample_data, request)

        # Should be sorted by ID in descending order
        assert len(result.items) == 5
        ids = [item["id"] for item in result.items]
        assert ids == sorted(ids, reverse=True)

    @pytest.mark.asyncio
    async def test_conversation_pagination_integration(self):
        """Test conversation pagination service integration."""
        service = ConversationPaginationService()
        request = PaginationRequest(page=1, size=10)

        result = await service.get_child_conversations("child_123", request)

        assert result.metadata.page == 1
        assert result.metadata.size == 10
        assert len(result.items) <= 10

        # Check conversation structure
        if result.items:
            conversation = result.items[0]
            assert "conversation_id" in conversation
            assert "child_id" in conversation
            assert "timestamp" in conversation

    @pytest.mark.asyncio
    async def test_conversation_search_integration(self):
        """Test conversation search with pagination."""
        service = ConversationPaginationService()

        result = await service.search_conversations(
            "child_123", "hello", PaginationRequest(page=1, size=5)
        )

        assert result.metadata.page == 1
        # Search results should contain the search term
        for item in result.items:
            message_text = (
                item.get("child_message", "").lower()
                + item.get("ai_response", "").lower()
            )
            assert "hello" in message_text


class TestMonitoringIntegration:
    """Integration tests for monitoring system."""

    def test_metric_recording_and_retrieval(self):
        """Test recording and retrieving metrics."""
        # Record test metrics
        monitoring_service.record_metric("test_metric", 42.0, {"env": "test"})
        monitoring_service.record_metric("test_metric", 43.0, {"env": "test"})

        # Check metrics were recorded
        assert "test_metric" in monitoring_service.metrics
        assert len(monitoring_service.metrics["test_metric"]) >= 2

        # Check latest value
        latest_metric = monitoring_service.metrics["test_metric"][-1]
        assert latest_metric.value == 43.0
        assert latest_metric.tags["env"] == "test"

    def test_child_safety_event_recording(self):
        """Test child safety event recording and alerting."""
        initial_events = len(
            monitoring_service.child_safety_monitor.safety_events
        )

        # Record a child safety event
        monitoring_service.record_child_safety_event(
            child_id="child_123",
            event_type="inappropriate_content_blocked",
            severity="medium",
            details={"content_type": "text", "reason": "profanity"},
        )

        # Check event was recorded
        assert (
            len(monitoring_service.child_safety_monitor.safety_events)
            == initial_events + 1
        )

        # Check latest event
        latest_event = monitoring_service.child_safety_monitor.safety_events[
            -1
        ]
        assert latest_event["child_id"] == "child_123"
        assert latest_event["event_type"] == "inappropriate_content_blocked"
        assert latest_event["severity"] == "medium"

    def test_emergency_alert_creation(self):
        """Test emergency alert creation for critical child safety events."""
        initial_alerts = len(
            monitoring_service.child_safety_monitor.safety_alerts
        )

        # Record an emergency event
        monitoring_service.record_child_safety_event(
            child_id="child_456",
            event_type="severe_distress",
            severity="emergency",
            details={"distress_level": "high", "requires_intervention": True},
        )

        # Check emergency alert was created
        assert (
            len(monitoring_service.child_safety_monitor.safety_alerts)
            > initial_alerts
        )

        # Find the emergency alert
        emergency_alerts = [
            alert
            for alert in monitoring_service.child_safety_monitor.safety_alerts.values()
            if alert.get("severity") == "EMERGENCY"
        ]
        assert len(emergency_alerts) > 0

    def test_security_event_monitoring(self):
        """Test security event monitoring and tracking."""
        # Record security events
        monitoring_service.record_security_event(
            event_type="failed_authentication",
            user_id="user_123",
            ip_address="192.168.1.100",
            details={"attempt_count": 1},
        )

        # Check event was recorded
        assert len(monitoring_service.suspicious_activities) > 0

        # Check failed auth tracking
        assert "192.168.1.100" in monitoring_service.failed_auth_attempts
        assert monitoring_service.failed_auth_attempts["192.168.1.100"] >= 1

    def test_coppa_compliance_monitoring(self):
        """Test COPPA compliance event monitoring."""
        initial_logs = len(monitoring_service.data_access_logs)

        # Record COPPA event
        monitoring_service.record_coppa_event(
            event_type="data_access",
            child_id="child_789",
            parent_id="parent_123",
            details={"access_type": "profile_view", "consent_valid": True},
        )

        # Check event was logged
        assert len(monitoring_service.data_access_logs) == initial_logs + 1

        # Check latest log
        latest_log = monitoring_service.data_access_logs[-1]
        assert latest_log["child_id"] == "child_789"
        assert latest_log["parent_id"] == "parent_123"
        assert latest_log["event_type"] == "data_access"

    def test_alert_rule_creation_and_triggering(self):
        """Test alert rule creation and triggering."""
        # Add a test alert rule
        alert_id = monitoring_service.add_alert_rule(
            name="Test High Value Alert",
            description="Test alert for high values",
            severity=AlertSeverity.HIGH,
            condition="test_value > 100",
            threshold=100.0,
            metric_name="test_value",
        )

        assert alert_id in monitoring_service.alerts

        # Trigger the alert
        monitoring_service.record_metric("test_value", 150.0)

        # Check alert was triggered
        alert = monitoring_service.alerts[alert_id]
        assert alert.trigger_count > 0
        assert alert.last_triggered is not None

    @pytest.mark.asyncio
    async def test_monitoring_dashboard_integration(self):
        """Test monitoring dashboard service integration."""
        dashboard_service = MonitoringDashboardService()

        # Record some test data
        monitoring_service.record_metric("cpu_usage", 0.75)
        monitoring_service.record_metric("memory_usage", 0.60)
        monitoring_service.record_metric("error_rate", 0.02)

        # Get system health
        health = await dashboard_service.get_system_health()

        assert "overall_health" in health
        assert "metrics_summary" in health
        assert "recent_alerts" in health
        assert "child_safety" in health
        assert health["system_status"] in ["operational", "degraded"]

    @pytest.mark.asyncio
    async def test_child_safety_dashboard_integration(self):
        """Test child safety dashboard integration."""
        dashboard_service = MonitoringDashboardService()

        # Record some child safety events
        monitoring_service.record_child_safety_event(
            "child_001", "content_filter", "low", {"filtered_words": 1}
        )
        monitoring_service.record_child_safety_event(
            "child_002", "emotional_support", "medium", {"emotion": "sad"}
        )

        # Get child safety dashboard
        safety_dashboard = await dashboard_service.get_child_safety_dashboard()

        assert "total_events" in safety_dashboard
        assert "event_types" in safety_dashboard
        assert "severity_distribution" in safety_dashboard
        assert "monitoring_status" in safety_dashboard
        assert safety_dashboard["monitoring_status"] == "active"


class TestIntegratedWorkflow:
    """Test complete integrated workflows."""

    @pytest.mark.asyncio
    async def test_child_data_access_with_monitoring(self):
        """Test complete workflow of child data access with monitoring."""
        # Simulate parent accessing child data with pagination
        conversation_service = ConversationPaginationService()

        # Record the data access for COPPA compliance
        monitoring_service.record_coppa_event(
            event_type="data_access",
            child_id="child_workflow_test",
            parent_id="parent_workflow_test",
            details={"access_type": "conversation_history", "page": 1},
        )

        # Get paginated conversations
        pagination_request = PaginationRequest(page=1, size=20)
        result = await conversation_service.get_child_conversations(
            "child_workflow_test", pagination_request, "parent_workflow_test"
        )

        # Record performance metric
        monitoring_service.record_request_time("get_child_conversations", 0.25)

        # Verify workflow completed successfully
        assert result.metadata.page == 1
        assert len(monitoring_service.data_access_logs) > 0
        assert len(monitoring_service.request_times) > 0

        # Check COPPA compliance was logged
        latest_coppa_log = monitoring_service.data_access_logs[-1]
        assert latest_coppa_log["child_id"] == "child_workflow_test"
        assert latest_coppa_log["parent_id"] == "parent_workflow_test"

    @pytest.mark.asyncio
    async def test_safety_incident_workflow(self):
        """Test complete safety incident detection and response workflow."""
        dashboard_service = MonitoringDashboardService()

        # Simulate multiple safety events (pattern detection)
        child_id = "child_safety_workflow"

        for i in range(6):  # Trigger threshold
            monitoring_service.record_child_safety_event(
                child_id=child_id,
                event_type="inappropriate_content_blocked",
                severity="medium",
                details={"attempt": i + 1, "content": f"blocked_content_{i}"},
            )

        # Check that pattern alert was created
        safety_alerts = monitoring_service.child_safety_monitor.safety_alerts
        pattern_alerts = [
            alert
            for alert in safety_alerts.values()
            if alert.get("pattern_type") == "excessive_inappropriate_content"
        ]

        assert len(pattern_alerts) > 0

        # Get safety dashboard to verify incident is visible
        safety_dashboard = await dashboard_service.get_child_safety_dashboard()

        assert safety_dashboard["total_events"] >= 6
        assert (
            "inappropriate_content_blocked" in safety_dashboard["event_types"]
        )
        assert safety_dashboard["active_alerts"] > 0

    def test_performance_monitoring_integration(self):
        """Test performance monitoring with pagination."""
        from src.infrastructure.monitoring import monitor_performance

        @monitor_performance("test_paginated_function")
        def sample_paginated_function(items: List[Dict], page_size: int):
            """Sample function with performance monitoring."""
            # Simulate processing time
            import time

            time.sleep(0.1)

            # Return paginated results
            pagination_service = PaginationService()
            request = PaginationRequest(page=1, size=page_size)
            return pagination_service.paginate_list(items, request)

        # Create test data
        test_items = [{"id": i, "value": f"item_{i}"} for i in range(50)]

        # Call monitored function
        result = sample_paginated_function(test_items, 10)

        # Check result
        assert len(result.items) == 10
        assert result.metadata.total_items == 50

        # Check monitoring recorded the performance
        assert len(monitoring_service.request_times) > 0
        latest_request = monitoring_service.request_times[-1]
        assert latest_request["endpoint"] == "test_paginated_function"
        assert latest_request["duration"] >= 0.1  # Should include sleep time


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
