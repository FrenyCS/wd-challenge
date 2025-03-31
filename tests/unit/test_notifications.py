from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import HTTPException

from app.models import UserPreference
from app.routes.notifications import NotificationPayload, create_notification


@pytest.mark.asyncio
async def test_create_notification():
    # Mock async DB session ensuring add is an AsyncMock
    mock_db = AsyncMock()
    mock_db.add = AsyncMock()

    # Mock user preferences fetched from DB
    mock_preferences = UserPreference(
        user_id="user123",
        email="user@example.com",
        phone_number="+1234567890",
        email_enabled=True,
        sms_enabled=True,
    )
    mock_db.execute.return_value.scalar_one_or_none = MagicMock(
        return_value=mock_preferences
    )

    # Mock Celery tasks
    mock_send_email_task = MagicMock()
    mock_send_sms_task = MagicMock()

    # Mock datetime
    mock_now = datetime(2025, 1, 1, tzinfo=timezone.utc)

    with (
        patch("app.routes.notifications.send_email_task", mock_send_email_task),
        patch("app.routes.notifications.send_sms_task", mock_send_sms_task),
        patch("app.routes.notifications.datetime") as mock_datetime,
    ):
        mock_datetime.now.return_value = mock_now

        # Prepare payload
        payload = NotificationPayload(
            user_id="user123",
            subject="Test Notification",
            message="This is a test message",
            send_at=None,  # Immediate send
        )

        # Call the function
        response = await create_notification(payload, db=mock_db)

        # Assert response
        assert response["status"] == "queued"
        assert response["send_at"] == mock_now.isoformat()

        # Assert DB interactions
        mock_db.add.assert_called()  # Ensure notifications were added
        mock_db.commit.assert_called_once()

        # Assert Celery tasks were triggered
        mock_send_email_task.apply_async.assert_called_once()
        mock_send_sms_task.apply_async.assert_called_once()


@pytest.mark.asyncio
async def test_create_scheduled_notification():
    # Mock async DB session ensuring add is an AsyncMock
    mock_db = AsyncMock()
    mock_db.add = AsyncMock()

    # Mock user preferences fetched from DB
    mock_preferences = UserPreference(
        user_id="user123",
        email="user@example.com",
        phone_number="+1234567890",
        email_enabled=True,
        sms_enabled=True,
    )
    mock_db.execute.return_value.scalar_one_or_none = MagicMock(
        return_value=mock_preferences
    )

    # Mock Celery tasks
    mock_send_email_task = MagicMock()
    mock_send_sms_task = MagicMock()

    # Mock datetime
    mock_now = datetime(2025, 1, 1, tzinfo=timezone.utc)
    mock_future_time = datetime(2025, 1, 2, tzinfo=timezone.utc)  # Scheduled time

    with (
        patch("app.routes.notifications.send_email_task", mock_send_email_task),
        patch("app.routes.notifications.send_sms_task", mock_send_sms_task),
        patch("app.routes.notifications.datetime") as mock_datetime,
    ):
        mock_datetime.now.return_value = mock_now

        # Prepare payload
        payload = NotificationPayload(
            user_id="user123",
            subject="Scheduled Notification",
            message="This is a scheduled test message",
            send_at=mock_future_time,  # Scheduled send
        )

        # Call the function
        response = await create_notification(payload, db=mock_db)

        # Assert response
        assert response["status"] == "queued"
        assert response["send_at"] == mock_future_time.isoformat()

        # Assert DB interactions
        mock_db.add.assert_called()  # Ensure notifications were added
        mock_db.commit.assert_called_once()

        # Assert Celery tasks were triggered with ETA
        mock_send_email_task.apply_async.assert_called_once_with(
            kwargs={
                "user_id": "user123",
                "subject": "Scheduled Notification",
                "message": "This is a scheduled test message",
                "notification_id": mock_db.add.call_args[0][0].id,
                "recipient": "user@example.com",
            },
            eta=mock_future_time,
        )
        mock_send_sms_task.apply_async.assert_called_once_with(
            kwargs={
                "user_id": "user123",
                "subject": "Scheduled Notification",
                "message": "This is a scheduled test message",
                "notification_id": mock_db.add.call_args[0][0].id,
                "recipient": "+1234567890",
            },
            eta=mock_future_time,
        )


@pytest.mark.asyncio
async def test_create_notification_user_preferences_not_found():
    # Mock async DB session ensuring add is an AsyncMock
    mock_db = AsyncMock()
    mock_db.add = AsyncMock()

    # Simulate no user preferences found in DB
    mock_db.execute.return_value.scalar_one_or_none = MagicMock(return_value=None)

    # Prepare payload
    payload = NotificationPayload(
        user_id="user123",
        subject="Test Notification",
        message="This is a test message",
        send_at=None,  # Immediate send
    )

    # Call the function and expect an HTTPException
    with pytest.raises(HTTPException) as exc:
        await create_notification(payload, db=mock_db)

    # Assert exception details
    assert exc.value.status_code == 404
    assert exc.value.detail == "User preferences not found"

    # Ensure no DB interactions or Celery tasks were triggered
    mock_db.add.assert_not_called()
    mock_db.commit.assert_not_called()


@pytest.mark.asyncio
async def test_create_notification_disabled_channels():
    # Mock async DB session ensuring add is an AsyncMock
    mock_db = AsyncMock()
    mock_db.add = AsyncMock()

    # Mock user preferences with both channels disabled
    mock_preferences = UserPreference(
        user_id="user123",
        email="user@example.com",
        phone_number="+1234567890",
        email_enabled=False,
        sms_enabled=False,
    )
    mock_db.execute.return_value.scalar_one_or_none = MagicMock(
        return_value=mock_preferences
    )

    # Mock Celery tasks
    mock_send_email_task = MagicMock()
    mock_send_sms_task = MagicMock()

    with (
        patch("app.routes.notifications.send_email_task", mock_send_email_task),
        patch("app.routes.notifications.send_sms_task", mock_send_sms_task),
    ):
        # Prepare payload
        payload = NotificationPayload(
            user_id="user123",
            subject="Test Notification",
            message="This is a test message",
            send_at=None,  # Immediate send
        )

        # Call the function
        response = await create_notification(payload, db=mock_db)

        # Assert response
        assert response["status"] == "queued"
        assert response["send_at"] is not None  # Should still return a valid timestamp

        # Ensure no notifications were added to the DB
        mock_db.add.assert_not_called()
        mock_db.commit.assert_called_once()  # Commit is still called, but no records added

        # Ensure no Celery tasks were triggered
        mock_send_email_task.apply_async.assert_not_called()
        mock_send_sms_task.apply_async.assert_not_called()


@pytest.mark.asyncio
async def test_create_notification_invalid_payload():
    # Mock async DB session ensuring add is an AsyncMock
    mock_db = AsyncMock()
    mock_db.add = AsyncMock()

    # Prepare an invalid payload (missing required fields)
    invalid_payload = {
        "user_id": "user123",
        # Missing 'subject' and 'message'
    }

    # Call the function and expect a ValidationError
    from pydantic import ValidationError

    with pytest.raises(ValidationError):
        await create_notification(NotificationPayload(**invalid_payload), db=mock_db)

    # Ensure no DB interactions or Celery tasks were triggered
    mock_db.add.assert_not_called()
    mock_db.commit.assert_not_called()
