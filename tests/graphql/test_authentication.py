import os

import pytest

try:
    from src.infrastructure.graphql.authentication import create_auth_service
    from src.infrastructure.graphql.authentication.authentication import (
        Permission,
        User,
        UserRole,
        create_auth_config,
    )

    FEDERATION_AVAILABLE = True
except ImportError:
    FEDERATION_AVAILABLE = False


@pytest.fixture
def auth_config():
    """Test authentication configuration."""
    return create_auth_config("test-secret-key")


@pytest.fixture
async def auth_service(auth_config):
    """Authentication service fixture."""
    return await create_auth_service(auth_config)


@pytest.mark.skipif(
    not FEDERATION_AVAILABLE, reason="Federation not available"
)
class TestAuthentication:
    """Test authentication system."""

    @pytest.mark.asyncio
    async def test_user_creation(self, auth_service):
        """Test user creation."""
        user = await auth_service.create_user(
            username="testuser",
            email="test@example.com",
            password=os.environ.get("TEST_PASSWORD"),
            role=UserRole.PARENT,
        )

        assert user.username == "testuser"
        assert user.role == UserRole.PARENT
        assert Permission.READ_CHILD in user.permissions

    @pytest.mark.asyncio
    async def test_user_authentication(self, auth_service):
        """Test user authentication."""
        # Create user first
        import secrets

        test_password = secrets.token_urlsafe(16)
        await auth_service.create_user(
            "authuser", "auth@example.com", test_password, UserRole.PARENT
        )

        # Test successful authentication
        user = await auth_service.authenticate_user("authuser", test_password)
        assert user is not None
        assert user.username == "authuser"

        # Test failed authentication
        user = await auth_service.authenticate_user(
            "authuser", "wrongpassword"
        )
        assert user is None

    @pytest.mark.asyncio
    async def test_jwt_token_creation(self, auth_service):
        """Test JWT token creation and verification."""
        import secrets

        test_password2 = secrets.token_urlsafe(16)
        user = await auth_service.create_user(
            "tokenuser", "token@example.com", test_password2, UserRole.PARENT
        )

        # Create token
        token = await auth_service.create_access_token(user)
        assert token is not None
        assert isinstance(token, str)

        # Verify token
        verified_user = await auth_service.verify_token(token)
        assert verified_user is not None
        assert verified_user.id == user.id

    @pytest.mark.asyncio
    async def test_api_key_creation(self, auth_service):
        """Test API key creation and verification."""
        import secrets

        test_password3 = secrets.token_urlsafe(16)
        user = await auth_service.create_user(
            "apikeyuser",
            "apikey@example.com",
            test_password3,
            UserRole.SERVICE,
        )

        permissions = {Permission.READ_CHILD, Permission.WRITE_CHILD}

        # Create API key
        api_key = await auth_service.create_api_key(
            user.id, "Test API Key", permissions
        )

        assert api_key.name == "Test API Key"
        assert api_key.permissions == permissions

        # Verify API key
        verified_key = await auth_service.verify_api_key(api_key.key)
        assert verified_key is not None
        assert verified_key.user_id == user.id

    def test_permission_checking(self, auth_service):
        """Test permission checking."""
        # Create users with different roles
        admin_user = User(
            id="admin-test",
            username="admin",
            email="admin@test.com",
            role=UserRole.ADMIN,
            permissions=auth_service.RolePermissions.get_permissions(
                UserRole.ADMIN
            ),
        )

        parent_user = User(
            id="parent-test",
            username="parent",
            email="parent@test.com",
            role=UserRole.PARENT,
            permissions=auth_service.RolePermissions.get_permissions(
                UserRole.PARENT
            ),
            children_ids=["child-123"],
        )

        # Test admin permissions
        assert (
            auth_service.check_permission(admin_user, Permission.READ_CHILD)
            is True
        )
        assert (
            auth_service.check_permission(admin_user, Permission.ADMIN_SYSTEM)
            is False
        )

        # Test parent permissions
        assert (
            auth_service.check_permission(parent_user, Permission.READ_CHILD)
            is True
        )
        assert (
            auth_service.check_permission(parent_user, Permission.DELETE_CHILD)
            is False
        )

        # Test child access
        assert (
            auth_service.check_child_access(parent_user, "child-123") is True
        )
        assert (
            auth_service.check_child_access(parent_user, "child-456") is False
        )
