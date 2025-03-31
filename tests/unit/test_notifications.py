from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

import pytest
from fastapi import HTTPException
from pydantic import ValidationError

from app.routes.notifications import NotificationPayload, create_notification


@pytest.fixture
def mock_celery_tasks():
    """Fixture for mocking Celery tasks."""
    return {
        "send_email_task": MagicMock(),
        "send_sms_task": MagicMock(),
    }


@pytest.mark.asyncio
async def test_create_notification(
    mock_db, mock_user_preferences, mock_celery_tasks
):  # pylint: disable=redefined-outer-name
    # Use shared and module-specific fixtures
    mock_db.execute.return_value.scalar_one_or_none.return_value = mock_user_preferences

    with (
        patch(
            "app.routes.notifications.send_email_task",
            mock_celery_tasks["send_email_task"],
        ),
        patch(
            "app.routes.notifications.send_sms_task", mock_celery_tasks["send_sms_task"]
        ),
    ):
        # Mock datetime
        mock_now = datetime(2025, 1, 1, tzinfo=timezone.utc)
        with patch("app.routes.notifications.datetime") as mock_datetime:
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
            mock_celery_tasks["send_email_task"].apply_async.assert_called_once()
            mock_celery_tasks["send_sms_task"].apply_async.assert_called_once()


@pytest.mark.asyncio
async def test_create_scheduled_notification(
    mock_db,
    mock_user_preferences,
    mock_celery_tasks,  # pylint: disable=redefined-outer-name
):
    # Use shared and module-specific fixtures
    mock_db.execute.return_value.scalar_one_or_none.return_value = mock_user_preferences

    # Mock datetime
    mock_now = datetime(2025, 1, 1, tzinfo=timezone.utc)
    mock_future_time = datetime(2025, 1, 2, tzinfo=timezone.utc)  # Scheduled time

    with (
        patch(
            "app.routes.notifications.send_email_task",
            mock_celery_tasks["send_email_task"],
        ),
        patch(
            "app.routes.notifications.send_sms_task", mock_celery_tasks["send_sms_task"]
        ),
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
        mock_celery_tasks["send_email_task"].apply_async.assert_called_once_with(
            kwargs={
                "user_id": "user123",
                "subject": "Scheduled Notification",
                "message": "This is a scheduled test message",
                "notification_id": mock_db.add.call_args[0][0].id,
                "recipient": "user@example.com",
            },
            eta=mock_future_time,
        )
        mock_celery_tasks["send_sms_task"].apply_async.assert_called_once_with(
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
async def test_create_notification_user_preferences_not_found(mock_db):
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
async def test_create_notification_disabled_channels(
    mock_db,
    mock_user_preferences,
    mock_celery_tasks,  # pylint: disable=redefined-outer-name
):
    # Mock user preferences with both channels disabled
    mock_user_preferences.email_enabled = False
    mock_user_preferences.sms_enabled = False
    mock_db.execute.return_value.scalar_one_or_none.return_value = mock_user_preferences

    with (
        patch(
            "app.routes.notifications.send_email_task",
            mock_celery_tasks["send_email_task"],
        ),
        patch(
            "app.routes.notifications.send_sms_task", mock_celery_tasks["send_sms_task"]
        ),
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
        mock_celery_tasks["send_email_task"].apply_async.assert_not_called()
        mock_celery_tasks["send_sms_task"].apply_async.assert_not_called()


@pytest.mark.asyncio
async def test_create_notification_invalid_payload(mock_db):
    # Prepare an invalid payload (missing required fields)
    invalid_payload = {
        "user_id": "user123",
        # Missing 'subject' and 'message'
    }

    with pytest.raises(ValidationError):
        await create_notification(NotificationPayload(**invalid_payload), db=mock_db)

    # Ensure no DB interactions or Celery tasks were triggered
    mock_db.add.assert_not_called()
    mock_db.commit.assert_not_called()
