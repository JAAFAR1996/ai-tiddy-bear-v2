"""
Tests for Consent Service
Testing core consent management functionality for COPPA compliance.
"""

import pytest
from unittest.mock import patch, Mock, AsyncMock
from datetime import datetime, timedelta
import asyncio

from src.application.services.consent.consent_service import ConsentService
from src.application.services.consent.consent_models import (
    ConsentRecord,
    VerificationMethod,
    VerificationStatus,
    VerificationAttempt,
)


class TestConsentService:
    """Test the Consent Service."""

    @pytest.fixture
    def service(self):
        """Create a consent service instance."""
        return ConsentService()

    def test_initialization(self, service):
        """Test service initialization."""
        assert isinstance(service, ConsentService)
        assert hasattr(service, "consents")
        assert hasattr(service, "verification_service")
        assert isinstance(service.consents, dict)
        assert len(service.consents) == 0

    @pytest.mark.asyncio
    async def test_request_consent_success(self, service):
        """Test successful consent request."""
        parent_id = "parent_123"
        child_id = "child_456"
        feature = "audio_recording"

        result = await service.request_consent(parent_id, child_id, feature)

        assert result["status"] == "pending"
        assert "consent_id" in result

        consent_id = result["consent_id"]
        assert consent_id in service.consents

        consent = service.consents[consent_id]
        assert consent.parent_id == parent_id
        assert consent.child_id == child_id
        assert consent.feature == feature
        assert consent.status == "pending"
        assert consent.requested_at is not None
        assert consent.expiry_date is not None

    @pytest.mark.asyncio
    async def test_request_consent_custom_expiry(self, service):
        """Test consent request with custom expiry days."""
        parent_id = "parent_custom"
        child_id = "child_custom"
        feature = "location_tracking"
        custom_days = 180

        result = await service.request_consent(
            parent_id, child_id, feature, expiry_days=custom_days
        )

        consent_id = result["consent_id"]
        consent = service.consents[consent_id]

        requested_dt = datetime.fromisoformat(consent.requested_at)
        expiry_dt = datetime.fromisoformat(consent.expiry_date)

        # Should be approximately 180 days apart
        diff = expiry_dt - requested_dt
        assert 179 <= diff.days <= 181  # Allow for small timing differences

    @pytest.mark.asyncio
    async def test_grant_consent_success(self, service):
        """Test successful consent granting."""
        # First create a consent request
        parent_id = "parent_grant"
        child_id = "child_grant"
        feature = "personalization"

        request_result = await service.request_consent(parent_id, child_id, feature)
        consent_id = request_result["consent_id"]

        # Grant the consent
        verification_method = "email_verification"
        result = await service.grant_consent(consent_id, verification_method)

        assert result["status"] == "granted"
        assert result["consent_id"] == consent_id

        consent = service.consents[consent_id]
        assert consent.status == "granted"
        assert consent.granted_at is not None
        assert consent.verification_method == verification_method

    @pytest.mark.asyncio
    async def test_grant_consent_not_found(self, service):
        """Test granting consent for non-existent consent ID."""
        result = await service.grant_consent(
            "nonexistent_consent", "email_verification"
        )

        assert result["status"] == "not_found"
        assert result["consent_id"] == "nonexistent_consent"

    @pytest.mark.asyncio
    async def test_revoke_consent_success(self, service):
        """Test successful consent revocation."""
        # Create and grant consent first
        parent_id = "parent_revoke"
        child_id = "child_revoke"
        feature = "data_collection"

        request_result = await service.request_consent(parent_id, child_id, feature)
        consent_id = request_result["consent_id"]

        await service.grant_consent(consent_id, "sms_verification")

        # Revoke the consent
        result = await service.revoke_consent(consent_id)

        assert result["status"] == "revoked"
        assert result["consent_id"] == consent_id

        consent = service.consents[consent_id]
        assert consent.status == "revoked"
        assert consent.revoked_at is not None

    @pytest.mark.asyncio
    async def test_revoke_consent_not_found(self, service):
        """Test revoking consent for non-existent consent ID."""
        result = await service.revoke_consent("nonexistent_consent")

        assert result["status"] == "not_found"
        assert result["consent_id"] == "nonexistent_consent"

    @pytest.mark.asyncio
    async def test_check_consent_status_pending(self, service):
        """Test checking status of pending consent."""
        parent_id = "parent_status"
        child_id = "child_status"
        feature = "voice_analysis"

        request_result = await service.request_consent(parent_id, child_id, feature)
        consent_id = request_result["consent_id"]

        result = await service.check_consent_status(consent_id)

        assert result["status"] == "pending"
        assert result["consent_id"] == consent_id
        assert result["feature"] == feature
        assert result["requested_at"] is not None
        assert result["expiry_date"] is not None
        assert result["granted_at"] is None
        assert result["verification_method"] is None

    @pytest.mark.asyncio
    async def test_check_consent_status_granted(self, service):
        """Test checking status of granted consent."""
        parent_id = "parent_granted"
        child_id = "child_granted"
        feature = "ai_interaction"

        request_result = await service.request_consent(parent_id, child_id, feature)
        consent_id = request_result["consent_id"]

        await service.grant_consent(consent_id, "digital_signature")

        result = await service.check_consent_status(consent_id)

        assert result["status"] == "granted"
        assert result["granted_at"] is not None
        assert result["verification_method"] == "digital_signature"

    @pytest.mark.asyncio
    async def test_check_consent_status_not_found(self, service):
        """Test checking status of non-existent consent."""
        result = await service.check_consent_status("nonexistent_consent")

        assert result["status"] == "not_found"
        assert result["consent_id"] == "nonexistent_consent"

    @pytest.mark.asyncio
    async def test_check_consent_status_expired(self, service):
        """Test that expired consent is properly detected."""
        parent_id = "parent_expired"
        child_id = "child_expired"
        feature = "expired_feature"

        # Create consent that expires in the past
        result = await service.request_consent(
            parent_id, child_id, feature, expiry_days=-1
        )
        consent_id = result["consent_id"]

        # Check status should mark it as expired
        status_result = await service.check_consent_status(consent_id)

        assert status_result["status"] == "expired"

    @pytest.mark.asyncio
    async def test_verify_parental_consent_valid(self, service):
        """Test verification of valid parental consent."""
        parent_id = "parent_verify"
        child_id = "child_verify"
        consent_type = "data_processing"

        # Create and grant consent
        await service.request_consent(parent_id, child_id, consent_type)
        consent_id = f"consent_{parent_id}_{child_id}_{consent_type}"
        await service.grant_consent(consent_id, "government_id_verification")

        # Verify consent
        result = await service.verify_parental_consent(
            parent_id, child_id, consent_type
        )

        assert result is True

    @pytest.mark.asyncio
    async def test_verify_parental_consent_not_found(self, service):
        """Test verification when consent doesn't exist."""
        result = await service.verify_parental_consent(
            "nonexistent_parent", "nonexistent_child", "feature"
        )

        assert result is False

    @pytest.mark.asyncio
    async def test_verify_parental_consent_not_granted(self, service):
        """Test verification when consent is not granted."""
        parent_id = "parent_not_granted"
        child_id = "child_not_granted"
        consent_type = "analytics"

        # Create but don't grant consent
        await service.request_consent(parent_id, child_id, consent_type)

        result = await service.verify_parental_consent(
            parent_id, child_id, consent_type
        )

        assert result is False

    @pytest.mark.asyncio
    async def test_verify_parental_consent_expired(self, service):
        """Test verification when consent has expired."""
        parent_id = "parent_expired_verify"
        child_id = "child_expired_verify"
        consent_type = "expired_consent"

        # Create expired consent
        await service.request_consent(parent_id, child_id, consent_type, expiry_days=-1)
        consent_id = f"consent_{parent_id}_{child_id}_{consent_type}"
        await service.grant_consent(consent_id, "email_verification")

        result = await service.verify_parental_consent(
            parent_id, child_id, consent_type
        )

        assert result is False

        # Check that consent status was updated to expired
        consent = service.consents[consent_id]
        assert consent.status == "expired"

    @pytest.mark.asyncio
    async def test_initiate_email_verification(self, service):
        """Test email verification initiation."""
        consent_id = "test_email_consent"
        email = "parent@example.com"

        with patch.object(
            service.verification_service, "send_email_verification"
        ) as mock_send:
            mock_send.return_value = {
                "status": "success",
                "attempt_id": "test_attempt"}

            result = await service.initiate_email_verification(consent_id, email)

            mock_send.assert_called_once_with(email, consent_id)
            assert result["status"] == "success"
            assert result["attempt_id"] == "test_attempt"

    @pytest.mark.asyncio
    async def test_initiate_sms_verification(self, service):
        """Test SMS verification initiation."""
        consent_id = "test_sms_consent"
        phone = "+1234567890"

        with patch.object(
            service.verification_service, "send_sms_verification"
        ) as mock_send:
            mock_send.return_value = {
                "status": "success",
                "attempt_id": "sms_attempt"}

            result = await service.initiate_sms_verification(consent_id, phone)

            mock_send.assert_called_once_with(phone, consent_id)
            assert result["status"] == "success"
            assert result["attempt_id"] == "sms_attempt"

    @pytest.mark.asyncio
    async def test_complete_verification(self, service):
        """Test verification completion."""
        attempt_id = "test_verification_attempt"
        verification_code = "123456"

        with patch.object(service.verification_service, "verify_code") as mock_verify:
            mock_verify.return_value = {
                "status": "success",
                "message": "Verification successful",
            }

            result = await service.complete_verification(attempt_id, verification_code)

            mock_verify.assert_called_once_with(attempt_id, verification_code)
            assert result["status"] == "success"
            assert result["message"] == "Verification successful"

    def test_get_consent_audit_trail_success(self, service):
        """Test getting audit trail for existing consent."""
        # Create a consent manually for testing
        consent_id = "audit_test_consent"
        consent = ConsentRecord(
            consent_id=consent_id,
            parent_id="audit_parent",
            child_id="audit_child",
            feature="audit_feature",
            status="granted",
            requested_at="2024-01-15T10:30:00",
            expiry_date="2025-01-15T10:30:00",
            granted_at="2024-01-15T11:00:00",
            verification_method="email_verification",
            metadata={"source": "web_app"},
        )
        service.consents[consent_id] = consent

        result = service.get_consent_audit_trail(consent_id)

        assert result is not None
        assert result["consent_id"] == consent_id
        assert result["parent_id"] == "audit_parent"
        assert result["child_id"] == "audit_child"
        assert result["feature"] == "audit_feature"
        assert result["status"] == "granted"
        assert result["requested_at"] == "2024-01-15T10:30:00"
        assert result["granted_at"] == "2024-01-15T11:00:00"
        assert result["verification_method"] == "email_verification"
        assert result["metadata"] == {"source": "web_app"}

    def test_get_consent_audit_trail_not_found(self, service):
        """Test getting audit trail for non-existent consent."""
        result = service.get_consent_audit_trail("nonexistent_consent")

        assert result is None

    @pytest.mark.asyncio
    async def test_consent_lifecycle_complete_workflow(self, service):
        """Test complete consent lifecycle workflow."""
        parent_id = "lifecycle_parent"
        child_id = "lifecycle_child"
        feature = "complete_workflow"

        # Step 1: Request consent
        request_result = await service.request_consent(parent_id, child_id, feature)
        consent_id = request_result["consent_id"]

        assert request_result["status"] == "pending"

        # Step 2: Check initial status
        status_result = await service.check_consent_status(consent_id)
        assert status_result["status"] == "pending"

        # Step 3: Grant consent
        grant_result = await service.grant_consent(
            consent_id, "video_call_verification"
        )
        assert grant_result["status"] == "granted"

        # Step 4: Verify consent is active
        verify_result = await service.verify_parental_consent(
            parent_id, child_id, feature
        )
        assert verify_result is True

        # Step 5: Check granted status
        final_status = await service.check_consent_status(consent_id)
        assert final_status["status"] == "granted"
        assert final_status["verification_method"] == "video_call_verification"

        # Step 6: Get complete audit trail
        audit_trail = service.get_consent_audit_trail(consent_id)
        assert audit_trail["status"] == "granted"
        assert audit_trail["verification_method"] == "video_call_verification"

    @pytest.mark.asyncio
    async def test_consent_revocation_workflow(self, service):
        """Test consent revocation workflow."""
        parent_id = "revoke_parent"
        child_id = "revoke_child"
        feature = "revocation_test"

        # Create and grant consent
        request_result = await service.request_consent(parent_id, child_id, feature)
        consent_id = request_result["consent_id"]
        await service.grant_consent(consent_id, "credit_card_verification")

        # Verify consent is active
        verify_before = await service.verify_parental_consent(
            parent_id, child_id, feature
        )
        assert verify_before is True

        # Revoke consent
        revoke_result = await service.revoke_consent(consent_id)
        assert revoke_result["status"] == "revoked"

        # Verify consent is no longer active
        verify_after = await service.verify_parental_consent(
            parent_id, child_id, feature
        )
        assert verify_after is False

        # Check final status
        final_status = await service.check_consent_status(consent_id)
        assert final_status["status"] == "revoked"

    @pytest.mark.asyncio
    async def test_multiple_consents_same_parent_child(self, service):
        """Test multiple consents for same parent-child pair."""
        parent_id = "multi_parent"
        child_id = "multi_child"
        features = ["audio_recording", "location_tracking", "personalization"]

        consent_ids = []
        for feature in features:
            result = await service.request_consent(parent_id, child_id, feature)
            consent_ids.append(result["consent_id"])
            await service.grant_consent(
                result["consent_id"], "government_id_verification"
            )

        # Verify all consents are independent and active
        for i, feature in enumerate(features):
            verify_result = await service.verify_parental_consent(
                parent_id, child_id, feature
            )
            assert verify_result is True

            status_result = await service.check_consent_status(consent_ids[i])
            assert status_result["feature"] == feature
            assert status_result["status"] == "granted"

    @pytest.mark.asyncio
    async def test_concurrent_consent_operations(self, service):
        """Test concurrent consent operations."""
        parent_id = "concurrent_parent"
        child_id = "concurrent_child"
        features = ["feature1", "feature2", "feature3", "feature4"]

        # Create multiple consent requests concurrently
        tasks = [
            service.request_consent(
                parent_id, child_id, f"{feature}_concurrent")
            for feature in features
        ]

        results = await asyncio.gather(*tasks)

        # All should succeed
        assert len(results) == 4
        assert all(r["status"] == "pending" for r in results)

        # All should have unique consent IDs
        consent_ids = [r["consent_id"] for r in results]
        assert len(set(consent_ids)) == 4

        # All consents should be stored
        assert len(service.consents) == 4

    @pytest.mark.asyncio
    async def test_verification_integration_flow(self, service):
        """Test integration with verification service."""
        parent_id = "verify_integration_parent"
        child_id = "verify_integration_child"
        feature = "integration_test"
        email = "integration@test.com"

        # Mock verification service methods
        with patch.object(
            service.verification_service, "send_email_verification"
        ) as mock_email:
            with patch.object(
                service.verification_service, "verify_code"
            ) as mock_verify:
                mock_email.return_value = {
                    "status": "success",
                    "attempt_id": "integration_attempt",
                }
                mock_verify.return_value = {
                    "status": "success",
                    "message": "Verification successful",
                }

                # Request consent
                request_result = await service.request_consent(
                    parent_id, child_id, feature
                )
                consent_id = request_result["consent_id"]

                # Initiate email verification
                email_result = await service.initiate_email_verification(
                    consent_id, email
                )
                assert email_result["status"] == "success"

                # Complete verification
                verify_result = await service.complete_verification(
                    "integration_attempt", "123456"
                )
                assert verify_result["status"] == "success"

                # Grant consent
                grant_result = await service.grant_consent(
                    consent_id, "email_verification"
                )
                assert grant_result["status"] == "granted"

    @pytest.mark.asyncio
    async def test_logging_behavior(self, service):
        """Test that consent service logs appropriately."""
        with patch(
            "src.application.services.consent.consent_service.logger"
        ) as mock_logger:
            parent_id = "logging_parent"
            child_id = "logging_child"
            feature = "logging_test"

            # Test request logging
            await service.request_consent(parent_id, child_id, feature)
            mock_logger.info.assert_called()

            # Test grant logging
            consent_id = f"consent_{parent_id}_{child_id}_{feature}"
            await service.grant_consent(consent_id, "email_verification")
            mock_logger.info.assert_called()

            # Test revoke logging
            await service.revoke_consent(consent_id)
            mock_logger.info.assert_called()

    @pytest.mark.asyncio
    async def test_coppa_compliance_requirements(self, service):
        """Test that service meets COPPA compliance requirements."""
        parent_id = "coppa_parent"
        child_id = "coppa_child_under_13"
        feature = "personal_data_collection"

        # Request consent for data collection from child under 13
        result = await service.request_consent(parent_id, child_id, feature)
        consent_id = result["consent_id"]

        # Grant with proper verification
        await service.grant_consent(consent_id, "government_id_verification")

        consent = service.consents[consent_id]

        # Verify COPPA-required fields are present
        assert consent.parent_id is not None
        assert consent.child_id is not None
        assert consent.feature is not None
        assert consent.status == "granted"
        assert consent.requested_at is not None
        assert consent.granted_at is not None
        assert consent.verification_method is not None
        assert consent.expiry_date is not None

        # Verify audit trail is complete
        audit_trail = service.get_consent_audit_trail(consent_id)
        assert all(
            key in audit_trail
            for key in [
                "consent_id",
                "parent_id",
                "child_id",
                "feature",
                "status",
                "requested_at",
                "granted_at",
                "verification_method",
                "expiry_date",
            ]
        )

    @pytest.mark.asyncio
    async def test_edge_case_empty_strings(self, service):
        """Test handling of edge cases with empty strings."""
        # Test with empty parent_id
        with pytest.raises(Exception):
            await service.request_consent("", "child_123", "feature")

        # Test with empty child_id
        with pytest.raises(Exception):
            await service.request_consent("parent_123", "", "feature")

        # Test with empty feature
        with pytest.raises(Exception):
            await service.request_consent("parent_123", "child_123", "")

    @pytest.mark.asyncio
    async def test_consent_id_generation_pattern(self, service):
        """Test that consent IDs follow expected pattern."""
        parent_id = "pattern_parent"
        child_id = "pattern_child"
        feature = "pattern_feature"

        result = await service.request_consent(parent_id, child_id, feature)
        consent_id = result["consent_id"]

        # Should follow pattern: consent_{parent_id}_{child_id}_{feature}
        expected_id = f"consent_{parent_id}_{child_id}_{feature}"
        assert consent_id == expected_id

    @pytest.mark.asyncio
    async def test_expiry_date_calculation(self, service):
        """Test that expiry dates are calculated correctly."""
        parent_id = "expiry_parent"
        child_id = "expiry_child"
        feature = "expiry_test"
        expiry_days = 90

        before_request = datetime.utcnow()
        result = await service.request_consent(
            parent_id, child_id, feature, expiry_days
        )
        after_request = datetime.utcnow()

        consent_id = result["consent_id"]
        consent = service.consents[consent_id]

        requested_dt = datetime.fromisoformat(consent.requested_at)
        expiry_dt = datetime.fromisoformat(consent.expiry_date)

        # Requested time should be between before and after
        assert before_request <= requested_dt <= after_request

        # Expiry should be approximately expiry_days later
        expected_expiry = requested_dt + timedelta(days=expiry_days)
        time_diff = abs((expiry_dt - expected_expiry).total_seconds())
        assert time_diff < 5  # Allow 5 seconds tolerance
