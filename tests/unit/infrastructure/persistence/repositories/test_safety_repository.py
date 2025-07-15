"""
Test Safety Repository

Comprehensive unit tests for SafetyRepository with child safety and alert functionality.
"""
import pytest
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

from src.infrastructure.persistence.repositories.safety_repository import SafetyRepository
from src.infrastructure.persistence.database import Database
from src.infrastructure.security.database_input_validator import SecurityError


@pytest.fixture
def mock_database():
    """Create mock database instance."""
    database = MagicMock(spec=Database)
    database.get_session = MagicMock()
    return database


@pytest.fixture
def safety_repository(mock_database):
    """Create SafetyRepository instance with mocked dependencies."""
    return SafetyRepository(mock_database)


class TestSafetyEventRecording:
    """Test safety event recording functionality."""
    
    @pytest.mark.asyncio
    async def test_record_safety_event_success(self, safety_repository, mock_database):
        """Test successful safety event recording."""
        # Arrange
        child_id = str(uuid4())
        event_type = "content_filter"
        details = "Filtered inappropriate content in conversation"
        severity = "medium"
        
        with patch('src.infrastructure.persistence.repositories.safety_repository.validate_database_operation',
                  return_value={"data": {
                      "child_id": child_id,
                      "event_type": event_type,
                      "details": details,
                      "severity": severity
                  }}):
            # Act
            event_id = await safety_repository.record_safety_event(
                child_id, event_type, details, severity
            )
            
            # Assert
            assert event_id is not None
            assert isinstance(event_id, str)
    
    @pytest.mark.asyncio
    async def test_record_safety_event_default_severity(self, safety_repository, mock_database):
        """Test safety event recording with default severity."""
        # Arrange
        child_id = str(uuid4())
        event_type = "time_limit_warning"
        details = "Child approaching daily usage limit"
        
        with patch('src.infrastructure.persistence.repositories.safety_repository.validate_database_operation',
                  return_value={"data": {
                      "child_id": child_id,
                      "event_type": event_type,
                      "details": details,
                      "severity": "low"
                  }}):
            # Act
            event_id = await safety_repository.record_safety_event(
                child_id, event_type, details
            )
            
            # Assert
            assert event_id is not None
    
    @pytest.mark.asyncio
    async def test_record_safety_event_critical_severity(self, safety_repository, mock_database):
        """Test recording high-severity safety events."""
        # Arrange
        child_id = str(uuid4())
        event_type = "inappropriate_content_attempt"
        details = "Child attempted to access blocked content multiple times"
        severity = "high"
        
        with patch('src.infrastructure.persistence.repositories.safety_repository.validate_database_operation',
                  return_value={"data": {
                      "child_id": child_id,
                      "event_type": event_type,
                      "details": details,
                      "severity": severity
                  }}):
            # Act
            event_id = await safety_repository.record_safety_event(
                child_id, event_type, details, severity
            )
            
            # Assert
            assert event_id is not None
    
    @pytest.mark.asyncio
    async def test_record_safety_event_security_violation(self, safety_repository, mock_database):
        """Test safety event recording with SQL injection attempt."""
        # Arrange
        child_id = str(uuid4())
        malicious_details = "'; DROP TABLE safety_events; --"
        
        with patch('src.infrastructure.persistence.repositories.safety_repository.validate_database_operation',
                  side_effect=SecurityError("SQL injection detected")):
            # Act & Assert
            with pytest.raises(ValueError, match="Invalid event data"):
                await safety_repository.record_safety_event(
                    child_id, "test_event", malicious_details
                )
    
    @pytest.mark.asyncio
    async def test_record_safety_event_database_error(self, safety_repository, mock_database):
        """Test safety event recording with database error."""
        # Arrange
        child_id = str(uuid4())
        
        with patch('src.infrastructure.persistence.repositories.safety_repository.validate_database_operation',
                  side_effect=Exception("Database connection lost")):
            # Act & Assert
            with pytest.raises(RuntimeError, match="Database error"):
                await safety_repository.record_safety_event(
                    child_id, "test_event", "details"
                )


class TestSafetyScoreUpdate:
    """Test safety score update functionality."""
    
    @pytest.mark.asyncio
    async def test_update_safety_score_success(self, safety_repository, mock_database):
        """Test successful safety score update."""
        # Arrange
        child_id = str(uuid4())
        new_score = 0.85
        reason = "Improved interaction patterns over past week"
        
        with patch('src.infrastructure.persistence.repositories.safety_repository.validate_database_operation',
                  return_value={"data": {
                      "child_id": child_id,
                      "safety_score": new_score,
                      "reason": reason,
                      "updated_at": datetime.utcnow()
                  }}):
            # Act
            result = await safety_repository.update_safety_score(child_id, new_score, reason)
            
            # Assert
            assert result is True
    
    @pytest.mark.asyncio
    async def test_update_safety_score_boundary_values(self, safety_repository, mock_database):
        """Test safety score update with boundary values."""
        child_id = str(uuid4())
        
        # Test minimum valid score (0.0)
        with patch('src.infrastructure.persistence.repositories.safety_repository.validate_database_operation',
                  return_value={"data": {"child_id": child_id, "safety_score": 0.0}}):
            result = await safety_repository.update_safety_score(child_id, 0.0, "Critical safety concern")
            assert result is True
        
        # Test maximum valid score (1.0)
        with patch('src.infrastructure.persistence.repositories.safety_repository.validate_database_operation',
                  return_value={"data": {"child_id": child_id, "safety_score": 1.0}}):
            result = await safety_repository.update_safety_score(child_id, 1.0, "Perfect safety record")
            assert result is True
    
    @pytest.mark.asyncio
    async def test_update_safety_score_invalid_range(self, safety_repository, mock_database):
        """Test safety score update with out-of-range values."""
        child_id = str(uuid4())
        
        # Test score below 0.0
        with pytest.raises(ValueError, match="Safety score must be between 0.0 and 1.0"):
            await safety_repository.update_safety_score(child_id, -0.1, "Invalid score")
        
        # Test score above 1.0
        with pytest.raises(ValueError, match="Safety score must be between 0.0 and 1.0"):
            await safety_repository.update_safety_score(child_id, 1.1, "Invalid score")
    
    @pytest.mark.asyncio
    async def test_update_safety_score_security_violation(self, safety_repository, mock_database):
        """Test safety score update with security violation."""
        # Arrange
        child_id = str(uuid4())
        
        with patch('src.infrastructure.persistence.repositories.safety_repository.validate_database_operation',
                  side_effect=SecurityError("Invalid input detected")):
            # Act & Assert
            with pytest.raises(ValueError, match="Invalid score data"):
                await safety_repository.update_safety_score(child_id, 0.5, "Test reason")


class TestSafetyEventRetrieval:
    """Test safety event retrieval functionality."""
    
    @pytest.mark.asyncio
    async def test_get_safety_events_success(self, safety_repository, mock_database):
        """Test successful safety event retrieval."""
        # Arrange
        child_id = str(uuid4())
        
        # Act
        events = await safety_repository.get_safety_events(child_id, limit=10)
        
        # Assert
        assert isinstance(events, list)
        assert len(events) <= 10
        for event in events:
            assert event["child_id"] == child_id
            assert "event_id" in event
            assert "event_type" in event
            assert "severity" in event
            assert "timestamp" in event
    
    @pytest.mark.asyncio
    async def test_get_safety_events_with_limit(self, safety_repository, mock_database):
        """Test safety event retrieval with custom limit."""
        # Arrange
        child_id = str(uuid4())
        
        # Act
        events = await safety_repository.get_safety_events(child_id, limit=2)
        
        # Assert
        assert len(events) <= 2
    
    @pytest.mark.asyncio
    async def test_get_safety_events_invalid_limit(self, safety_repository, mock_database):
        """Test safety event retrieval with invalid limit values."""
        child_id = str(uuid4())
        
        # Test zero limit
        with pytest.raises(ValueError, match="Limit must be between 1 and 1000"):
            await safety_repository.get_safety_events(child_id, limit=0)
        
        # Test negative limit
        with pytest.raises(ValueError, match="Limit must be between 1 and 1000"):
            await safety_repository.get_safety_events(child_id, limit=-1)
        
        # Test excessive limit
        with pytest.raises(ValueError, match="Limit must be between 1 and 1000"):
            await safety_repository.get_safety_events(child_id, limit=1001)
    
    @pytest.mark.asyncio
    async def test_get_safety_events_database_error(self, safety_repository, mock_database):
        """Test safety event retrieval with database error."""
        # Arrange
        child_id = str(uuid4())
        
        # Mock database error
        with patch.object(safety_repository, 'get_safety_events',
                         side_effect=RuntimeError("Database connection failed")):
            # Act & Assert
            with pytest.raises(RuntimeError):
                await safety_repository.get_safety_events(child_id)


class TestSafetyAlerts:
    """Test safety alert functionality."""
    
    @pytest.mark.asyncio
    async def test_send_safety_alert_success(self, safety_repository, mock_database):
        """Test successful safety alert sending."""
        # Arrange
        alert_data = {
            "child_id": str(uuid4()),
            "alert_type": "content_violation",
            "severity": "high",
            "message": "Multiple attempts to access inappropriate content detected"
        }
        
        with patch('src.infrastructure.persistence.repositories.safety_repository.validate_database_operation',
                  return_value={"data": alert_data}):
            # Act
            alert_id = await safety_repository.send_safety_alert(alert_data)
            
            # Assert
            assert alert_id is not None
            assert isinstance(alert_id, str)
    
    @pytest.mark.asyncio
    async def test_send_safety_alert_missing_fields(self, safety_repository, mock_database):
        """Test safety alert with missing required fields."""
        # Test missing child_id
        alert_data = {
            "alert_type": "test",
            "severity": "low",
            "message": "Test message"
        }
        with pytest.raises(ValueError, match="Missing required field: child_id"):
            await safety_repository.send_safety_alert(alert_data)
        
        # Test missing alert_type
        alert_data = {
            "child_id": str(uuid4()),
            "severity": "low",
            "message": "Test message"
        }
        with pytest.raises(ValueError, match="Missing required field: alert_type"):
            await safety_repository.send_safety_alert(alert_data)
        
        # Test missing severity
        alert_data = {
            "child_id": str(uuid4()),
            "alert_type": "test",
            "message": "Test message"
        }
        with pytest.raises(ValueError, match="Missing required field: severity"):
            await safety_repository.send_safety_alert(alert_data)
        
        # Test missing message
        alert_data = {
            "child_id": str(uuid4()),
            "alert_type": "test",
            "severity": "low"
        }
        with pytest.raises(ValueError, match="Missing required field: message"):
            await safety_repository.send_safety_alert(alert_data)
    
    @pytest.mark.asyncio
    async def test_send_safety_alert_critical_scenarios(self, safety_repository, mock_database):
        """Test safety alerts for critical child safety scenarios."""
        # Arrange
        critical_alerts = [
            {
                "child_id": str(uuid4()),
                "alert_type": "stranger_contact_attempt",
                "severity": "critical",
                "message": "Unknown adult attempted to initiate private conversation"
            },
            {
                "child_id": str(uuid4()),
                "alert_type": "personal_info_request",
                "severity": "high",
                "message": "AI detected attempt to extract personal information"
            },
            {
                "child_id": str(uuid4()),
                "alert_type": "bullying_detected",
                "severity": "high",
                "message": "Potential bullying language detected in conversation"
            }
        ]
        
        for alert_data in critical_alerts:
            with patch('src.infrastructure.persistence.repositories.safety_repository.validate_database_operation',
                      return_value={"data": alert_data}):
                # Act
                alert_id = await safety_repository.send_safety_alert(alert_data)
                
                # Assert
                assert alert_id is not None
    
    @pytest.mark.asyncio
    async def test_send_safety_alert_security_violation(self, safety_repository, mock_database):
        """Test safety alert with security violation."""
        # Arrange
        alert_data = {
            "child_id": "'; DELETE FROM alerts; --",
            "alert_type": "test",
            "severity": "low",
            "message": "Test"
        }
        
        with patch('src.infrastructure.persistence.repositories.safety_repository.validate_database_operation',
                  side_effect=SecurityError("SQL injection detected")):
            # Act & Assert
            with pytest.raises(ValueError, match="Invalid alert data"):
                await safety_repository.send_safety_alert(alert_data)


class TestSafetyRepositoryEdgeCases:
    """Test edge cases and boundary conditions."""
    
    @pytest.mark.asyncio
    async def test_record_multiple_concurrent_events(self, safety_repository, mock_database):
        """Test recording multiple safety events concurrently."""
        # Arrange
        child_id = str(uuid4())
        events = [
            ("content_filter", "Filtered word: violence", "medium"),
            ("time_limit_exceeded", "Daily limit reached", "low"),
            ("unsafe_interaction", "Suspicious conversation pattern", "high")
        ]
        
        event_ids = []
        for event_type, details, severity in events:
            with patch('src.infrastructure.persistence.repositories.safety_repository.validate_database_operation',
                      return_value={"data": {
                          "child_id": child_id,
                          "event_type": event_type,
                          "details": details,
                          "severity": severity
                      }}):
                event_id = await safety_repository.record_safety_event(
                    child_id, event_type, details, severity
                )
                event_ids.append(event_id)
        
        # Assert
        assert len(event_ids) == 3
        assert len(set(event_ids)) == 3  # All IDs should be unique
    
    @pytest.mark.asyncio
    async def test_safety_score_rapid_updates(self, safety_repository, mock_database):
        """Test rapid safety score updates (rate limiting scenario)."""
        # Arrange
        child_id = str(uuid4())
        scores = [0.9, 0.7, 0.5, 0.3, 0.1]  # Declining safety score
        
        for score in scores:
            with patch('src.infrastructure.persistence.repositories.safety_repository.validate_database_operation',
                      return_value={"data": {
                          "child_id": child_id,
                          "safety_score": score,
                          "reason": f"Score update to {score}",
                          "updated_at": datetime.utcnow()
                      }}):
                result = await safety_repository.update_safety_score(
                    child_id, score, f"Rapid decline test - score: {score}"
                )
                assert result is True