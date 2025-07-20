"""Tests for Verification Service
Testing parental verification functionality for COPPA compliance.
"""

from unittest.mock import patch

import pytest

from src.application.services.consent.consent_models import (
    VerificationMethod,
    VerificationStatus,
)
from src.application.services.consent.verification_service import (
    VerificationService,
)


class TestVerificationService:
    """Test the Verification Service."""

    @pytest.fixture
    def service(self):
        """Create a verification service instance."""
        return VerificationService()

    def test_initialization(self, service):
        """Test service initialization."""
        assert isinstance(service, VerificationService)
        assert hasattr(service, "verification_attempts")
        assert hasattr(service, "verification_codes")
        assert isinstance(service.verification_attempts, dict)
        assert isinstance(service.verification_codes, dict)
        assert len(service.verification_attempts) == 0
        assert len(service.verification_codes) == 0

    @pytest.mark.asyncio
    async def test_send_email_verification_success(self, service):
        """Test successful email verification initiation."""
        email = "parent@example.com"
        consent_id = "consent_123"

        with patch.object(service, "_validate_email", return_value=True):
            with patch.object(
                service, "_generate_verification_code", return_value="123456"
            ):
                with patch(
                    "src.application.services.consent.verification_service.secrets.token_urlsafe",
                    return_value="random_token",
                ):
                    result = await service.send_email_verification(email, consent_id)

        assert result["status"] == "success"
        assert "attempt_id" in result
        assert result["message"] == "Verification code sent to email"

        # Check that verification attempt was stored
        attempt_id = result["attempt_id"]
        assert attempt_id in service.verification_attempts

        attempt = service.verification_attempts[attempt_id]
        assert attempt.consent_id == consent_id
        assert attempt.method == VerificationMethod.EMAIL_VERIFICATION
        assert attempt.status == VerificationStatus.PENDING
        assert attempt.verification_code == "123456"

    @pytest.mark.asyncio
    async def test_send_email_verification_invalid_email(self, service):
        """Test email verification with invalid email format."""
        invalid_emails = [
            "invalid-email",
            "@example.com",
            "user@",
            "user@.com",
            "",
            "user space@example.com",
        ]

        for email in invalid_emails:
            result = await service.send_email_verification(email, "consent_123")

            assert result["status"] == "error"
            assert result["message"] == "Invalid email format"

    @pytest.mark.asyncio
    async def test_send_sms_verification_success(self, service):
        """Test successful SMS verification initiation."""
        phone = "+1234567890"
        consent_id = "consent_456"

        with patch.object(service, "_validate_phone", return_value=True):
            with patch.object(
                service, "_generate_verification_code", return_value="654321"
            ):
                with patch(
                    "src.application.services.consent.verification_service.secrets.token_urlsafe",
                    return_value="sms_token",
                ):
                    result = await service.send_sms_verification(phone, consent_id)

        assert result["status"] == "success"
        assert "attempt_id" in result
        assert result["message"] == "Verification code sent via SMS"

        # Check that verification attempt was stored
        attempt_id = result["attempt_id"]
        assert attempt_id in service.verification_attempts

        attempt = service.verification_attempts[attempt_id]
        assert attempt.consent_id == consent_id
        assert attempt.method == VerificationMethod.SMS_VERIFICATION
        assert attempt.status == VerificationStatus.PENDING
        assert attempt.verification_code == "654321"

    @pytest.mark.asyncio
    async def test_send_sms_verification_invalid_phone(self, service):
        """Test SMS verification with invalid phone format."""
        invalid_phones = [
            "123",  # Too short
            "abc123def456",  # Contains letters
            "",  # Empty
            "123456789012345678",  # Too long
            "+",  # Just plus sign
        ]

        for phone in invalid_phones:
            result = await service.send_sms_verification(phone, "consent_123")

            assert result["status"] == "error"
            assert result["message"] == "Invalid phone format"

    @pytest.mark.asyncio
    async def test_verify_code_success(self, service):
        """Test successful code verification."""
        # First, create a verification attempt
        email = "test@example.com"
        consent_id = "consent_verify"

        with patch.object(service, "_validate_email", return_value=True):
            with patch.object(
                service, "_generate_verification_code", return_value="999888"
            ):
                with patch(
                    "src.application.services.consent.verification_service.secrets.token_urlsafe",
                    return_value="verify_token",
                ):
                    email_result = await service.send_email_verification(
                        email, consent_id
                    )

        attempt_id = email_result["attempt_id"]

        # Now verify the code
        result = await service.verify_code(attempt_id, "999888")

        assert result["status"] == "success"
        assert result["message"] == "Verification successful"

        # Check that attempt status was updated
        attempt = service.verification_attempts[attempt_id]
        assert attempt.status == VerificationStatus.VERIFIED
        assert attempt.completed_at is not None

    @pytest.mark.asyncio
    async def test_verify_code_invalid_attempt_id(self, service):
        """Test code verification with invalid attempt ID."""
        result = await service.verify_code("nonexistent_attempt", "123456")

        assert result["status"] == "error"
        assert result["message"] == "Invalid attempt ID"

    @pytest.mark.asyncio
    async def test_verify_code_wrong_code(self, service):
        """Test code verification with wrong verification code."""
        # Create a verification attempt
        email = "test@example.com"
        consent_id = "consent_wrong_code"

        with patch.object(service, "_validate_email", return_value=True):
            with patch.object(
                service,
                "_generate_verification_code",
                return_value="correct_code",
            ):
                with patch(
                    "src.application.services.consent.verification_service.secrets.token_urlsafe",
                    return_value="wrong_token",
                ):
                    email_result = await service.send_email_verification(
                        email, consent_id
                    )

        attempt_id = email_result["attempt_id"]

        # Try to verify with wrong code
        result = await service.verify_code(attempt_id, "wrong_code")

        assert result["status"] == "error"
        assert result["message"] == "Invalid verification code"

        # Check that attempt status was updated to failed
        attempt = service.verification_attempts[attempt_id]
        assert attempt.status == VerificationStatus.FAILED
        assert attempt.failure_reason == "Invalid verification code"

    def test_validate_email_valid_formats(self, service):
        """Test email validation with valid email formats."""
        valid_emails = [
            "user@example.com",
            "test.email@domain.co.uk",
            "parent123@gmail.com",
            "first.last+tag@example.org",
            "user_name@example-domain.com",
            "a@b.co",
        ]

        for email in valid_emails:
            assert service._validate_email(email) is True

    def test_validate_email_invalid_formats(self, service):
        """Test email validation with invalid email formats."""
        invalid_emails = [
            "plainaddress",
            "@missingdomain.com",
            "missing@.com",
            "missing@domain",
            "spaces in@email.com",
            "user@domain,com",
            "",
            "user@@domain.com",
            "user@domain..com",
        ]

        for email in invalid_emails:
            assert service._validate_email(email) is False

    def test_validate_phone_valid_formats(self, service):
        """Test phone validation with valid phone formats."""
        valid_phones = [
            "+1234567890",  # 10 digits
            "1234567890",  # 10 digits no plus
            "+12345678901",  # 11 digits
            "+123456789012345",  # 15 digits (max)
            "(123) 456-7890",  # With formatting
            "123-456-7890",  # With dashes
            "123.456.7890",  # With dots
            "+1 (123) 456-7890",  # Full international format
        ]

        for phone in valid_phones:
            assert service._validate_phone(phone) is True

    def test_validate_phone_invalid_formats(self, service):
        """Test phone validation with invalid phone formats."""
        invalid_phones = [
            "123456789",  # Too short (9 digits)
            "12345678901234567",  # Too long (17 digits)
            "abc1234567890",  # Contains letters
            "",  # Empty
            "+",  # Just plus sign
            "123",  # Way too short
            "abcdefghij",  # All letters
        ]

        for phone in invalid_phones:
            assert service._validate_phone(phone) is False

    def test_generate_verification_code_format(self, service):
        """Test verification code generation format."""
        with patch(
            "src.application.services.consent.verification_service.secrets.randbelow",
            return_value=123456,
        ):
            code = service._generate_verification_code()
            assert code == "123456"
            assert len(code) == 6
            assert code.isdigit()

    def test_generate_verification_code_zero_padding(self, service):
        """Test verification code generation with zero padding."""
        with patch(
            "src.application.services.consent.verification_service.secrets.randbelow",
            return_value=123,
        ):
            code = service._generate_verification_code()
            assert code == "000123"
            assert len(code) == 6

    def test_generate_verification_code_randomness(self, service):
        """Test verification code generation produces different codes."""
        codes = set()
        for _ in range(100):
            code = service._generate_verification_code()
            codes.add(code)
            assert len(code) == 6
            assert code.isdigit()

        # Should have generated mostly unique codes
        assert len(codes) > 50  # Reasonable expectation for randomness

    @pytest.mark.asyncio
    async def test_multiple_verification_attempts_same_consent(self, service):
        """Test multiple verification attempts for same consent."""
        consent_id = "consent_multiple"

        # Send email verification
        with patch.object(service, "_validate_email", return_value=True):
            with patch.object(
                service, "_generate_verification_code", return_value="111111"
            ):
                email_result = await service.send_email_verification(
                    "email@test.com", consent_id
                )

        # Send SMS verification for same consent
        with patch.object(service, "_validate_phone", return_value=True):
            with patch.object(
                service, "_generate_verification_code", return_value="222222"
            ):
                sms_result = await service.send_sms_verification(
                    "+1234567890", consent_id
                )

        assert email_result["status"] == "success"
        assert sms_result["status"] == "success"
        assert email_result["attempt_id"] != sms_result["attempt_id"]

        # Both attempts should be stored
        assert len(service.verification_attempts) == 2

        # Both should reference the same consent
        email_attempt = service.verification_attempts[email_result["attempt_id"]]
        sms_attempt = service.verification_attempts[sms_result["attempt_id"]]

        assert email_attempt.consent_id == consent_id
        assert sms_attempt.consent_id == consent_id
        assert email_attempt.method == VerificationMethod.EMAIL_VERIFICATION
        assert sms_attempt.method == VerificationMethod.SMS_VERIFICATION

    @pytest.mark.asyncio
    async def test_verification_attempt_lifecycle(self, service):
        """Test complete verification attempt lifecycle."""
        email = "lifecycle@test.com"
        consent_id = "consent_lifecycle"

        # Step 1: Initiate verification
        with patch.object(service, "_validate_email", return_value=True):
            with patch.object(
                service, "_generate_verification_code", return_value="555666"
            ):
                result = await service.send_email_verification(email, consent_id)

        attempt_id = result["attempt_id"]
        attempt = service.verification_attempts[attempt_id]

        # Verify initial state
        assert attempt.status == VerificationStatus.PENDING
        assert attempt.attempted_at is not None
        assert attempt.completed_at is None
        assert attempt.failure_reason is None

        # Step 2: Verify with correct code
        verify_result = await service.verify_code(attempt_id, "555666")

        # Verify final state
        assert verify_result["status"] == "success"
        assert attempt.status == VerificationStatus.VERIFIED
        assert attempt.completed_at is not None
        assert attempt.failure_reason is None

    @pytest.mark.asyncio
    async def test_verification_attempt_failure_lifecycle(self, service):
        """Test verification attempt failure lifecycle."""
        email = "failure@test.com"
        consent_id = "consent_failure"

        # Step 1: Initiate verification
        with patch.object(service, "_validate_email", return_value=True):
            with patch.object(
                service,
                "_generate_verification_code",
                return_value="correct123",
            ):
                result = await service.send_email_verification(email, consent_id)

        attempt_id = result["attempt_id"]
        attempt = service.verification_attempts[attempt_id]

        # Step 2: Verify with wrong code
        verify_result = await service.verify_code(attempt_id, "wrong123")

        # Verify failure state
        assert verify_result["status"] == "error"
        assert attempt.status == VerificationStatus.FAILED
        assert attempt.failure_reason == "Invalid verification code"

    @pytest.mark.asyncio
    async def test_concurrent_verification_operations(self, service):
        """Test concurrent verification operations."""
        import asyncio

        # Prepare multiple verification requests
        verification_requests = [
            ("email1@test.com", "consent_1"),
            ("email2@test.com", "consent_2"),
            ("email3@test.com", "consent_3"),
        ]

        with patch.object(service, "_validate_email", return_value=True):
            with patch.object(
                service,
                "_generate_verification_code",
                side_effect=["111111", "222222", "333333"],
            ):
                # Send verifications concurrently
                tasks = [
                    service.send_email_verification(email, consent_id)
                    for email, consent_id in verification_requests
                ]

                results = await asyncio.gather(*tasks)

        # All should succeed
        assert len(results) == 3
        assert all(r["status"] == "success" for r in results)

        # All should have unique attempt IDs
        attempt_ids = [r["attempt_id"] for r in results]
        assert len(set(attempt_ids)) == 3

        # All attempts should be stored
        assert len(service.verification_attempts) == 3

    @pytest.mark.asyncio
    async def test_attempt_id_generation_pattern(self, service):
        """Test attempt ID generation follows expected pattern."""
        with patch.object(service, "_validate_email", return_value=True):
            with patch.object(
                service, "_generate_verification_code", return_value="123456"
            ):
                with patch(
                    "src.application.services.consent.verification_service.secrets.token_urlsafe",
                    return_value="test_token",
                ):
                    result = await service.send_email_verification(
                        "test@example.com", "consent_pattern"
                    )

        attempt_id = result["attempt_id"]

        # Should start with "verify_"
        assert attempt_id.startswith("verify_")

        # Should contain consent ID
        assert "consent_pattern" in attempt_id

        # Should contain token
        assert "test_token" in attempt_id

    @pytest.mark.asyncio
    async def test_sms_attempt_id_generation_pattern(self, service):
        """Test SMS attempt ID generation follows expected pattern."""
        with patch.object(service, "_validate_phone", return_value=True):
            with patch.object(
                service, "_generate_verification_code", return_value="123456"
            ):
                with patch(
                    "src.application.services.consent.verification_service.secrets.token_urlsafe",
                    return_value="sms_token",
                ):
                    result = await service.send_sms_verification(
                        "+1234567890", "consent_sms_pattern"
                    )

        attempt_id = result["attempt_id"]

        # Should start with "sms_"
        assert attempt_id.startswith("sms_")

        # Should contain consent ID
        assert "consent_sms_pattern" in attempt_id

        # Should contain token
        assert "sms_token" in attempt_id

    @pytest.mark.asyncio
    async def test_logging_behavior(self, service):
        """Test that verification service logs appropriately."""
        with patch(
            "src.application.services.consent.verification_service.logger"
        ) as mock_logger:
            # Test email verification logging
            with patch.object(service, "_validate_email", return_value=True):
                with patch.object(
                    service,
                    "_generate_verification_code",
                    return_value="123456",
                ):
                    await service.send_email_verification(
                        "test@example.com", "consent_log"
                    )

            # Should log email sending with masked email
            mock_logger.info.assert_called()
            log_call = mock_logger.info.call_args[0][0]
            assert "te***@example.com" in log_call
            assert "[REDACTED]" in log_call

    @pytest.mark.asyncio
    async def test_logging_successful_verification(self, service):
        """Test logging for successful verification."""
        with patch(
            "src.application.services.consent.verification_service.logger"
        ) as mock_logger:
            # Create verification attempt
            with patch.object(service, "_validate_email", return_value=True):
                with patch.object(
                    service,
                    "_generate_verification_code",
                    return_value="success123",
                ):
                    result = await service.send_email_verification(
                        "success@test.com", "consent_success"
                    )

            # Clear previous calls
            mock_logger.reset_mock()

            # Verify successfully
            await service.verify_code(result["attempt_id"], "success123")

            # Should log successful verification
            mock_logger.info.assert_called()
            log_call = mock_logger.info.call_args[0][0]
            assert "Verification successful" in log_call
            assert "[REDACTED]" in log_call

    @pytest.mark.asyncio
    async def test_logging_failed_verification(self, service):
        """Test logging for failed verification."""
        with patch(
            "src.application.services.consent.verification_service.logger"
        ) as mock_logger:
            # Create verification attempt
            with patch.object(service, "_validate_email", return_value=True):
                with patch.object(
                    service,
                    "_generate_verification_code",
                    return_value="fail123",
                ):
                    result = await service.send_email_verification(
                        "fail@test.com", "consent_fail"
                    )

            # Clear previous calls
            mock_logger.reset_mock()

            # Verify with wrong code
            await service.verify_code(result["attempt_id"], "wrong123")

            # Should log failed verification
            mock_logger.warning.assert_called()
            log_call = mock_logger.warning.call_args[0][0]
            assert "Verification failed" in log_call
            assert "[REDACTED]" in log_call

    def test_phone_masking_in_logs(self, service):
        """Test that phone numbers are properly masked in logs."""
        test_cases = [
            ("+1234567890", "+12***90"),
            ("1234567890", "123***90"),
            ("12345", "***"),  # Short number
            ("+123456789012", "+12***12"),  # Long number
        ]

        for phone, expected_mask in test_cases:
            with patch(
                "src.application.services.consent.verification_service.logger"
            ) as mock_logger:
                with patch.object(service, "_validate_phone", return_value=True):
                    with patch.object(
                        service,
                        "_generate_verification_code",
                        return_value="123456",
                    ):
                        # This should trigger the masking logic
                        asyncio.run(
                            service.send_sms_verification(phone, "consent_mask")
                        )

                # Check that phone was properly masked
                mock_logger.info.assert_called()
                log_call = mock_logger.info.call_args[0][0]
                assert expected_mask in log_call
                assert phone not in log_call  # Original number should not appear

    def test_email_masking_in_logs(self, service):
        """Test that email addresses are properly masked in logs."""
        test_cases = [
            ("test@example.com", "te***@example.com"),
            ("a@b.co", "a***@b.co"),
            ("verylongemail@domain.org", "ve***@domain.org"),
        ]

        for email, expected_mask in test_cases:
            with patch(
                "src.application.services.consent.verification_service.logger"
            ) as mock_logger:
                with patch.object(service, "_validate_email", return_value=True):
                    with patch.object(
                        service,
                        "_generate_verification_code",
                        return_value="123456",
                    ):
                        asyncio.run(
                            service.send_email_verification(email, "consent_mask")
                        )

                # Check that email was properly masked
                mock_logger.info.assert_called()
                log_call = mock_logger.info.call_args[0][0]
                assert expected_mask in log_call
                assert email not in log_call  # Original email should not appear
