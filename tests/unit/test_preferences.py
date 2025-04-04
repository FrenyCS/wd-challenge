from unittest.mock import MagicMock, patch

import pytest
from fastapi import HTTPException
from pydantic import ValidationError

from app.routes.preferences import (
    PreferencesPayload,
    create_or_replace_preferences,
    get_preferences,
)


@pytest.mark.asyncio
async def test_get_preferences(mock_db, mock_user_preferences):
    # Use shared and module-specific fixtures
    mock_db.execute.return_value.scalar_one_or_none.return_value = mock_user_preferences

    # Call the function
    with patch("app.db.get_db", return_value=mock_db):
        response = await get_preferences(user_id="user123", db=mock_db)

    # Assert response
    assert response.email_enabled == mock_user_preferences.email_enabled
    assert response.sms_enabled == mock_user_preferences.sms_enabled
    assert response.email == mock_user_preferences.email
    assert response.phone_number == mock_user_preferences.phone_number


@pytest.mark.asyncio
async def test_get_preferences_not_found(mock_db):
    # Use shared and module-specific fixtures
    mock_db.execute.return_value.scalar_one_or_none = MagicMock(return_value=None)

    # Call the function and catch exception
    with patch("app.db.get_db", return_value=mock_db):
        with pytest.raises(HTTPException) as exc:
            await get_preferences(user_id="user123", db=mock_db)

    # Assert exception details
    assert exc.value.status_code == 404
    assert exc.value.detail == "User preferences not found"


@pytest.mark.asyncio
async def test_create_or_replace_preferences_create_new(mock_db):
    # Use shared and module-specific fixtures
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
async def test_create_or_replace_preferences_update_existing(
    mock_db, mock_user_preferences
):
    # Use shared and module-specific fixtures
    mock_db.execute.return_value.scalar_one_or_none.return_value = mock_user_preferences

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
