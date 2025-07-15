"""
Test Child Repository

Comprehensive unit tests for ChildRepository with COPPA compliance and security coverage.
"""
import pytest
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

from sqlalchemy.exc import IntegrityError
from src.infrastructure.persistence.repositories.child_repository import ChildRepository
from src.infrastructure.persistence.models.child_model import ChildModel
from src.infrastructure.persistence.database import Database
from src.infrastructure.security.database_input_validator import SecurityError


@pytest.fixture
def mock_database():
    """Create mock database instance."""
    database = MagicMock(spec=Database)
    database.get_session = MagicMock()
    return database


@pytest.fixture
def mock_consent_manager():
    """Create mock consent manager."""
    consent_manager = MagicMock()
    consent_manager.has_consent = MagicMock(return_value=True)
    return consent_manager


@pytest.fixture
def child_repository(mock_database, mock_consent_manager):
    """Create ChildRepository instance with mocked dependencies."""
    with patch('src.infrastructure.persistence.repositories.child_repository.get_consent_manager',
              return_value=mock_consent_manager):
        return ChildRepository(mock_database)


@pytest.fixture
def sample_child_data():
    """Sample child data for testing."""
    return {
        "name": "Timmy",
        "age": 8,
        "preferences": {
            "favorite_color": "blue",
            "favorite_animal": "dinosaur",
            "interests": ["space", "robots"]
        }
    }


class TestChildRepositoryCreate:
    """Test child profile creation functionality."""
    
    @pytest.mark.asyncio
    async def test_create_child_success(self, child_repository, mock_database, 
                                       mock_consent_manager, sample_child_data):
        """Test successful child profile creation with parental consent."""
        # Arrange
        parent_id = str(uuid4())
        mock_session = AsyncMock()
        mock_database.get_session.return_value.__aenter__.return_value = mock_session
        
        with patch('src.infrastructure.persistence.repositories.child_repository.validate_database_operation',
                  return_value={"data": sample_child_data}):
            # Act
            child_id = await child_repository.create_child(parent_id, sample_child_data)
            
            # Assert
            assert child_id is not None
            assert isinstance(child_id, str)
            mock_consent_manager.has_consent.assert_called_once_with(parent_id)
            mock_session.add.assert_called_once()
            mock_session.commit.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_create_child_no_consent(self, child_repository, mock_consent_manager, sample_child_data):
        """Test child creation without parental consent (COPPA violation)."""
        # Arrange
        parent_id = str(uuid4())
        mock_consent_manager.has_consent.return_value = False
        
        # Act & Assert
        with pytest.raises(ValueError, match="Parent has not provided COPPA consent"):
            await child_repository.create_child(parent_id, sample_child_data)
    
    @pytest.mark.asyncio
    async def test_create_child_invalid_age(self, child_repository, mock_database, sample_child_data):
        """Test child creation with invalid age."""
        # Arrange
        parent_id = str(uuid4())
        invalid_data = sample_child_data.copy()
        invalid_data["age"] = -5
        
        with patch('src.infrastructure.persistence.repositories.child_repository.validate_database_operation',
                  side_effect=SecurityError("Invalid age")):
            # Act & Assert
            with pytest.raises(ValueError, match="Invalid child data"):
                await child_repository.create_child(parent_id, invalid_data)
    
    @pytest.mark.asyncio
    async def test_create_child_security_violation(self, child_repository, mock_database, sample_child_data):
        """Test child creation with SQL injection attempt."""
        # Arrange
        parent_id = str(uuid4())
        malicious_data = sample_child_data.copy()
        malicious_data["name"] = "'; DROP TABLE children; --"
        
        with patch('src.infrastructure.persistence.repositories.child_repository.validate_database_operation',
                  side_effect=SecurityError("SQL injection detected")):
            # Act & Assert
            with pytest.raises(ValueError, match="Invalid child data"):
                await child_repository.create_child(parent_id, malicious_data)
    
    @pytest.mark.asyncio
    async def test_create_child_database_error(self, child_repository, mock_database, sample_child_data):
        """Test child creation with database error."""
        # Arrange
        parent_id = str(uuid4())
        mock_session = AsyncMock()
        mock_session.commit.side_effect = Exception("Database connection lost")
        mock_database.get_session.return_value.__aenter__.return_value = mock_session
        
        with patch('src.infrastructure.persistence.repositories.child_repository.validate_database_operation',
                  return_value={"data": sample_child_data}):
            # Act & Assert
            with pytest.raises(RuntimeError, match="Database error"):
                await child_repository.create_child(parent_id, sample_child_data)


class TestChildRepositoryRead:
    """Test child profile retrieval functionality."""
    
    @pytest.mark.asyncio
    async def test_get_child_success(self, child_repository, mock_database):
        """Test successful child profile retrieval."""
        # Arrange
        child_id = str(uuid4())
        parent_id = str(uuid4())
        
        mock_child = MagicMock(spec=ChildModel)
        mock_child.id = child_id
        mock_child.parent_id = parent_id
        mock_child.name = "Timmy"
        mock_child.age = 8
        mock_child.preferences = {"favorite_color": "blue"}
        mock_child.created_at = datetime.utcnow()
        
        mock_session = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_child
        mock_session.execute.return_value = mock_result
        
        mock_database.get_session.return_value.__aenter__.return_value = mock_session
        
        # Act
        result = await child_repository.get_child(child_id)
        
        # Assert
        assert result is not None
        assert result["id"] == child_id
        assert result["parent_id"] == parent_id
        assert result["name"] == "Timmy"
        assert result["age"] == 8
        assert "created_at" in result
    
    @pytest.mark.asyncio
    async def test_get_child_not_found(self, child_repository, mock_database):
        """Test retrieving non-existent child profile."""
        # Arrange
        mock_session = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result
        
        mock_database.get_session.return_value.__aenter__.return_value = mock_session
        
        # Act
        result = await child_repository.get_child(str(uuid4()))
        
        # Assert
        assert result is None
    
    @pytest.mark.asyncio
    async def test_get_children_by_parent_success(self, child_repository, mock_database):
        """Test retrieving all children for a parent."""
        # Arrange
        parent_id = str(uuid4())
        
        # Create mock children
        children = []
        for i in range(3):
            mock_child = MagicMock(spec=ChildModel)
            mock_child.id = str(uuid4())
            mock_child.parent_id = parent_id
            mock_child.name = f"Child{i}"
            mock_child.age = 5 + i
            mock_child.preferences = {}
            mock_child.created_at = datetime.utcnow()
            children.append(mock_child)
        
        mock_session = AsyncMock()
        mock_result = MagicMock()
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = children
        mock_result.scalars.return_value = mock_scalars
        mock_session.execute.return_value = mock_result
        
        mock_database.get_session.return_value.__aenter__.return_value = mock_session
        
        # Act
        result = await child_repository.get_children_by_parent(parent_id)
        
        # Assert
        assert len(result) == 3
        for i, child in enumerate(result):
            assert child["name"] == f"Child{i}"
            assert child["parent_id"] == parent_id
    
    @pytest.mark.asyncio
    async def test_get_children_by_parent_empty(self, child_repository, mock_database):
        """Test retrieving children for parent with no children."""
        # Arrange
        parent_id = str(uuid4())
        
        mock_session = AsyncMock()
        mock_result = MagicMock()
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = []
        mock_result.scalars.return_value = mock_scalars
        mock_session.execute.return_value = mock_result
        
        mock_database.get_session.return_value.__aenter__.return_value = mock_session
        
        # Act
        result = await child_repository.get_children_by_parent(parent_id)
        
        # Assert
        assert result == []


class TestChildRepositoryUpdate:
    """Test child profile update functionality."""
    
    @pytest.mark.asyncio
    async def test_update_child_success(self, child_repository, mock_database):
        """Test successful child profile update."""
        # Arrange
        child_id = str(uuid4())
        updates = {
            "age": 9,
            "preferences": {"favorite_color": "green", "favorite_animal": "tiger"}
        }
        
        mock_session = AsyncMock()
        mock_result = MagicMock()
        mock_result.rowcount = 1
        mock_session.execute.return_value = mock_result
        
        mock_database.get_session.return_value.__aenter__.return_value = mock_session
        
        with patch('src.infrastructure.persistence.repositories.child_repository.validate_database_operation',
                  return_value={"data": updates}):
            # Act
            result = await child_repository.update_child(child_id, updates)
            
            # Assert
            assert result is True
            mock_session.execute.assert_called_once()
            mock_session.commit.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_update_child_parent_id_ignored(self, child_repository, mock_database):
        """Test that parent_id cannot be updated (security feature)."""
        # Arrange
        child_id = str(uuid4())
        updates = {
            "parent_id": str(uuid4()),  # Should be ignored
            "age": 9
        }
        
        mock_session = AsyncMock()
        mock_result = MagicMock()
        mock_result.rowcount = 1
        mock_session.execute.return_value = mock_result
        
        mock_database.get_session.return_value.__aenter__.return_value = mock_session
        
        with patch('src.infrastructure.persistence.repositories.child_repository.validate_database_operation',
                  return_value={"data": {"age": 9}}):  # parent_id removed
            # Act
            result = await child_repository.update_child(child_id, updates)
            
            # Assert
            assert result is True
            # Verify parent_id was not in validated data
    
    @pytest.mark.asyncio
    async def test_update_child_not_found(self, child_repository, mock_database):
        """Test updating non-existent child profile."""
        # Arrange
        child_id = str(uuid4())
        updates = {"age": 9}
        
        mock_session = AsyncMock()
        mock_result = MagicMock()
        mock_result.rowcount = 0
        mock_session.execute.return_value = mock_result
        
        mock_database.get_session.return_value.__aenter__.return_value = mock_session
        
        with patch('src.infrastructure.persistence.repositories.child_repository.validate_database_operation',
                  return_value={"data": updates}):
            # Act
            result = await child_repository.update_child(child_id, updates)
            
            # Assert
            assert result is False
    
    @pytest.mark.asyncio
    async def test_update_child_security_violation(self, child_repository, mock_database):
        """Test child update with security violation."""
        # Arrange
        child_id = str(uuid4())
        updates = {"name": "'; UPDATE children SET parent_id = '123' WHERE 1=1; --"}
        
        with patch('src.infrastructure.persistence.repositories.child_repository.validate_database_operation',
                  side_effect=SecurityError("SQL injection detected")):
            # Act & Assert
            with pytest.raises(ValueError, match="Invalid update data"):
                await child_repository.update_child(child_id, updates)


class TestChildRepositoryEdgeCases:
    """Test edge cases and COPPA compliance scenarios."""
    
    @pytest.mark.asyncio
    async def test_create_child_age_boundary_cases(self, child_repository, mock_database, sample_child_data):
        """Test child creation with boundary age values."""
        parent_id = str(uuid4())
        
        # Test minimum age (0)
        data_age_0 = sample_child_data.copy()
        data_age_0["age"] = 0
        
        mock_session = AsyncMock()
        mock_database.get_session.return_value.__aenter__.return_value = mock_session
        
        with patch('src.infrastructure.persistence.repositories.child_repository.validate_database_operation',
                  return_value={"data": data_age_0}):
            child_id = await child_repository.create_child(parent_id, data_age_0)
            assert child_id is not None
    
    @pytest.mark.asyncio
    async def test_create_child_maximum_preferences(self, child_repository, mock_database):
        """Test child creation with large preferences object."""
        # Arrange
        parent_id = str(uuid4())
        large_preferences = {
            f"pref_{i}": f"value_{i}" for i in range(100)
        }
        child_data = {
            "name": "TestChild",
            "age": 8,
            "preferences": large_preferences
        }
        
        mock_session = AsyncMock()
        mock_database.get_session.return_value.__aenter__.return_value = mock_session
        
        with patch('src.infrastructure.persistence.repositories.child_repository.validate_database_operation',
                  return_value={"data": child_data}):
            # Act
            child_id = await child_repository.create_child(parent_id, child_data)
            
            # Assert
            assert child_id is not None
    
    @pytest.mark.asyncio
    async def test_get_children_by_parent_database_error(self, child_repository, mock_database):
        """Test handling database errors when retrieving children."""
        # Arrange
        parent_id = str(uuid4())
        mock_session = AsyncMock()
        mock_session.execute.side_effect = Exception("Connection timeout")
        
        mock_database.get_session.return_value.__aenter__.return_value = mock_session
        
        # Act & Assert
        with pytest.raises(RuntimeError, match="Database error"):
            await child_repository.get_children_by_parent(parent_id)