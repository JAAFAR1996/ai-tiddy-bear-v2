"""
Test User Repository

Comprehensive unit tests for UserRepository with security and error handling coverage.
"""
import pytest
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

from sqlalchemy.exc import IntegrityError, DataError
from sqlalchemy.orm.exc import NoResultFound

from src.infrastructure.persistence.repositories.user_repository import UserRepository
from src.infrastructure.persistence.models.user_model import UserModel
from src.infrastructure.persistence.database import Database
from src.infrastructure.security.database_input_validator import SecurityError


@pytest.fixture
def mock_database():
    """Create mock database instance."""
    database = MagicMock(spec=Database)
    database.get_session = MagicMock()
    return database


@pytest.fixture
def user_repository(mock_database):
    """Create UserRepository instance with mocked dependencies."""
    return UserRepository(mock_database)


@pytest.fixture
def sample_user_data():
    """Sample user data for testing."""
    return {
        "email": "parent@example.com",
        "hashed_password": "hashed_password_123",
        "role": "parent"
    }


class TestUserRepositoryCreate:
    """Test user creation functionality."""
    
    @pytest.mark.asyncio
    async def test_create_user_success(self, user_repository, mock_database, sample_user_data):
        """Test successful user creation."""
        # Arrange
        mock_session = AsyncMock()
        mock_safe_session = MagicMock()
        mock_safe_session.safe_select = AsyncMock()
        mock_safe_session.safe_select.return_value.rowcount = 0
        
        mock_database.get_session.return_value.__aenter__.return_value = mock_session
        
        with patch('src.infrastructure.persistence.repositories.user_repository.create_safe_database_session',
                  return_value=mock_safe_session):
            with patch('src.infrastructure.persistence.repositories.user_repository.validate_database_operation',
                      return_value={"data": sample_user_data}):
                # Act
                user_id = await user_repository.create_user(**sample_user_data)
                
                # Assert
                assert user_id is not None
                assert isinstance(user_id, str)
                mock_session.add.assert_called_once()
                mock_session.commit.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_create_user_already_exists(self, user_repository, mock_database, sample_user_data):
        """Test user creation when email already exists."""
        # Arrange
        mock_session = AsyncMock()
        mock_safe_session = MagicMock()
        mock_safe_session.safe_select = AsyncMock()
        mock_safe_session.safe_select.return_value.rowcount = 1  # User exists
        
        mock_database.get_session.return_value.__aenter__.return_value = mock_session
        
        with patch('src.infrastructure.persistence.repositories.user_repository.create_safe_database_session',
                  return_value=mock_safe_session):
            with patch('src.infrastructure.persistence.repositories.user_repository.validate_database_operation',
                      return_value={"data": sample_user_data}):
                # Act & Assert
                with pytest.raises(ValueError, match="already exists"):
                    await user_repository.create_user(**sample_user_data)
    
    @pytest.mark.asyncio
    async def test_create_user_security_violation(self, user_repository, mock_database, sample_user_data):
        """Test user creation with security violation."""
        # Arrange
        with patch('src.infrastructure.persistence.repositories.user_repository.validate_database_operation',
                  side_effect=SecurityError("SQL injection detected")):
            # Act & Assert
            with pytest.raises(ValueError, match="Invalid input data"):
                await user_repository.create_user(**sample_user_data)
    
    @pytest.mark.asyncio
    async def test_create_user_integrity_error(self, user_repository, mock_database, sample_user_data):
        """Test user creation with database integrity error."""
        # Arrange
        mock_session = AsyncMock()
        mock_session.commit.side_effect = IntegrityError("Constraint violation", None, None)
        
        mock_safe_session = MagicMock()
        mock_safe_session.safe_select = AsyncMock()
        mock_safe_session.safe_select.return_value.rowcount = 0
        
        mock_database.get_session.return_value.__aenter__.return_value = mock_session
        
        with patch('src.infrastructure.persistence.repositories.user_repository.create_safe_database_session',
                  return_value=mock_safe_session):
            with patch('src.infrastructure.persistence.repositories.user_repository.validate_database_operation',
                      return_value={"data": sample_user_data}):
                # Act & Assert
                with pytest.raises(ValueError, match="database constraint violation"):
                    await user_repository.create_user(**sample_user_data)
    
    @pytest.mark.asyncio
    async def test_create_user_generic_error(self, user_repository, mock_database, sample_user_data):
        """Test user creation with generic database error."""
        # Arrange
        mock_session = AsyncMock()
        mock_session.add.side_effect = Exception("Database connection lost")
        
        mock_safe_session = MagicMock()
        mock_safe_session.safe_select = AsyncMock()
        mock_safe_session.safe_select.return_value.rowcount = 0
        
        mock_database.get_session.return_value.__aenter__.return_value = mock_session
        
        with patch('src.infrastructure.persistence.repositories.user_repository.create_safe_database_session',
                  return_value=mock_safe_session):
            with patch('src.infrastructure.persistence.repositories.user_repository.validate_database_operation',
                      return_value={"data": sample_user_data}):
                # Act & Assert
                with pytest.raises(RuntimeError, match="Database error"):
                    await user_repository.create_user(**sample_user_data)


class TestUserRepositoryRead:
    """Test user retrieval functionality."""
    
    @pytest.mark.asyncio
    async def test_get_user_by_email_found(self, user_repository, mock_database):
        """Test retrieving existing user by email."""
        # Arrange
        mock_user = MagicMock(spec=UserModel)
        mock_user.id = str(uuid4())
        mock_user.email = "parent@example.com"
        mock_user.password_hash = "hashed_password"
        mock_user.role = "parent"
        mock_user.is_active = True
        mock_user.email_verified = True
        mock_user.created_at = datetime.utcnow()
        
        mock_session = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_user
        mock_session.execute.return_value = mock_result
        
        mock_database.get_session.return_value.__aenter__.return_value = mock_session
        
        # Act
        result = await user_repository.get_user_by_email("parent@example.com")
        
        # Assert
        assert result is not None
        assert result["email"] == "parent@example.com"
        assert result["role"] == "parent"
        assert "password_hash" in result
        assert "created_at" in result
    
    @pytest.mark.asyncio
    async def test_get_user_by_email_not_found(self, user_repository, mock_database):
        """Test retrieving non-existent user by email."""
        # Arrange
        mock_session = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result
        
        mock_database.get_session.return_value.__aenter__.return_value = mock_session
        
        # Act
        result = await user_repository.get_user_by_email("nonexistent@example.com")
        
        # Assert
        assert result is None
    
    @pytest.mark.asyncio
    async def test_get_user_by_email_database_error(self, user_repository, mock_database):
        """Test user retrieval with database error."""
        # Arrange
        mock_session = AsyncMock()
        mock_session.execute.side_effect = Exception("Connection timeout")
        
        mock_database.get_session.return_value.__aenter__.return_value = mock_session
        
        # Act & Assert
        with pytest.raises(RuntimeError, match="Database error"):
            await user_repository.get_user_by_email("parent@example.com")


class TestUserRepositoryUpdate:
    """Test user update functionality."""
    
    @pytest.mark.asyncio
    async def test_update_user_success(self, user_repository, mock_database):
        """Test successful user update."""
        # Arrange
        user_id = str(uuid4())
        updates = {"email_verified": True, "is_active": True}
        
        mock_session = AsyncMock()
        mock_result = MagicMock()
        mock_result.rowcount = 1
        mock_session.execute.return_value = mock_result
        
        mock_database.get_session.return_value.__aenter__.return_value = mock_session
        
        with patch('src.infrastructure.persistence.repositories.user_repository.validate_database_operation',
                  return_value={"data": updates}):
            # Act
            result = await user_repository.update_user(user_id, updates)
            
            # Assert
            assert result is True
            mock_session.execute.assert_called_once()
            mock_session.commit.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_update_user_not_found(self, user_repository, mock_database):
        """Test updating non-existent user."""
        # Arrange
        user_id = str(uuid4())
        updates = {"email_verified": True}
        
        mock_session = AsyncMock()
        mock_result = MagicMock()
        mock_result.rowcount = 0  # No rows updated
        mock_session.execute.return_value = mock_result
        
        mock_database.get_session.return_value.__aenter__.return_value = mock_session
        
        with patch('src.infrastructure.persistence.repositories.user_repository.validate_database_operation',
                  return_value={"data": updates}):
            # Act
            result = await user_repository.update_user(user_id, updates)
            
            # Assert
            assert result is False
    
    @pytest.mark.asyncio
    async def test_update_user_security_violation(self, user_repository, mock_database):
        """Test user update with security violation."""
        # Arrange
        user_id = str(uuid4())
        updates = {"role": "'; DROP TABLE users; --"}
        
        with patch('src.infrastructure.persistence.repositories.user_repository.validate_database_operation',
                  side_effect=SecurityError("SQL injection detected")):
            # Act & Assert
            with pytest.raises(ValueError, match="Invalid update data"):
                await user_repository.update_user(user_id, updates)
    
    @pytest.mark.asyncio
    async def test_update_user_database_error(self, user_repository, mock_database):
        """Test user update with database error."""
        # Arrange
        user_id = str(uuid4())
        updates = {"email_verified": True}
        
        mock_session = AsyncMock()
        mock_session.execute.side_effect = Exception("Database locked")
        
        mock_database.get_session.return_value.__aenter__.return_value = mock_session
        
        with patch('src.infrastructure.persistence.repositories.user_repository.validate_database_operation',
                  return_value={"data": updates}):
            # Act & Assert
            with pytest.raises(RuntimeError, match="Database error"):
                await user_repository.update_user(user_id, updates)


class TestUserRepositoryEdgeCases:
    """Test edge cases and boundary conditions."""
    
    @pytest.mark.asyncio
    async def test_create_user_empty_email(self, user_repository, mock_database):
        """Test user creation with empty email."""
        # Act & Assert
        with pytest.raises(ValueError):
            await user_repository.create_user("", "password", "parent")
    
    @pytest.mark.asyncio
    async def test_create_user_invalid_role(self, user_repository, mock_database):
        """Test user creation with invalid role."""
        # Arrange
        with patch('src.infrastructure.persistence.repositories.user_repository.validate_database_operation',
                  side_effect=SecurityError("Invalid role")):
            # Act & Assert
            with pytest.raises(ValueError, match="Invalid input data"):
                await user_repository.create_user("test@example.com", "password", "invalid_role")
    
    @pytest.mark.asyncio
    async def test_update_user_empty_updates(self, user_repository, mock_database):
        """Test user update with empty updates dictionary."""
        # Arrange
        user_id = str(uuid4())
        
        with patch('src.infrastructure.persistence.repositories.user_repository.validate_database_operation',
                  return_value={"data": {}}):
            mock_session = AsyncMock()
            mock_result = MagicMock()
            mock_result.rowcount = 0
            mock_session.execute.return_value = mock_result
            
            mock_database.get_session.return_value.__aenter__.return_value = mock_session
            
            # Act
            result = await user_repository.update_user(user_id, {})
            
            # Assert
            assert result is False