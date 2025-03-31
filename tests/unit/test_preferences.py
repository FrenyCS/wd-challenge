from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import HTTPException
from pydantic import ValidationError

from app.models import UserPreference
from app.routes.preferences import (
    PreferencesPayload,
    create_or_replace_preferences,
    get_preferences,
)


@pytest.mark.asyncio
async def test_get_preferences():
    # Mock async DB session
    mock_db = AsyncMock()

    # Mock user preferences fetched from DB
    mock_preferences = UserPreference(
        user_id="user123",
        email="user@example.com",
        phone_number="1234567890",
        email_enabled=True,
        sms_enabled=False,
    )
    # Scalar result should directly return the mock_preferences object
    mock_db.execute.return_value.scalar_one_or_none = MagicMock(
        return_value=mock_preferences
    )

    # Call the function
    with patch("app.db.get_db", return_value=mock_db):
        response = await get_preferences(user_id="user123", db=mock_db)

    # Assert response
    assert response.email_enabled == mock_preferences.email_enabled
    assert response.sms_enabled == mock_preferences.sms_enabled
    assert response.email == mock_preferences.email
    assert response.phone_number == mock_preferences.phone_number


@pytest.mark.asyncio
async def test_get_preferences_not_found():
    # Mock async DB session
    mock_db = AsyncMock()

    # No preferences found in DB
    mock_db.execute.return_value.scalar_one_or_none = MagicMock(return_value=None)

    # Call the function and catch exception
    with patch("app.db.get_db", return_value=mock_db):
        with pytest.raises(HTTPException) as exc:
            await get_preferences(user_id="user123", db=mock_db)

    # Assert exception details
    assert exc.value.status_code == 404
    assert exc.value.detail == "User preferences not found"


@pytest.mark.asyncio
async def test_create_or_replace_preferences_create_new():
    # Mock async DB session
    mock_db = AsyncMock()

    # No existing preference found
    mock_db.execute.return_value.scalar_one_or_none = MagicMock(return_value=None)

    # Mock payload
    payload = {
        "email_enabled": True,
        "sms_enabled": False,
        "email": "user@example.com",
        "phone_number": None,
    }

    # Convert payload dict to PreferencesPayload object
    payload_obj = PreferencesPayload(**payload)

    # Call the function
    with patch("app.db.get_db", return_value=mock_db):
        response = await create_or_replace_preferences(
            user_id="user123", payload=payload_obj, db=mock_db
        )

    # Assert response
    assert response.email_enabled == payload["email_enabled"]
    assert response.sms_enabled == payload["sms_enabled"]
    assert response.email == payload["email"]
    assert response.phone_number == payload["phone_number"]

    # Ensure DB commit was called
    mock_db.commit.assert_called_once()


@pytest.mark.asyncio
async def test_create_or_replace_preferences_update_existing():
    # Mock async DB session
    mock_db = AsyncMock()

    # Existing preference found
    existing_preferences = UserPreference(
        user_id="user123",
        email="old_email@example.com",
        phone_number="9876543210",
        email_enabled=False,
        sms_enabled=True,
    )
    mock_db.execute.return_value.scalar_one_or_none = MagicMock(
        return_value=existing_preferences
    )

    # Mock payload
    payload = {
        "email_enabled": True,
        "sms_enabled": False,
        "email": "new_email@example.com",
        "phone_number": "1234567890",
    }

    # Convert payload dict to PreferencesPayload object
    payload_obj = PreferencesPayload(**payload)

    # Call the function
    with patch("app.db.get_db", return_value=mock_db):
        response = await create_or_replace_preferences(
            user_id="user123", payload=payload_obj, db=mock_db
        )

    # Assert response
    assert response.email_enabled == payload["email_enabled"]
    assert response.sms_enabled == payload["sms_enabled"]
    assert response.email == payload["email"]
    assert response.phone_number == payload["phone_number"]

    # Ensure DB commit was called
    mock_db.commit.assert_called_once()


@pytest.mark.asyncio
async def test_create_or_replace_preferences_invalid_payload():
    # Mock invalid payload (missing required fields)
    payload = {
        "email_enabled": True,
        # Missing "sms_enabled", "email", and "phone_number"
    }

    # Attempt to create PreferencesPayload object and expect validation error
    with pytest.raises(ValidationError) as exc:
        PreferencesPayload(**payload)

    # Assert the validation error contains the missing field
    assert "sms_enabled" in str(exc.value)
