"""Pytest Configuration and Fixtures with Real Database"""

import asyncio
import os
import sys
from datetime import datetime
from uuid import uuid4
import tempfile

import pytest
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import text

from src.infrastructure.config.settings import Settings
from src.infrastructure.di.container import Container
from src.infrastructure.persistence.database_manager import Database
from src.domain.models.models_infra import Base

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Use in-memory SQLite for tests to ensure clean state
TEST_DB_URL = "sqlite+aiosqlite:///:memory:"
os.environ["DATABASE_URL"] = TEST_DB_URL
os.environ["ASYNC_DATABASE_URL"] = TEST_DB_URL
os.environ["ENVIRONMENT"] = "testing"
os.environ["REDIS_URL"] = "redis://localhost:6379/1"  # Use different Redis DB for tests


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def test_settings():
    """Create test settings with dynamically generated secure keys."""
    import secrets

    from cryptography.fernet import Fernet

    # Generate secure test keys dynamically - never hardcode
    test_secret_key = secrets.token_urlsafe(32)
    test_jwt_secret = secrets.token_urlsafe(32)
    test_coppa_key = Fernet.generate_key().decode()

    return Settings(
        ENVIRONMENT="test",
        DEBUG=True,
        SECRET_KEY=os.getenv("TEST_SECRET_KEY", test_secret_key),
        JWT_SECRET_KEY=os.getenv("TEST_JWT_SECRET", test_jwt_secret),
        JWT_ALGORITHM="HS256",
        JWT_EXPIRATION_HOURS=24,
        DATABASE_URL=os.getenv("TEST_DATABASE_URL", "sqlite+aiosqlite:///:memory:"),
        REDIS_URL=os.getenv("TEST_REDIS_URL", "redis://localhost:6379/15"),
        OPENAI_API_KEY=os.getenv(
            "TEST_OPENAI_API_KEY", "sk-test-key-not-real-for-testing-only"
        ),
        OPENAI_MODEL="gpt-4-turbo-preview",
        COPPA_ENCRYPTION_KEY=os.getenv("TEST_COPPA_KEY", test_coppa_key),
        RATE_LIMIT_PER_MINUTE=60,
        ALLOWED_HOSTS=["testserver", "localhost"],
        LOG_LEVEL="DEBUG",
        SENTRY_DSN=None,
    )


@pytest.fixture(scope="session")
async def test_database():
    """Create real test database with in-memory SQLite."""
    # Create real database instance with test URL
    db = Database(database_url=TEST_DB_URL)

    # Initialize database and create all tables
    await db.init_db()

    # Create all tables from models
    engine = create_async_engine(TEST_DB_URL)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield db

    # Cleanup - close database connections
    await db.close()


@pytest.fixture
async def db_session(test_database):
    """Create a real database session for tests."""
    async with test_database.get_session() as session:
        # Start transaction for test isolation
        trans = await session.begin()
        yield session
        # Rollback transaction to keep tests isolated
        await trans.rollback()
        await session.rollback()


@pytest.fixture(scope="session")
def test_container(test_settings, test_database):
    """Create test dependency injection container."""
    container = Container()
    container.settings.override(test_settings)
    container.database.override(test_database)
    return container


@pytest.fixture
def mock_redis():
    """Create mock Redis client."""
    redis = AsyncMock()
    redis.get = AsyncMock(return_value=None)
    redis.setex = AsyncMock(return_value=True)
    redis.delete = AsyncMock(return_value=True)
    redis.exists = AsyncMock(return_value=False)
    redis.incr = AsyncMock(return_value=1)
    redis.expire = AsyncMock(return_value=True)
    return redis


@pytest.fixture
def mock_openai_client():
    """Create mock OpenAI client."""
    client = AsyncMock()

    # Mock chat completions
    client.chat.completions.create = AsyncMock(
        return_value=MagicMock(  # Using MagicMock for more flexible attribute access
            choices=[
                MagicMock(
                    message=MagicMock(
                        content="This is a safe, age-appropriate response.",
                        role="assistant",  # Add role attribute
                    )
                )
            ],
            # Add a mock ID for the completion object, similar to production
            id=f"chatcmpl-{uuid4().hex}",
            model="mock-gpt-4-turbo",  # Reflects a production model name
            object="chat.completion",
            created=int(datetime.now().timestamp()),  # Timestamp for creation
            usage=MagicMock(
                prompt_tokens=10, completion_tokens=20, total_tokens=30
            ),  # Usage stats
        )
    )

    # Mock moderations
    client.moderations.create = AsyncMock(
        return_value=MagicMock(  # Using MagicMock for more flexible attribute access
            id=f"mod-{uuid4().hex}",  # Add a mock ID for the moderation object
            model="text-moderation-007",  # Reflects a production model name
            results=[
                MagicMock(
                    flagged=False,  # Explicitly state flagged status
                    categories=MagicMock(
                        hate=False,
                        hate_threatening=False,
                        self_harm=False,
                        sexual=False,
                        sexual_minors=False,
                        violence=False,
                        harassment=False,
                        harassment_threatening=False,
                        self_harm_instructions=False,
                        self_harm_intent=False,
                        violence_graphic=False,
                    ),
                    category_scores=MagicMock(
                        hate=0.001,
                        hate_threatening=0.0001,
                        self_harm=0.0001,
                        sexual=0.0001,
                        sexual_minors=0.0001,
                        violence=0.001,
                        harassment=0.001,
                        harassment_threatening=0.0001,
                        self_harm_instructions=0.0001,
                        self_harm_intent=0.0001,
                        violence_graphic=0.0001,
                    ),
                )
            ],
        )
    )

    return client


@pytest.fixture
def sample_parent():
    """Create sample parent data."""
    return {
        "id": str(uuid4()),
        "email": "test.parent@example.com",
        "name": "Test Parent",
        "role": "parent",
        "is_active": True,
        "created_at": "2024-01-01T00:00:00Z",
    }


@pytest.fixture
def sample_child():
    """Create sample child data."""
    return {
        "id": str(uuid4()),
        "name": "Test Child",
        "age": 7,
        "parent_id": str(uuid4()),
        "interests": ["dinosaurs", "space", "art"],
        "language": "en",
        "personality_traits": ["curious", "friendly"],
        "created_at": "2024-01-01T00:00:00Z",
    }


@pytest.fixture
def auth_headers(sample_parent):
    """Create authentication headers with dynamic secure key."""
    import secrets

    # from src.infrastructure.security.real_auth_service import (
    #     ProductionAuthService,
    # )

    # Mock auth service since real_auth_service has import issues
    token = f"test-token-{secrets.token_urlsafe(16)}"
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def mock_coppa_service():
    """Create mock COPPA service."""
    service = AsyncMock()

    service.validate_child_age = AsyncMock(
        return_value={
            "compliant": True,
            "severity": "none",
            "reason": "Age within COPPA compliant range",
            "legal_risk": "none",
        }
    )

    service.validate_parental_consent = AsyncMock(
        return_value={
            "valid": True,
            "missing_fields": [],
            "invalid_fields": [],
            "compliance_score": 100,
        }
    )

    service.encrypt_child_data = AsyncMock(side_effect=lambda data: f"encrypted_{data}")

    service.decrypt_child_data = AsyncMock(
        side_effect=lambda data: data.replace("encrypted_", "")
    )

    return service


@pytest.fixture(autouse=True)
def reset_singletons():
    """Reset singleton instances between tests."""
    # Reset database service
    from src.infrastructure.persistence.real_database_service import (
        reset_database_service,
    )

    reset_database_service()

    yield

    # Cleanup after test
    reset_database_service()


@pytest.fixture
def mock_email_service():
    """Create mock email service."""
    service = AsyncMock()
    service.send_email = AsyncMock(return_value=True)
    service.send_verification_email = AsyncMock(return_value=True)
    service.send_safety_alert = AsyncMock(return_value=True)
    return service


# Pytest plugins configuration
pytest_plugins = []


def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers",
        "slow: marks tests as slow (deselect with '-m \"not slow\"')",
    )
    config.addinivalue_line("markers", "integration: marks tests as integration tests")
    config.addinivalue_line("markers", "e2e: marks tests as end-to-end tests")
    config.addinivalue_line("markers", "security: marks tests as security-related")
    config.addinivalue_line("markers", "unit: Unit tests")
    config.addinivalue_line("markers", "child_safety: Child safety tests")


# Test environment setup
os.environ["TESTING"] = "true"
os.environ["ENVIRONMENT"] = "testing"


@pytest.fixture
def mock_udid() -> str:
    """Generates a dynamic UDID for testing."""
    return str(uuid4())


@pytest.fixture
def mock_parent_email() -> str:
    """Generates a dynamic parent email for testing."""
    return f"parent_{uuid4()}@example.com"


@pytest.fixture
def mock_child_name() -> str:
    """Generates a dynamic child name for testing."""
    return f"Child_{uuid4().hex[:8]}"


@pytest.fixture
def mock_child_age() -> int:
    """Generates a dynamic child age for testing (between 2 and 12 for COPPA)."""
    import random

    return random.randint(2, 12)


@pytest.fixture
def mock_voice_id() -> str:
    """Generates a dynamic voice ID for testing."""
    return f"voice_{uuid4().hex[:8]}"


@pytest.fixture
def mock_ai_response_text() -> str:
    """Generates dynamic AI response text for testing."""
    return f"Hello from AI Teddy Bear! This is a test response generated at {datetime.now().isoformat()}."


@pytest.fixture
def mock_ai_audio_content() -> bytes:
    """Generates dynamic mock audio content for testing."""
    return f"mock_audio_content_{uuid4().hex}".encode()


@pytest.fixture
def mock_conversation_id() -> str:
    """Generates a dynamic conversation ID for testing."""
    return f"conv_{uuid4().hex[:8]}"
