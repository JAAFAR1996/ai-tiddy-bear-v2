"""Unit Tests for Unified Security Service"""

from datetime import datetime, timedelta

import pytest

from src.infrastructure.security.unified_security_service import (
    SecurityConfig,
    UnifiedSecurityService,
)


@pytest.mark.unit
class TestUnifiedSecurityService:
    """Test unified security service functionality"""

    @pytest.fixture
    def security_config(self):
        """Security configuration for tests"""
        return SecurityConfig(
            max_login_attempts=3,
            lockout_duration=timedelta(minutes=15),
            dangerous_patterns=["<script>", "drop table", "exec("],
        )

    @pytest.fixture
    def security_service(self, security_config):
        """Security service instance"""
        return UnifiedSecurityService(security_config)

    # ==================== Threat Detection Tests ====================

    @pytest.mark.asyncio
    async def test_analyze_threat_no_threat(self, security_service):
        """Test threat analysis with safe content"""
        result = await security_service.analyze_threat(
            "Hello, how are you today?", "192.168.1.1"
        )

        assert result["threat_detected"] is False
        assert result["threat_types"] == []
        assert result["severity"] == "low"
        assert result["action_taken"] == "none"

    @pytest.mark.asyncio
    async def test_analyze_threat_dangerous_pattern(self, security_service):
        """Test threat analysis with dangerous pattern"""
        result = await security_service.analyze_threat(
            "Some text with <script>alert('xss')</script>", "192.168.1.1"
        )

        assert result["threat_detected"] is True
        assert any("Dangerous pattern: <script>" in t for t in result["threat_types"])
        assert result["severity"] == "high"

    @pytest.mark.asyncio
    async def test_analyze_threat_sql_injection(self, security_service):
        """Test threat analysis with SQL injection attempt"""
        result = await security_service.analyze_threat(
            "'; DROP TABLE users; --", "192.168.1.1"
        )

        assert result["threat_detected"] is True
        assert "SQL injection attempt" in result["threat_types"]
        assert result["severity"] == "critical"
        assert result["action_taken"] == "blocked"

    @pytest.mark.asyncio
    async def test_analyze_threat_blocks_critical_ip(self, security_service):
        """Test that critical threats block IP"""
        ip = "192.168.1.100"

        # Trigger critical threat
        await security_service.analyze_threat("'; DROP TABLE users; --", ip)

        # Check IP is blocked
        assert ip in security_service.blocked_ips
        assert security_service.blocked_ips[ip] > datetime.utcnow()

    # ==================== Access Control Tests ====================

    @pytest.mark.asyncio
    async def test_validate_login_attempt_allowed(self, security_service):
        """Test login validation when allowed"""
        result = await security_service.validate_login_attempt("user123", "192.168.1.1")

        assert result["allowed"] is True

    @pytest.mark.asyncio
    async def test_validate_login_attempt_blocked_ip(self, security_service):
        """Test login validation with blocked IP"""
        ip = "192.168.1.1"
        block_until = datetime.utcnow() + timedelta(minutes=30)
        security_service.blocked_ips[ip] = block_until

        result = await security_service.validate_login_attempt("user123", ip)

        assert result["allowed"] is False
        assert result["reason"] == "IP temporarily blocked"
        assert "block_until" in result

    @pytest.mark.asyncio
    async def test_validate_login_attempt_too_many_failures(self, security_service):
        """Test login validation with too many failed attempts"""
        user_id = "user123"

        # Record multiple failed attempts
        for _ in range(3):
            await security_service.record_failed_login(user_id, "192.168.1.1")

        result = await security_service.validate_login_attempt(user_id, "192.168.1.1")

        assert result["allowed"] is False
        assert result["reason"] == "Too many failed attempts"
        assert "retry_after" in result

    @pytest.mark.asyncio
    async def test_record_failed_login_creates_audit_log(self, security_service):
        """Test that failed login creates audit log"""
        user_id = "user123"
        ip = "192.168.1.1"

        await security_service.record_failed_login(user_id, ip)

        assert len(security_service.audit_entries) > 0
        last_audit = security_service.audit_entries[-1]
        assert last_audit["event"] == "failed_login"
        assert last_audit["user_id"] == user_id
        assert last_audit["ip_address"] == ip

    # ==================== File Security Tests ====================

    def test_validate_audio_file_valid(self, security_service):
        """Test audio file validation with valid file"""
        result = security_service.validate_audio_file(
            "test_audio.wav", b"RIFF" + b"\x00" * 100
        )

        assert result["is_valid"] is True
        assert result["errors"] == []
        assert result["file_info"]["file_type"] == "wav"

    def test_validate_audio_file_empty(self, security_service):
        """Test audio file validation with empty file"""
        result = security_service.validate_audio_file("test.wav", b"")

        assert result["is_valid"] is False
        assert "File is empty" in result["errors"]

    def test_validate_audio_file_too_large(self, security_service):
        """Test audio file validation with oversized file"""
        large_content = b"X" * (11 * 1024 * 1024)  # 11MB
        result = security_service.validate_audio_file("test.wav", large_content)

        assert result["is_valid"] is False
        assert any("size exceeds maximum" in e for e in result["errors"])

    def test_validate_audio_file_wrong_extension(self, security_service):
        """Test audio file validation with wrong extension"""
        result = security_service.validate_audio_file("test.exe", b"MZ")  # EXE header

        assert result["is_valid"] is False
        assert any("not allowed" in e for e in result["errors"])

    def test_sanitize_filename(self, security_service):
        """Test filename sanitization"""
        dangerous_filename = "../../../etc/passwd"
        safe_filename = security_service.sanitize_filename(dangerous_filename)

        assert safe_filename == "passwd"
        assert ".." not in safe_filename
        assert "/" not in safe_filename

    # ==================== Utility Method Tests ====================

    def test_generate_secure_token(self, security_service):
        """Test secure token generation"""
        token1 = security_service.generate_secure_token()
        token2 = security_service.generate_secure_token()

        assert len(token1) >= 32
        assert token1 != token2  # Should be unique
        assert isinstance(token1, str)

    def test_hash_password(self, security_service):
        """Test password hashing"""
        password = "test_password_123"
        hashed, salt = security_service.hash_password(password)

        assert hashed != password
        assert len(hashed) > 0
        assert len(salt) == 32  # Default salt size

    def test_verify_password_correct(self, security_service):
        """Test password verification with correct password"""
        password = "test_password_123"
        hashed, salt = security_service.hash_password(password)

        assert security_service.verify_password(password, hashed, salt) is True

    def test_verify_password_incorrect(self, security_service):
        """Test password verification with incorrect password"""
        password = "test_password_123"
        hashed, salt = security_service.hash_password(password)

        assert security_service.verify_password("wrong_password", hashed, salt) is False

    # ==================== Security Status Tests ====================

    def test_get_security_status(self, security_service):
        """Test security status reporting"""
        # Add some test data
        security_service.blocked_ips["192.168.1.1"] = datetime.utcnow() + timedelta(
            hours=1
        )
        security_service.threats.append(
            {"timestamp": datetime.utcnow().isoformat(), "severity": "high"}
        )

        status = security_service.get_security_status()

        assert status["active_blocks"] == 1
        assert status["recent_threats"] >= 1
        assert "failed_login_tracking" in status
        assert "audit_entries" in status


@pytest.mark.unit
@pytest.mark.child_safety
class TestUnifiedSecurityServiceChildSafety:
    """Test child safety specific security features"""

    @pytest.fixture
    def child_safety_config(self):
        """Child safety focused configuration"""
        return SecurityConfig(
            dangerous_patterns=[
                "violence",
                "scary",
                "inappropriate",
                "adult",
                "mature",
                "death",
            ],
            allowed_audio_types=["wav", "mp3"],
            max_file_size=5 * 1024 * 1024,  # 5MB for children
        )

    @pytest.fixture
    def child_safety_service(self, child_safety_config):
        """Child safety focused security service"""
        return UnifiedSecurityService(child_safety_config)

    @pytest.mark.asyncio
    async def test_analyze_threat_child_unsafe_content(self, child_safety_service):
        """Test detection of child-unsafe content"""
        result = await child_safety_service.analyze_threat(
            "This story contains violence and scary content", "192.168.1.1"
        )

        assert result["threat_detected"] is True
        assert any("violence" in t for t in result["threat_types"])
        assert result["severity"] == "high"

    @pytest.mark.asyncio
    async def test_child_audio_file_size_limit(self, child_safety_service):
        """Test stricter file size limits for children"""
        large_content = b"X" * (6 * 1024 * 1024)  # 6MB
        result = child_safety_service.validate_audio_file("test.wav", large_content)

        assert result["is_valid"] is False
        assert any("size exceeds maximum" in e for e in result["errors"])
