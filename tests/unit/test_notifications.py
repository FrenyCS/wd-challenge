import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timedelta, timezone

from app.routes.notifications import create_notification, NotificationPayload
from app.models import UserPreference, NotificationStatus


# Mock Celery tasks
@patch("app.tasks.notification_tasks.send_email_task")
@patch("app.tasks.notification_tasks.send_sms_task")
@pytest.mark.asyncio
async def test_create_notification(mock_send_sms_task, mock_send_email_task):
    # Mock async DB session
    mock_db = AsyncMock()

    # Mock user preferences fetched from DB
    mock_preferences = UserPreference(
        user_id="user123",
        email="user@example.com",
        phone_number="1234567890",
        email_enabled=True,
        sms_enabled=True,
    )
    mock_db.execute.return_value.scalar_one_or_none = AsyncMock(
        return_value=mock_preferences
    )

    # Mock payload data
    payload = NotificationPayload(
        user_id="user123",
        subject="Subject",
        message="Message",
        send_at=datetime.now(timezone.utc) + timedelta(days=1),  # Future time
    )

    # Call the function
    with patch("app.db.get_db", return_value=mock_db):
        response = await create_notification(payload=payload, db=mock_db)

    # Assert response data
    assert response["status"] == "queued"
    assert response["send_at"] == payload.send_at.isoformat()

    # Ensure Email Task was queued with the correct parameters
    mock_send_email_task.apply_async.assert_called_once()
    email_task_args = mock_send_email_task.apply_async.call_args[1]["kwargs"]
    assert email_task_args["user_id"] == payload.user_id
    assert email_task_args["subject"] == payload.subject
    assert email_task_args["message"] == payload.message
    assert email_task_args["recipient"] == mock_preferences.email

    # Ensure SMS Task was queued with the correct parameters
    mock_send_sms_task.apply_async.assert_called_once()
    sms_task_args = mock_send_sms_task.apply_async.call_args[1]["kwargs"]
    assert sms_task_args["user_id"] == payload.user_id
    assert sms_task_args["recipient"] == mock_preferences.phone_number

    # Ensure DB commit was called
    mock_db.commit.assert_called_once()


@pytest.mark.asyncio
async def test_create_notification_user_preference_not_found():
    # Mock async DB session
    mock_db = AsyncMock()
    mock_db.execute.return_value.scalar_one_or_none = AsyncMock(return_value=None)  # No preferences found

    # Mock payload data
    payload = NotificationPayload(
        user_id="user123",
        subject="Subject",
        message="Message",
    )

    # Call the function and catch exception
    with patch("app.db.get_db", return_value=mock_db):
        with pytest.raises(Exception) as exc:
            await create_notification(payload=payload, db=mock_db)

    # Assert exception details
    assert exc.value.status_code == 404
    assert exc.value.detail == "User preferences not found"
