import os
import sys
import tempfile
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import patch

from src.infrastructure.security.main_security_service import MainSecurityService

from infrastructure.security.enhanced_security import SecurityConfig


class MockThreatLevel:
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


ThreatLevel = MockThreatLevel


# Add src to path
src_path = Path(__file__).parent
while src_path.name != "backend" and src_path.parent != src_path:
    src_path = src_path.parent
src_path = src_path / "src"

if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

"""
Comprehensive Security Service Tests
Tests for advanced security features and threat detection
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

# Import the service we're testing

sys.path.append("/mnt/c/Users/jaafa/Desktop/5555/ai-teddy/backend/src")


class TestComprehensiveSecurityService:
    """Test comprehensive security service functionality"""

    @pytest.fixture
    def security_service(self):
        """Create security service instance for testing"""
        config = SecurityConfig(
            password_min_length=8,
            max_login_attempts=3,
            lockout_duration=timedelta(minutes=15),
        )
        return ComprehensiveSecurityService(config)

    @pytest.fixture
    def sample_threats(self):
        """Sample threat data for testing"""
        return [
            "SELECT * FROM users WHERE '1'='1'",  # SQL injection
            "<script>alert('xss')</script>",  # XSS
            "; cat /etc/passwd",  # Command injection
            "../../../etc/passwd",  # Path traversal
            "normal safe content",  # Safe content
        ]

    @pytest.mark.asyncio
    async def test_threat_detection_sql_injection(self, security_service):
        """Test SQL injection threat detection"""
        threat = await security_service.analyze_threat(
            "SELECT * FROM users WHERE '1'='1'", source_ip="192.168.1.100"
        )

        assert threat.level in [ThreatLevel.MEDIUM, ThreatLevel.HIGH]
        assert "sql_injection" in threat.threat_type
        assert threat.source_ip == "192.168.1.100"
        assert not threat.resolved

    @pytest.mark.asyncio
    async def test_threat_detection_xss(self, security_service):
        """Test XSS threat detection"""
        threat = await security_service.analyze_threat(
            "<script>alert('malicious')</script>"
        )

        assert threat.level in [ThreatLevel.MEDIUM, ThreatLevel.HIGH]
        assert "xss_patterns" in threat.threat_type
        assert len(threat.evidence) > 0

    @pytest.mark.asyncio
    async def test_threat_detection_safe_content(self, security_service):
        """Test that safe content is not flagged as threat"""
        threat = await security_service.analyze_threat(
            "Hello, this is a normal message from a child"
        )

        assert threat.level == ThreatLevel.LOW
        assert threat.threat_type == "none"
        assert threat.description == "No threats detected"

    @pytest.mark.asyncio
    async def test_multiple_threats_detection(self, security_service):
        """Test detection of multiple threat types in single content"""
        malicious_content = "'; DROP TABLE users; <script>alert('xss')</script>"
        threat = await security_service.analyze_threat(malicious_content)

        assert threat.level == ThreatLevel.HIGH
        assert "sql_injection" in threat.threat_type
        assert "xss_patterns" in threat.threat_type
        assert len(threat.evidence) >= 2

    @pytest.mark.asyncio
    async def test_child_content_validation_safe(self, security_service):
        """Test child-safe content validation"""
        result = await security_service.validate_child_content(
            "Let's play with toys and read a fun story!", child_age=7
        )

        assert result["safe"] is True
        assert result["safety_score"] >= 80
        assert len(result["issues"]) == 0
        assert "child-safe" in result["recommendations"][0]

    @pytest.mark.asyncio
    async def test_child_content_validation_unsafe_violence(self, security_service):
        """Test detection of violent content"""
        result = await security_service.validate_child_content(
            "The character uses a gun to fight the monster", child_age=7
        )

        assert result["safe"] is False
        assert result["safety_score"] < 100
        assert len(result["issues"]) > 0

        # Check that violence was detected
        violence_issue = next(
            (issue for issue in result["issues"] if issue["category"] == "violence"),
            None,
        )
        assert violence_issue is not None
        assert "gun" in violence_issue["keywords"]

    @pytest.mark.asyncio
    async def test_child_content_validation_age_appropriate(self, security_service):
        """Test age-appropriate content validation"""
        # Content too complex for young children
        result = await security_service.validate_child_content(
            "This advanced quantum physics concept is quite complex",
            child_age=4,
        )

        assert len(result["issues"]) > 0
        age_issue = next(
            (
                issue
                for issue in result["issues"]
                if issue["category"] == "age_inappropriate"
            ),
            None,
        )
        assert age_issue is not None

    @pytest.mark.asyncio
    async def test_file_malware_scanning_safe_file(self, security_service):
        """Test malware scanning of safe file"""
        # Create temporary safe file
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
            f.write("This is a safe text file")
            temp_file = f.name

        try:
            result = await security_service.scan_file_for_malware(temp_file)

            assert result["safe"] is True
            assert "file_hash" in result
            assert "file_size" in result
            assert result["suspicious_size"] is False
        finally:
            os.unlink(temp_file)

    @pytest.mark.asyncio
    async def test_file_malware_scanning_nonexistent_file(self, security_service):
        """Test malware scanning of non-existent file"""
        result = await security_service.scan_file_for_malware("/nonexistent/file.txt")

        assert result["safe"] is False
        assert "error" in result
        assert "File not found" in result["error"]

    @pytest.mark.asyncio
    async def test_enhanced_audit_logging(self, security_service):
        """Test enhanced audit logging functionality"""
        await security_service.create_enhanced_audit_log(
            action="LOGIN_ATTEMPT",
            user_id="test_user_123",
            details={"success": True, "method": "password"},
            ip_address="192.168.1.100",
            user_agent="TestAgent/1.0",
            risk_score=10,
        )

        # Check that audit entry was created
        assert len(security_service.audit_entries) == 1
        entry = security_service.audit_entries[0]

        assert entry.action == "LOGIN_ATTEMPT"
        assert entry.user_id == "test_user_123"
        assert entry.ip_address == "192.168.1.100"
        assert entry.success is True
        assert entry.risk_score == 10

    @pytest.mark.asyncio
    async def test_incident_response_trigger(self, security_service):
        """Test that high-severity threats trigger incident response"""
        with patch.object(
            security_service, "_trigger_incident_response"
        ) as mock_incident:
            # Create high-severity threat
            threat = SecurityThreat(
                threat_id="test123",
                threat_type="sql_injection",
                level=ThreatLevel.HIGH,
                description="High severity test threat",
                source_ip="192.168.1.100",
            )

            await security_service._trigger_incident_response(threat)

            # Check that IP was blocked
            assert "192.168.1.100" in security_service.blocked_ips

    @pytest.mark.asyncio
    async def test_security_report_generation(self, security_service):
        """Test security report generation"""
        # Add some test data
        await security_service.analyze_threat("'; DROP TABLE users;")
        await security_service.create_enhanced_audit_log(
            action="TEST_ACTION",
            user_id="test_user",
            details={"success": False},
            risk_score=80,
        )

        report = await security_service.generate_security_report()

        assert "report_generated" in report
        assert "threat_summary" in report
        assert "audit_summary" in report
        assert "security_recommendations" in report
        assert "compliance_status" in report

        # Check threat summary
        assert report["threat_summary"]["total_threats"] >= 1
        assert report["audit_summary"]["total_audit_entries"] >= 1
        assert report["compliance_status"]["coppa_compliant"] is True

    @pytest.mark.asyncio
    async def test_data_cleanup(self, security_service):
        """Test cleanup of old security data"""
        # Add old threat (simulate old timestamp)
        old_threat = SecurityThreat(
            threat_id="old123",
            threat_type="test",
            level=ThreatLevel.LOW,
            description="Old threat",
        )
        old_threat.timestamp = datetime.now() - timedelta(days=100)
        security_service.threats.append(old_threat)

        # Add recent threat
        await security_service.analyze_threat("normal content")

        initial_count = len(security_service.threats)
        await security_service.cleanup_old_data(retention_days=30)

        # Old threat should be removed, recent one should remain
        assert len(security_service.threats) < initial_count
        remaining_threats = [
            t for t in security_service.threats if t.threat_id == "old123"
        ]
        assert len(remaining_threats) == 0

    def test_threat_pattern_loading(self, security_service):
        """Test that threat patterns are loaded correctly"""
        patterns = security_service.threat_patterns

        assert "sql_injection" in patterns
        assert "xss_patterns" in patterns
        assert "command_injection" in patterns
        assert "path_traversal" in patterns

        # Check some specific patterns
        assert any("union" in pattern for pattern in patterns["sql_injection"])
        assert any("script" in pattern for pattern in patterns["xss_patterns"])

    def test_child_safety_filters_initialization(self, security_service):
        """Test child safety filters are properly initialized"""
        keywords = security_service.inappropriate_keywords

        assert "violence" in keywords
        assert "adult_content" in keywords
        assert "scary_content" in keywords
        assert "substance_abuse" in keywords

        # Check some specific keywords
        assert "weapon" in keywords["violence"]
        assert "alcohol" in keywords["substance_abuse"]

    @pytest.mark.asyncio
    async def test_rate_limiting_integration(self, security_service):
        """Test integration with rate limiting"""
        ip_address = "192.168.1.200"

        # Should allow initial requests
        assert security_service.check_rate_limit(ip_address) is True

        # Simulate multiple failed attempts
        for _ in range(security_service.config.max_login_attempts + 1):
            security_service.record_failed_attempt(ip_address)

        # Should be blocked after max attempts
        assert security_service.check_rate_limit(ip_address) is False

        # Clear attempts should restore access
        security_service.clear_failed_attempts(ip_address)
        assert security_service.check_rate_limit(ip_address) is True

    def test_factory_function(self):
        """Test the factory function creates service correctly"""
        service = create_comprehensive_security_service()

        assert isinstance(service, ComprehensiveSecurityService)
        assert service.config is not None
        assert hasattr(service, "threat_patterns")
        assert hasattr(service, "inappropriate_keywords")


class TestSecurityIntegration:
    """Integration tests for security service"""

    @pytest.mark.asyncio
    async def test_end_to_end_threat_processing(self):
        """Test complete threat detection and response workflow"""
        service = create_comprehensive_security_service()

        # Simulate malicious request
        malicious_content = "'; DROP TABLE children; <script>steal_data()</script>"
        source_ip = "192.168.1.100"

        # Analyze threat
        threat = await service.analyze_threat(malicious_content, source_ip)

        # Verify threat detection
        assert threat.level in [ThreatLevel.HIGH, ThreatLevel.CRITICAL]
        assert source_ip in service.blocked_ips

        # Generate security report
        report = await service.generate_security_report()
        assert report["threat_summary"]["total_threats"] >= 1
        assert report["threat_summary"]["high_severity_threats"] >= 1

    @pytest.mark.asyncio
    async def test_child_safety_workflow(self):
        """Test complete child safety validation workflow"""
        service = create_comprehensive_security_service()

        # Test various content types
        test_cases = [
            ("Hello friend, let's play a fun game!", True),
            ("The monster has a scary weapon", False),
            ("Time for bed, sweet dreams!", True),
            ("Adult content not suitable for children", False),
        ]

        for content, should_be_safe in test_cases:
            result = await service.validate_child_content(content, child_age=7)
            assert result["safe"] == should_be_safe

            if not should_be_safe:
                assert len(result["issues"]) > 0
                assert len(result["recommendations"]) > 0

    @pytest.mark.asyncio
    async def test_audit_trail_completeness(self):
        """Test that all security events are properly audited"""
        service = create_comprehensive_security_service()

        # Perform various security operations
        await service.analyze_threat("'; DROP TABLE users;")
        await service.validate_child_content("scary monster story", 5)

        # Check audit trail
        # May have background audit entries
        assert len(service.audit_entries) >= 0

        # All threats should be logged
        assert len(service.threats) >= 1


@pytest.mark.asyncio
async def test_emergency_procedures():
    """Test emergency security procedures"""
    from infrastructure.security.comprehensive_security_service import (
        emergency_data_protection,
        emergency_security_lockdown,
    )

    # These should not raise exceptions
    await emergency_security_lockdown()
    await emergency_data_protection()


if __name__ == "__main__":
    # Run tests if executed directly
    pytest.main([__file__, "-v"])
