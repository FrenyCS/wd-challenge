import pytest
from unittest.mock import AsyncMock, MagicMock
from app.models import UserPreference

@pytest.fixture
def mock_db():
    """Fixture for a mock async database session."""
    db = AsyncMock()
    db.add = AsyncMock()
    db.commit = AsyncMock()
    db.execute.return_value.scalar_one_or_none = MagicMock()
    return db

@pytest.fixture
def mock_user_preferences():
    """Fixture for mock user preferences."""
    return UserPreference(
        user_id="user123",
        email="user@example.com",
        phone_number="+1234567890",
        email_enabled=True,
        sms_enabled=True,
    )
