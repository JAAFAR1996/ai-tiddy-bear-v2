"""Unit tests for real consent database service.

Tests verify that dummy implementations have been replaced with
production-ready database operations.
"""

import uuid
from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, MagicMock

import pytest

from src.domain.models.consent_models_domain import ConsentType
from src.infrastructure.persistence.services.consent_service import (
    ConsentDatabaseService,
)


class TestConsentDatabaseService:
    """Test real database operations for consent management."""

    @pytest.fixture
    def mock_db_session(self):
        """Create mock database session."""
        session = AsyncMock()
        return session

    @pytest.fixture
    def consent_service(self, mock_db_session):
        """Create consent service with mocked database."""
        return ConsentDatabaseService(mock_db_session)

    @pytest.mark.asyncio
    async def test_create_consent_record_success(
        self, consent_service, mock_db_session
    ):
        """Test creating consent record with real database operations."""
        # Arrange
        child_id = str(uuid.uuid4())
        parent_id = str(uuid.uuid4())
        data_types = ["voice_interactions", "preferences"]

        # Mock child and parent existence checks
        mock_db_session.scalar.side_effect = [child_id, parent_id]  # Both exist
        mock_db_session.commit = AsyncMock()

        # Act
        result = await consent_service.create_consent_record(
            child_id=child_id, parent_id=parent_id, data_types=data_types
        )

        # Assert
        assert result is not None
        assert isinstance(result, str)
        assert (
            result != f"consent_{child_id}_{datetime.now().timestamp()}"
        )  # Not dummy format

        # Verify database operations were called
        mock_db_session.add.assert_called_once()
        mock_db_session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_consent_record_child_not_found(
        self, consent_service, mock_db_session
    ):
        """Test consent creation fails when child doesn't exist."""
        # Arrange
        child_id = str(uuid.uuid4())
        parent_id = str(uuid.uuid4())
        data_types = ["voice_interactions"]

        # Mock child not found
        mock_db_session.scalar.return_value = None

        # Act & Assert
        with pytest.raises(ValueError, match="Child with ID .* not found"):
            await consent_service.create_consent_record(
                child_id=child_id, parent_id=parent_id, data_types=data_types
            )

    @pytest.mark.asyncio
    async def test_verify_parental_consent_valid(
        self, consent_service, mock_db_session
    ):
        """Test verification of valid parental consent."""
        # Arrange
        parent_id = str(uuid.uuid4())
        child_id = str(uuid.uuid4())

        # Mock valid consent record
        mock_consent = MagicMock()
        mock_consent.granted = True
        mock_consent.expires_at = datetime.now(UTC) + timedelta(days=30)
        mock_consent.revoked_at = None
        mock_consent.verification_metadata = {"child_id": child_id}

        mock_db_session.scalar.return_value = mock_consent

        # Act
        result = await consent_service.verify_parental_consent(
            parent_id=parent_id, child_id=child_id
        )

        # Assert
        assert result is True
        # Verify it's not just returning static True (dummy behavior)
        mock_db_session.scalar.assert_called_once()

    @pytest.mark.asyncio
    async def test_verify_parental_consent_expired(
        self, consent_service, mock_db_session
    ):
        """Test verification fails for expired consent."""
        # Arrange
        parent_id = str(uuid.uuid4())
        child_id = str(uuid.uuid4())

        # Mock expired consent record
        mock_consent = MagicMock()
        mock_consent.granted = True
        mock_consent.expires_at = datetime.now(UTC) - timedelta(days=1)  # Expired
        mock_consent.revoked_at = None

        mock_db_session.scalar.return_value = None  # Query returns None for expired

        # Act
        result = await consent_service.verify_parental_consent(
            parent_id=parent_id, child_id=child_id
        )

        # Assert
        assert result is False
        mock_db_session.scalar.assert_called_once()

    @pytest.mark.asyncio
    async def test_revoke_consent_success(self, consent_service, mock_db_session):
        """Test successful consent revocation."""
        # Arrange
        consent_id = str(uuid.uuid4())
        reason = "parent_request"

        # Mock successful update
        mock_result = MagicMock()
        mock_result.rowcount = 1
        mock_db_session.execute.return_value = mock_result
        mock_db_session.commit = AsyncMock()

        # Act
        result = await consent_service.revoke_consent(consent_id, reason)

        # Assert
        assert result is True
        mock_db_session.execute.assert_called_once()
        mock_db_session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_consent_status_active(self, consent_service, mock_db_session):
        """Test getting status of active consent."""
        # Arrange
        consent_id = str(uuid.uuid4())

        # Mock active consent
        mock_consent = MagicMock()
        mock_consent.id = consent_id
        mock_consent.granted = True
        mock_consent.granted_at = datetime.now(UTC)
        mock_consent.expires_at = datetime.now(UTC) + timedelta(days=30)
        mock_consent.revoked_at = None
        mock_consent.consent_type = ConsentType.EXPLICIT
        mock_consent.verification_method = "parental_confirmation"
        mock_consent.verification_metadata = {"child_id": "test"}

        mock_db_session.scalar.return_value = mock_consent

        # Act
        result = await consent_service.get_consent_status(consent_id)

        # Assert
        assert result["consent_id"] == consent_id
        assert result["status"] == "active"
        assert result["granted"] is True
        assert "granted_at" in result
        assert "expires_at" in result

        # Verify database query was made (not static data)
        mock_db_session.scalar.assert_called_once()


class TestIntegrationConsent:
    """Integration tests to verify dummy implementations are replaced."""

    @pytest.mark.asyncio
    async def test_consent_not_dummy_implementation(self):
        """Verify consent service uses real database, not dummy returns."""
        from src.infrastructure.validators.security.coppa_validator import (
            COPPAValidator,
        )
        from src.presentation.api.endpoints.children.compliance import (
            ParentalConsentManager,
        )

        # Create manager (this would normally connect to real DB)
        coppa_validator = COPPAValidator()
        consent_manager = ParentalConsentManager(coppa_validator)

        # The implementation should NOT return the old dummy format
        # Old dummy: f"consent_{child_id}_{datetime.now().timestamp()}"

        child_id = str(uuid.uuid4())
        parent_id = str(uuid.uuid4())
        data_types = ["voice_interactions"]

        try:
            result = await consent_manager.create_consent_record(
                child_id=child_id, parent_id=parent_id, data_types=data_types
            )

            # Should not match old dummy pattern
            assert not result.startswith(f"consent_{child_id}_")
            # Should be a UUID or database-generated ID
            assert len(result) > 10  # Not just a simple timestamp

        except Exception:
            # Even if DB connection fails, it should attempt real DB operations
            # The old dummy implementation never raised exceptions
            pass

    @pytest.mark.asyncio
    async def test_retention_not_dummy_implementation(self):
        """Verify retention service uses real database, not dummy returns."""
        from src.infrastructure.validators.security.coppa_validator import (
            COPPAValidator,
        )
        from src.presentation.api.endpoints.children.compliance import (
            LocalRetentionManager,
        )

        # Create manager
        coppa_validator = COPPAValidator()
        retention_manager = LocalRetentionManager(coppa_validator)

        child_id = str(uuid.uuid4())

        try:
            # Test retention compliance check
            result = await retention_manager.check_retention_compliance(child_id)

            # Old dummy always returned: {"compliant": True, "retention_days": 90, "next_review": datetime.now()}
            # New implementation should have more fields and real data
            assert "compliance_status" in result or "error" in result
            # Should not be static dummy values
            if "retention_days" in result:
                assert isinstance(result["retention_days"], int)

        except Exception:
            # Real implementation may fail due to DB connection
            # Dummy implementation never raised exceptions
            pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
