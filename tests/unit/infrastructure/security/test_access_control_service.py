"""
Tests for Access Control Service
Testing COPPA-compliant parent-child access control with comprehensive auditing.
"""

import pytest
from unittest.mock import patch
from datetime import datetime, timedelta
import asyncio

from src.infrastructure.security.access_control_service import (
    AccessControlService,
    AccessLevel,
    AccessAction,
)


class TestAccessControlService:
    """Test the Access Control Service."""

    @pytest.fixture
    def service(self):
        """Create an access control service instance."""
        return AccessControlService()

    def test_initialization(self, service):
        """Test service initialization."""
        assert isinstance(service, AccessControlService)
        assert hasattr(service, "parent_child_relationships")
        assert hasattr(service, "access_tokens")
        assert hasattr(service, "audit_logs")
        assert hasattr(service, "failed_access_attempts")
        assert hasattr(service, "access_permissions")
        assert isinstance(service.parent_child_relationships, dict)
        assert isinstance(service.access_tokens, dict)
        assert isinstance(service.audit_logs, list)
        assert isinstance(service.failed_access_attempts, dict)

    def test_access_level_enum_values(self):
        """Test AccessLevel enum values."""
        assert AccessLevel.FULL_PARENT.value == "full_parent"
        assert AccessLevel.SHARED_PARENT.value == "shared_parent"
        assert AccessLevel.TEMPORARY_GUARDIAN.value == "temporary_guardian"
        assert AccessLevel.READ_ONLY.value == "read_only"
        assert AccessLevel.EMERGENCY_CONTACT.value == "emergency_contact"

    def test_access_action_enum_values(self):
        """Test AccessAction enum values."""
        assert AccessAction.READ_PROFILE.value == "read_profile"
        assert AccessAction.UPDATE_PROFILE.value == "update_profile"
        assert AccessAction.DELETE_PROFILE.value == "delete_profile"
        assert AccessAction.READ_CONVERSATIONS.value == "read_conversations"
        assert (
            AccessAction.DELETE_CONVERSATIONS.value == "delete_conversations"
        )
        assert AccessAction.READ_ANALYTICS.value == "read_analytics"
        assert AccessAction.EXPORT_DATA.value == "export_data"
        assert AccessAction.MANAGE_SETTINGS.value == "manage_settings"
        assert AccessAction.GRANT_CONSENT.value == "grant_consent"
        assert AccessAction.REVOKE_CONSENT.value == "revoke_consent"

    def test_access_permissions_structure(self, service):
        """Test that access permissions are properly defined."""
        # Test that all access levels have defined permissions
        for access_level in AccessLevel:
            assert access_level in service.access_permissions
            assert isinstance(service.access_permissions[access_level], set)

        # Test permission hierarchies
        full_parent_perms = service.access_permissions[AccessLevel.FULL_PARENT]
        shared_parent_perms = service.access_permissions[
            AccessLevel.SHARED_PARENT
        ]
        temp_guardian_perms = service.access_permissions[
            AccessLevel.TEMPORARY_GUARDIAN
        ]
        read_only_perms = service.access_permissions[AccessLevel.READ_ONLY]
        emergency_perms = service.access_permissions[
            AccessLevel.EMERGENCY_CONTACT
        ]

        # Full parent should have most permissions
        assert len(full_parent_perms) >= len(shared_parent_perms)
        assert len(shared_parent_perms) >= len(temp_guardian_perms)
        assert len(temp_guardian_perms) >= len(read_only_perms)
        assert len(read_only_perms) >= len(emergency_perms)

        # Emergency contact should have minimal permissions
        assert emergency_perms == {AccessAction.READ_PROFILE}

    @pytest.mark.asyncio
    async def test_register_parent_child_relationship_success(self, service):
        """Test successful parent-child relationship registration."""
        parent_id = "parent_123"
        child_id = "child_456"
        access_level = AccessLevel.FULL_PARENT
        verification_method = "government_id_verification"

        result = await service.register_parent_child_relationship(
            parent_id, child_id, access_level, verification_method
        )

        assert "relationship_id" in result
        assert result["access_level"] == access_level.value
        assert "permissions" in result
        assert "expires_at" in result

        # Check that relationship was stored
        assert parent_id in service.parent_child_relationships
        relationships = service.parent_child_relationships[parent_id]
        assert len(relationships) == 1

        relationship = relationships[0]
        assert relationship["parent_id"] == parent_id
        assert relationship["child_id"] == child_id
        assert relationship["access_level"] == access_level.value
        assert relationship["verification_method"] == verification_method
        assert relationship["status"] == "active"
        assert relationship["verification_status"] == "verified"

    @pytest.mark.asyncio
    async def test_register_relationship_with_expiry(self, service):
        """Test registration with expiry date."""
        parent_id = "parent_expiry"
        child_id = "child_expiry"
        access_level = AccessLevel.TEMPORARY_GUARDIAN
        verification_method = "email_verification"
        expiry_date = datetime.utcnow() + timedelta(days=30)

        result = await service.register_parent_child_relationship(
            parent_id,
            child_id,
            access_level,
            verification_method,
            expiry_date=expiry_date,
        )

        assert result["expires_at"] is not None

        relationship = service.parent_child_relationships[parent_id][0]
        assert relationship["expires_at"] == expiry_date.isoformat()

    @pytest.mark.asyncio
    async def test_verify_access_success_full_parent(self, service):
        """Test successful access verification for full parent."""
        parent_id = "parent_full"
        child_id = "child_full"
        action = AccessAction.READ_PROFILE

        # Register relationship first
        await service.register_parent_child_relationship(
            parent_id, child_id, AccessLevel.FULL_PARENT, "government_id"
        )

        result = await service.verify_access(parent_id, child_id, action)

        assert result["access_granted"] is True
        assert "access_token" in result
        assert result["access_level"] == AccessLevel.FULL_PARENT.value
        assert "relationship_id" in result
        assert "expires_at" in result
        assert "permitted_actions" in result

    @pytest.mark.asyncio
    async def test_verify_access_no_relationship(self, service):
        """Test access verification when no relationship exists."""
        parent_id = "unknown_parent"
        child_id = "unknown_child"
        action = AccessAction.READ_PROFILE

        result = await service.verify_access(parent_id, child_id, action)

        assert result["access_granted"] is False
        assert result["reason"] == "No parent-child relationship found"
        assert result["error_code"] == "NO_RELATIONSHIP"

    @pytest.mark.asyncio
    async def test_verify_access_insufficient_permissions(self, service):
        """Test access verification with insufficient permissions."""
        parent_id = "parent_limited"
        child_id = "child_limited"
        action = AccessAction.DELETE_PROFILE  # Not allowed for READ_ONLY

        # Register relationship with limited access
        await service.register_parent_child_relationship(
            parent_id, child_id, AccessLevel.READ_ONLY, "email_verification"
        )

        result = await service.verify_access(parent_id, child_id, action)

        assert result["access_granted"] is False
        assert "insufficient" in result["reason"].lower()
        assert result["error_code"] == "INSUFFICIENT_PERMISSIONS"

    @pytest.mark.asyncio
    async def test_verify_access_expired_relationship(self, service):
        """Test access verification with expired relationship."""
        parent_id = "parent_expired"
        child_id = "child_expired"
        action = AccessAction.READ_PROFILE
        expired_date = datetime.utcnow() - timedelta(days=1)

        # Register expired relationship
        await service.register_parent_child_relationship(
            parent_id,
            child_id,
            AccessLevel.FULL_PARENT,
            "sms_verification",
            expiry_date=expired_date,
        )

        result = await service.verify_access(parent_id, child_id, action)

        assert result["access_granted"] is False
        assert "expired" in result["reason"].lower()
        assert result["error_code"] == "EXPIRED_RELATIONSHIP"

    @pytest.mark.asyncio
    async def test_access_token_generation_and_validation(self, service):
        """Test access token generation and validation."""
        parent_id = "parent_token"
        child_id = "child_token"
        action = AccessAction.UPDATE_PROFILE

        # Register relationship and get access
        await service.register_parent_child_relationship(
            parent_id, child_id, AccessLevel.FULL_PARENT, "government_id"
        )

        access_result = await service.verify_access(
            parent_id, child_id, action
        )
        token_id = access_result["access_token"]

        # Validate the token
        validation_result = await service.validate_access_token(
            token_id, parent_id, child_id, action
        )

        assert validation_result["valid"] is True
        assert (
            validation_result["access_level"] == AccessLevel.FULL_PARENT.value
        )
        assert "relationship_id" in validation_result

    @pytest.mark.asyncio
    async def test_access_token_validation_expired(self, service):
        """Test validation of expired access token."""
        parent_id = "parent_token_exp"
        child_id = "child_token_exp"
        action = AccessAction.READ_CONVERSATIONS

        # Manually create expired token
        token_id = "expired_token_123"
        service.access_tokens[token_id] = {
            "token_id": token_id,
            "parent_id": parent_id,
            "child_id": child_id,
            "action": action.value,
            "relationship_id": "rel_123",
            "access_level": "full_parent",
            "created_at": (datetime.utcnow() - timedelta(hours=2)).isoformat(),
            "expires_at": (datetime.utcnow() - timedelta(hours=1)).isoformat(),
            "used": False,
        }

        result = await service.validate_access_token(
            token_id, parent_id, child_id, action
        )

        assert result["valid"] is False
        assert result["reason"] == "Token expired"

    @pytest.mark.asyncio
    async def test_access_token_validation_mismatch(self, service):
        """Test validation with mismatched token parameters."""
        parent_id = "parent_mismatch"
        child_id = "child_mismatch"
        action = AccessAction.EXPORT_DATA
        wrong_action = AccessAction.DELETE_PROFILE

        # Register relationship and get token
        await service.register_parent_child_relationship(
            parent_id, child_id, AccessLevel.FULL_PARENT, "government_id"
        )

        access_result = await service.verify_access(
            parent_id, child_id, action
        )
        token_id = access_result["access_token"]

        # Try to validate with wrong action
        result = await service.validate_access_token(
            token_id, parent_id, child_id, wrong_action
        )

        assert result["valid"] is False
        assert result["reason"] == "Token mismatch"

    @pytest.mark.asyncio
    async def test_one_time_token_usage(self, service):
        """Test that destructive actions require one-time tokens."""
        parent_id = "parent_onetime"
        child_id = "child_onetime"
        action = AccessAction.DELETE_CONVERSATIONS

        # Register relationship and get token
        await service.register_parent_child_relationship(
            parent_id, child_id, AccessLevel.FULL_PARENT, "government_id"
        )

        access_result = await service.verify_access(
            parent_id, child_id, action
        )
        token_id = access_result["access_token"]

        # First validation should succeed
        result1 = await service.validate_access_token(
            token_id, parent_id, child_id, action
        )
        assert result1["valid"] is True

        # Second validation should fail (token used)
        result2 = await service.validate_access_token(
            token_id, parent_id, child_id, action
        )
        assert result2["valid"] is False
        assert result2["reason"] == "Token already used"

    @pytest.mark.asyncio
    async def test_audit_logging(self, service):
        """Test that audit events are properly logged."""
        parent_id = "parent_audit"
        child_id = "child_audit"

        initial_audit_count = len(service.audit_logs)

        # Register relationship (should generate audit log)
        await service.register_parent_child_relationship(
            parent_id,
            child_id,
            AccessLevel.SHARED_PARENT,
            "email_verification",
        )

        # Verify access (should generate audit log)
        await service.verify_access(
            parent_id, child_id, AccessAction.READ_PROFILE
        )

        # Should have at least 2 new audit entries
        assert len(service.audit_logs) >= initial_audit_count + 2

        # Check audit log structure
        latest_log = service.audit_logs[-1]
        assert "event_id" in latest_log
        assert "timestamp" in latest_log
        assert "parent_id" in latest_log
        assert "child_id" in latest_log
        assert "action" in latest_log
        assert "success" in latest_log

    @pytest.mark.asyncio
    async def test_failed_access_logging(self, service):
        """Test that failed access attempts are logged."""
        parent_id = "parent_failed"
        child_id = "child_failed"
        action = AccessAction.READ_PROFILE

        initial_failed_count = len(
            service.failed_access_attempts.get(parent_id, [])
        )

        # Attempt access without relationship
        await service.verify_access(parent_id, child_id, action)

        # Should log failed attempt
        assert parent_id in service.failed_access_attempts
        failed_attempts = service.failed_access_attempts[parent_id]
        assert len(failed_attempts) == initial_failed_count + 1

        latest_failure = failed_attempts[-1]
        assert latest_failure["child_id"] == child_id
        assert latest_failure["action"] == action.value
        assert latest_failure["reason"] == "no_relationship"

    @pytest.mark.asyncio
    async def test_suspicious_activity_detection(self, service):
        """Test detection of suspicious access patterns."""
        parent_id = "parent_suspicious"
        child_id = "child_suspicious"
        action = AccessAction.READ_PROFILE

        with patch(
            "src.infrastructure.security.access_control_service.logger"
        ) as mock_logger:
            # Generate multiple failed attempts
            for _ in range(6):
                await service.verify_access(parent_id, child_id, action)

            # Should trigger warning for suspicious activity
            mock_logger.warning.assert_called()
            warning_call = mock_logger.warning.call_args[0][0]
            assert "suspicious" in warning_call.lower()
            assert parent_id in warning_call

    @pytest.mark.asyncio
    async def test_get_parent_children_success(self, service):
        """Test getting children accessible by a parent."""
        parent_id = "parent_multiple"
        child_ids = ["child_1", "child_2", "child_3"]

        # Register multiple relationships
        for child_id in child_ids:
            await service.register_parent_child_relationship(
                parent_id, child_id, AccessLevel.FULL_PARENT, "government_id"
            )

        children = await service.get_parent_children(parent_id)

        assert len(children) == 3
        returned_child_ids = [child["child_id"] for child in children]
        assert set(returned_child_ids) == set(child_ids)

        for child in children:
            assert "access_level" in child
            assert "relationship_id" in child
            assert "expires_at" in child

    @pytest.mark.asyncio
    async def test_get_parent_children_no_relationships(self, service):
        """Test getting children when no relationships exist."""
        parent_id = "parent_no_children"

        children = await service.get_parent_children(parent_id)

        assert children == []

    @pytest.mark.asyncio
    async def test_get_parent_children_excludes_expired(self, service):
        """Test that expired relationships are excluded."""
        parent_id = "parent_expired_children"

        # Add active relationship
        await service.register_parent_child_relationship(
            parent_id, "active_child", AccessLevel.FULL_PARENT, "government_id"
        )

        # Add expired relationship
        expired_date = datetime.utcnow() - timedelta(days=1)
        await service.register_parent_child_relationship(
            parent_id,
            "expired_child",
            AccessLevel.FULL_PARENT,
            "government_id",
            expiry_date=expired_date,
        )

        children = await service.get_parent_children(parent_id)

        # Should only return active child
        assert len(children) == 1
        assert children[0]["child_id"] == "active_child"

    @pytest.mark.asyncio
    async def test_different_access_levels_permissions(self, service):
        """Test that different access levels have appropriate permissions."""
        parent_id = "parent_levels"
        child_id = "child_levels"

        test_cases = [
            (AccessLevel.FULL_PARENT, AccessAction.DELETE_PROFILE, True),
            (AccessLevel.SHARED_PARENT, AccessAction.DELETE_PROFILE, False),
            (AccessLevel.SHARED_PARENT, AccessAction.GRANT_CONSENT, True),
            (
                AccessLevel.TEMPORARY_GUARDIAN,
                AccessAction.GRANT_CONSENT,
                False,
            ),
            (
                AccessLevel.TEMPORARY_GUARDIAN,
                AccessAction.READ_CONVERSATIONS,
                True,
            ),
            (AccessLevel.READ_ONLY, AccessAction.UPDATE_PROFILE, False),
            (AccessLevel.READ_ONLY, AccessAction.READ_ANALYTICS, True),
            (
                AccessLevel.EMERGENCY_CONTACT,
                AccessAction.READ_ANALYTICS,
                False,
            ),
            (AccessLevel.EMERGENCY_CONTACT, AccessAction.READ_PROFILE, True),
        ]

        for access_level, action, should_succeed in test_cases:
            # Clear previous relationships
            service.parent_child_relationships.clear()

            # Register with specific access level
            await service.register_parent_child_relationship(
                parent_id, child_id, access_level, "government_id"
            )

            # Verify access
            result = await service.verify_access(parent_id, child_id, action)

            if should_succeed:
                assert (
                    result["access_granted"] is True
                ), f"{access_level.value} should allow {action.value}"
            else:
                assert (
                    result["access_granted"] is False
                ), f"{access_level.value} should NOT allow {action.value}"
                assert result["error_code"] == "INSUFFICIENT_PERMISSIONS"

    @pytest.mark.asyncio
    async def test_multiple_parents_same_child(self, service):
        """Test multiple parents with access to same child."""
        child_id = "shared_child"
        parent1_id = "primary_parent"
        parent2_id = "secondary_parent"

        # Register both parents
        await service.register_parent_child_relationship(
            parent1_id, child_id, AccessLevel.FULL_PARENT, "government_id"
        )
        await service.register_parent_child_relationship(
            parent2_id, child_id, AccessLevel.SHARED_PARENT, "court_order"
        )

        # Both should be able to read profile
        result1 = await service.verify_access(
            parent1_id, child_id, AccessAction.READ_PROFILE
        )
        result2 = await service.verify_access(
            parent2_id, child_id, AccessAction.READ_PROFILE
        )

        assert result1["access_granted"] is True
        assert result2["access_granted"] is True

        # Only primary parent should be able to delete
        delete_result1 = await service.verify_access(
            parent1_id, child_id, AccessAction.DELETE_PROFILE
        )
        delete_result2 = await service.verify_access(
            parent2_id, child_id, AccessAction.DELETE_PROFILE
        )

        assert delete_result1["access_granted"] is True
        assert delete_result2["access_granted"] is False

    @pytest.mark.asyncio
    async def test_concurrent_access_verification(self, service):
        """Test concurrent access verification operations."""
        parent_id = "concurrent_parent"
        child_ids = ["child_1", "child_2", "child_3", "child_4"]

        # Register relationships for all children
        for child_id in child_ids:
            await service.register_parent_child_relationship(
                parent_id, child_id, AccessLevel.FULL_PARENT, "government_id"
            )

        # Verify access concurrently
        tasks = [
            service.verify_access(
                parent_id, child_id, AccessAction.READ_PROFILE
            )
            for child_id in child_ids
        ]

        results = await asyncio.gather(*tasks)

        # All should succeed
        assert len(results) == 4
        assert all(r["access_granted"] for r in results)

        # All should have unique access tokens
        tokens = [r["access_token"] for r in results]
        assert len(set(tokens)) == 4

    @pytest.mark.asyncio
    async def test_coppa_compliance_audit_trail(self, service):
        """Test that comprehensive audit trails are maintained for COPPA compliance."""
        parent_id = "coppa_parent"
        child_id = "coppa_child_under_13"

        # Register relationship
        reg_result = await service.register_parent_child_relationship(
            parent_id,
            child_id,
            AccessLevel.FULL_PARENT,
            "government_id_verification",
            legal_document_id="birth_cert_123",
        )

        # Perform various actions
        actions = [
            AccessAction.READ_PROFILE,
            AccessAction.GRANT_CONSENT,
            AccessAction.READ_CONVERSATIONS,
            AccessAction.EXPORT_DATA,
        ]

        for action in actions:
            await service.verify_access(parent_id, child_id, action)

        # Verify comprehensive audit trail
        relevant_audits = [
            log
            for log in service.audit_logs
            if log["parent_id"] == parent_id and log["child_id"] == child_id
        ]

        # Should have registration + access verifications
        assert len(relevant_audits) >= len(actions) + 1

        # Check audit completeness
        for audit in relevant_audits:
            assert all(
                key in audit
                for key in [
                    "event_id",
                    "timestamp",
                    "parent_id",
                    "child_id",
                    "action",
                    "access_level",
                    "success",
                    "details",
                ]
            )
            assert audit["parent_id"] == parent_id
            assert audit["child_id"] == child_id

    @pytest.mark.asyncio
    async def test_relationship_status_management(self, service):
        """Test relationship status management."""
        parent_id = "status_parent"
        child_id = "status_child"

        # Register active relationship
        await service.register_parent_child_relationship(
            parent_id, child_id, AccessLevel.FULL_PARENT, "government_id"
        )

        relationship = service.parent_child_relationships[parent_id][0]
        assert relationship["status"] == "active"

        # Manually set to inactive for testing
        relationship["status"] = "inactive"

        # Should fail access verification
        result = await service.verify_access(
            parent_id, child_id, AccessAction.READ_PROFILE
        )

        assert result["access_granted"] is False
        assert result["error_code"] == "INACTIVE_RELATIONSHIP"

    @pytest.mark.asyncio
    async def test_error_handling_system_errors(self, service):
        """Test error handling for system errors."""
        parent_id = "error_parent"
        child_id = "error_child"
        action = AccessAction.READ_PROFILE

        # Mock a system error in relationship finding
        with patch.object(
            service,
            "_find_relationship",
            side_effect=Exception("System error"),
        ):
            result = await service.verify_access(parent_id, child_id, action)

            assert result["access_granted"] is False
            assert result["error_code"] == "SYSTEM_ERROR"
            assert "system error" in result["reason"].lower()

    def test_edge_cases_invalid_inputs(self, service):
        """Test handling of invalid inputs."""
        # Test with None values
        with pytest.raises((TypeError, AttributeError)):
            asyncio.run(
                service.register_parent_child_relationship(
                    None, "child_123", AccessLevel.FULL_PARENT, "method"
                )
            )

        # Test with empty strings
        with pytest.raises((ValueError, Exception)):
            asyncio.run(
                service.register_parent_child_relationship(
                    "", "child_123", AccessLevel.FULL_PARENT, "method"
                )
            )

    @pytest.mark.asyncio
    async def test_token_cleanup_and_management(self, service):
        """Test that tokens are properly managed and cleaned up."""
        parent_id = "token_cleanup_parent"
        child_id = "token_cleanup_child"

        # Register relationship
        await service.register_parent_child_relationship(
            parent_id, child_id, AccessLevel.FULL_PARENT, "government_id"
        )

        # Generate multiple tokens
        tokens = []
        for _ in range(5):
            result = await service.verify_access(
                parent_id, child_id, AccessAction.READ_PROFILE
            )
            tokens.append(result["access_token"])

        # All tokens should be stored
        assert len(service.access_tokens) >= 5

        # All tokens should be valid initially
        for token in tokens:
            validation = await service.validate_access_token(
                token, parent_id, child_id, AccessAction.READ_PROFILE
            )
            assert validation["valid"] is True
