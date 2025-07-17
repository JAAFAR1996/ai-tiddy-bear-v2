"""
Tests for Parent Child Verification Service
Testing parent-child relationship verification and management.
"""

import pytest

from src.application.services.parent_child_verification_service import (
    ParentChildVerificationService,
    RelationshipManager,
    RelationshipStatus,
    RelationshipType,
    VerificationRecord,
    RelationshipRecord,
    get_verification_service,
    get_relationship_manager,
)


class TestParentChildVerificationService:
    """Test the Parent Child Verification Service module."""

    def test_imports_available(self):
        """Test that all expected imports are available."""
        # Test that classes can be imported
        assert ParentChildVerificationService is not None
        assert RelationshipManager is not None
        assert RelationshipStatus is not None
        assert RelationshipType is not None
        assert VerificationRecord is not None
        assert RelationshipRecord is not None

    def test_factory_functions_available(self):
        """Test that factory functions are available."""
        assert callable(get_verification_service)
        assert callable(get_relationship_manager)

    def test_get_verification_service_factory(self):
        """Test the verification service factory function."""
        service = get_verification_service()

        assert service is not None
        assert isinstance(service, ParentChildVerificationService)

    def test_get_relationship_manager_factory(self):
        """Test the relationship manager factory function."""
        manager = get_relationship_manager()

        assert manager is not None
        assert isinstance(manager, RelationshipManager)

    def test_factory_functions_return_new_instances(self):
        """Test that factory functions return new instances each time."""
        service1 = get_verification_service()
        service2 = get_verification_service()

        assert service1 is not service2

        manager1 = get_relationship_manager()
        manager2 = get_relationship_manager()

        assert manager1 is not manager2

    def test_all_exports_in_all(self):
        """Test that __all__ contains expected exports."""
        from src.application.services.parent_child_verification_service import (
            __all__,
        )

        expected_exports = [
            "ParentChildVerificationService",
            "RelationshipManager",
            "RelationshipStatus",
            "RelationshipType",
            "VerificationRecord",
            "RelationshipRecord",
        ]

        for export in expected_exports:
            assert export in __all__

    @pytest.mark.asyncio
    async def test_verification_service_basic_functionality(self):
        """Test basic functionality of the verification service."""
        service = get_verification_service()

        # Test that the service has expected methods
        assert hasattr(service, "verify_relationship")
        assert hasattr(service, "get_verification_status")
        assert hasattr(service, "create_verification_request")

        # Test basic verification workflow
        parent_id = "parent_123"
        child_id = "child_456"

        # Create verification request
        request = await service.create_verification_request(
            parent_id, child_id
        )
        assert request is not None
        assert request.parent_id == parent_id
        assert request.child_id == child_id
        assert request.status in [
            RelationshipStatus.PENDING,
            RelationshipStatus.VERIFIED,
        ]

    @pytest.mark.asyncio
    async def test_relationship_manager_basic_functionality(self):
        """Test basic functionality of the relationship manager."""
        manager = get_relationship_manager()

        # Test that the manager has expected methods
        assert hasattr(manager, "add_relationship")
        assert hasattr(manager, "get_relationships")
        assert hasattr(manager, "update_relationship_status")

        # Test basic relationship management
        parent_id = "parent_789"
        child_id = "child_012"

        # Add relationship
        relationship = await manager.add_relationship(
            parent_id, child_id, RelationshipType.PARENT_CHILD
        )
        assert relationship is not None
        assert relationship.parent_id == parent_id
        assert relationship.child_id == child_id
        assert relationship.relationship_type == RelationshipType.PARENT_CHILD

    def test_relationship_status_enum(self):
        """Test RelationshipStatus enum values."""
        # Test that enum has expected values
        assert hasattr(RelationshipStatus, "PENDING")
        assert hasattr(RelationshipStatus, "VERIFIED")
        assert hasattr(RelationshipStatus, "REJECTED")
        assert hasattr(RelationshipStatus, "EXPIRED")

        # Test enum value types
        assert isinstance(RelationshipStatus.PENDING, RelationshipStatus)
        assert isinstance(RelationshipStatus.VERIFIED, RelationshipStatus)
        assert isinstance(RelationshipStatus.REJECTED, RelationshipStatus)
        assert isinstance(RelationshipStatus.EXPIRED, RelationshipStatus)

    def test_relationship_type_enum(self):
        """Test RelationshipType enum values."""
        # Test that enum has expected values
        assert hasattr(RelationshipType, "PARENT_CHILD")
        assert hasattr(RelationshipType, "GUARDIAN_CHILD")
        assert hasattr(RelationshipType, "CAREGIVER_CHILD")

        # Test enum value types
        assert isinstance(RelationshipType.PARENT_CHILD, RelationshipType)
        assert isinstance(RelationshipType.GUARDIAN_CHILD, RelationshipType)
        assert isinstance(RelationshipType.CAREGIVER_CHILD, RelationshipType)

    @pytest.mark.asyncio
    async def test_verification_record_creation(self):
        """Test VerificationRecord creation and attributes."""
        service = get_verification_service()

        parent_id = "parent_test"
        child_id = "child_test"

        record = await service.create_verification_request(parent_id, child_id)

        # Test that record has expected attributes
        assert hasattr(record, "id")
        assert hasattr(record, "parent_id")
        assert hasattr(record, "child_id")
        assert hasattr(record, "status")
        assert hasattr(record, "created_at")
        assert hasattr(record, "updated_at")

        # Test attribute values
        assert record.parent_id == parent_id
        assert record.child_id == child_id
        assert isinstance(record.status, RelationshipStatus)

    @pytest.mark.asyncio
    async def test_relationship_record_creation(self):
        """Test RelationshipRecord creation and attributes."""
        manager = get_relationship_manager()

        parent_id = "parent_rel_test"
        child_id = "child_rel_test"

        record = await manager.add_relationship(
            parent_id, child_id, RelationshipType.PARENT_CHILD
        )

        # Test that record has expected attributes
        assert hasattr(record, "id")
        assert hasattr(record, "parent_id")
        assert hasattr(record, "child_id")
        assert hasattr(record, "relationship_type")
        assert hasattr(record, "status")
        assert hasattr(record, "created_at")
        assert hasattr(record, "updated_at")

        # Test attribute values
        assert record.parent_id == parent_id
        assert record.child_id == child_id
        assert record.relationship_type == RelationshipType.PARENT_CHILD
        assert isinstance(record.status, RelationshipStatus)

    @pytest.mark.asyncio
    async def test_verification_workflow_complete(self):
        """Test complete verification workflow."""
        service = get_verification_service()

        parent_id = "parent_workflow"
        child_id = "child_workflow"

        # Step 1: Create verification request
        request = await service.create_verification_request(
            parent_id, child_id
        )
        assert request.status == RelationshipStatus.PENDING

        # Step 2: Check verification status
        status = await service.get_verification_status(parent_id, child_id)
        assert status == RelationshipStatus.PENDING

        # Step 3: Verify relationship
        verification_result = await service.verify_relationship(
            parent_id, child_id, verification_method="email_confirmation"
        )
        assert verification_result is True

        # Step 4: Check final status
        final_status = await service.get_verification_status(
            parent_id, child_id
        )
        assert final_status == RelationshipStatus.VERIFIED

    @pytest.mark.asyncio
    async def test_relationship_management_workflow(self):
        """Test complete relationship management workflow."""
        manager = get_relationship_manager()

        parent_id = "parent_mgmt_workflow"
        child_id = "child_mgmt_workflow"

        # Step 1: Add relationship
        relationship = await manager.add_relationship(
            parent_id, child_id, RelationshipType.GUARDIAN_CHILD
        )
        assert (
            relationship.relationship_type == RelationshipType.GUARDIAN_CHILD
        )

        # Step 2: Get relationships
        parent_relationships = await manager.get_relationships(parent_id)
        assert len(parent_relationships) >= 1
        assert any(rel.child_id == child_id for rel in parent_relationships)

        # Step 3: Update relationship status
        updated = await manager.update_relationship_status(
            relationship.id, RelationshipStatus.VERIFIED
        )
        assert updated.status == RelationshipStatus.VERIFIED

    @pytest.mark.asyncio
    async def test_multiple_children_verification(self):
        """Test verification for parent with multiple children."""
        service = get_verification_service()

        parent_id = "parent_multiple"
        child_ids = ["child_1", "child_2", "child_3"]

        # Create verification requests for all children
        requests = []
        for child_id in child_ids:
            request = await service.create_verification_request(
                parent_id, child_id
            )
            requests.append(request)

        # Verify all requests were created
        assert len(requests) == 3

        # Verify each child separately
        for i, child_id in enumerate(child_ids):
            verification_result = await service.verify_relationship(
                parent_id, child_id, verification_method="sms_code"
            )
            assert verification_result is True

            # Check individual status
            status = await service.get_verification_status(parent_id, child_id)
            assert status == RelationshipStatus.VERIFIED

    @pytest.mark.asyncio
    async def test_multiple_relationship_types(self):
        """Test different relationship types."""
        manager = get_relationship_manager()

        adult_id = "adult_multi"
        child_id = "child_multi"

        relationship_types = [
            RelationshipType.PARENT_CHILD,
            RelationshipType.GUARDIAN_CHILD,
            RelationshipType.CAREGIVER_CHILD,
        ]

        relationships = []
        for rel_type in relationship_types:
            # Use different adult IDs to test different types
            relationship = await manager.add_relationship(
                f"{adult_id}_{rel_type.value}", child_id, rel_type
            )
            relationships.append(relationship)

        # Verify all relationship types were created
        assert len(relationships) == 3
        for i, relationship in enumerate(relationships):
            assert relationship.relationship_type == relationship_types[i]

    @pytest.mark.asyncio
    async def test_error_handling_verification(self):
        """Test error handling in verification process."""
        service = get_verification_service()

        # Test with invalid IDs
        try:
            await service.create_verification_request(None, "child_123")
            assert False, "Should have raised an error"
        except (ValueError, TypeError):
            pass  # Expected

        try:
            await service.create_verification_request("parent_123", None)
            assert False, "Should have raised an error"
        except (ValueError, TypeError):
            pass  # Expected

        # Test verification of non-existent relationship
        status = await service.get_verification_status(
            "nonexistent_parent", "nonexistent_child"
        )
        assert status in [RelationshipStatus.REJECTED, None]

    @pytest.mark.asyncio
    async def test_error_handling_relationship_manager(self):
        """Test error handling in relationship manager."""
        manager = get_relationship_manager()

        # Test with invalid relationship type
        try:
            await manager.add_relationship(
                "parent_123",
                "child_123",
                "invalid_type",  # Should be RelationshipType enum
            )
            assert False, "Should have raised an error"
        except (ValueError, TypeError):
            pass  # Expected

        # Test updating non-existent relationship
        try:
            await manager.update_relationship_status(
                "nonexistent_id", RelationshipStatus.VERIFIED
            )
            assert False, "Should have raised an error"
        except (ValueError, TypeError, KeyError):
            pass  # Expected

    @pytest.mark.asyncio
    async def test_concurrent_verifications(self):
        """Test concurrent verification operations."""
        import asyncio

        service = get_verification_service()

        # Create multiple verification requests concurrently
        parent_child_pairs = [
            ("parent_a", "child_a"),
            ("parent_b", "child_b"),
            ("parent_c", "child_c"),
        ]

        # Create verification requests concurrently
        request_tasks = [
            service.create_verification_request(parent_id, child_id)
            for parent_id, child_id in parent_child_pairs
        ]

        requests = await asyncio.gather(*request_tasks)

        # All requests should be created successfully
        assert len(requests) == 3
        assert all(
            req.status == RelationshipStatus.PENDING for req in requests
        )

        # Verify relationships concurrently
        verify_tasks = [
            service.verify_relationship(
                parent_id, child_id, "email_confirmation"
            )
            for parent_id, child_id in parent_child_pairs
        ]

        results = await asyncio.gather(*verify_tasks)

        # All verifications should succeed
        assert all(result is True for result in results)

    def test_backward_compatibility_imports(self):
        """Test that backward compatibility imports work."""
        # Test that all classes can be imported from the main module
        from src.application.services.parent_child_verification_service import (
            ParentChildVerificationService as PCVS,
            RelationshipManager as RM,
            RelationshipStatus as RS,
            RelationshipType as RT,
            VerificationRecord as VR,
            RelationshipRecord as RR,
        )

        assert PCVS is not None
        assert RM is not None
        assert RS is not None
        assert RT is not None
        assert VR is not None
        assert RR is not None

    @pytest.mark.asyncio
    async def test_service_integration(self):
        """Test integration between verification service and relationship manager."""
        verification_service = get_verification_service()
        relationship_manager = get_relationship_manager()

        parent_id = "integration_parent"
        child_id = "integration_child"

        # Create verification through verification service
        verification_request = (
            await verification_service.create_verification_request(
                parent_id, child_id
            )
        )

        # Verify the relationship
        verification_result = await verification_service.verify_relationship(
            parent_id, child_id, "phone_verification"
        )
        assert verification_result is True

        # Check that relationship exists in relationship manager
        relationships = await relationship_manager.get_relationships(parent_id)

        # Should have at least one relationship for this parent
        assert len(relationships) >= 1
        child_relationship = next(
            (rel for rel in relationships if rel.child_id == child_id), None
        )
        assert child_relationship is not None
        assert child_relationship.status == RelationshipStatus.VERIFIED

    def test_module_documentation(self):
        """Test that the module has proper documentation."""
        import src.application.services.parent_child_verification_service as module

        assert module.__doc__ is not None
        assert "parent-child verification" in module.__doc__.lower()
        assert "migration note" in module.__doc__.lower()
        assert "verification" in module.__doc__.lower()
