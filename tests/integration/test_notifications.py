import asyncio
from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.future import select

from app.models import Notification, NotificationStatus


async def wait_for_notification_records(session, user_id, expected_count=2, timeout=3):
    for _ in range(timeout * 10):  # 10 retries per second
        result = await session.execute(
            select(Notification).where(Notification.user_id == user_id)
        )
        records = result.scalars().all()
        if len(records) == expected_count:
            return records
        await asyncio.sleep(0.1)  # retry after 100ms
    raise AssertionError(
        f"Expected {expected_count} notifications, but got {len(records)}"
    )


@pytest.fixture
def session_factory():
    engine = create_async_engine(
        "postgresql+asyncpg://alerts_user:alerts_pass@db:5432/alerts_db", echo=False
    )
    return async_sessionmaker(bind=engine, expire_on_commit=False)


async def test_create_immediate_notification(
    async_client, session_factory
):  # pylint: disable=redefined-outer-name
    async with session_factory() as session:
        user_id = "notify-user-db"

        pref_payload = {
            "email_enabled": True,
            "sms_enabled": True,
            "email": "notify@example.com",
            "phone_number": "+1111111111",
        }

        response = await async_client.post(f"/preferences/{user_id}", json=pref_payload)
        assert response.status_code == 200

        notif_payload = {
            "user_id": user_id,
            "subject": "Test Alert",
            "message": "This is a test notification",
        }

        response = await async_client.post("/notifications", json=notif_payload)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "queued"

        # Create session using the fixture (correct loop)
        async with session_factory() as session:
            await wait_for_notification_records(session, user_id)


@pytest.mark.asyncio
async def test_schedule_notification(
    async_client, session_factory
):  # pylint: disable=redefined-outer-name
    user_id = "scheduled-user"

    pref_payload = {
        "email_enabled": True,
        "sms_enabled": True,
        "email": "scheduled@example.com",
        "phone_number": "+1234567899",
    }

    response = await async_client.post(f"/preferences/{user_id}", json=pref_payload)
    assert response.status_code == 200

    # Schedule notification 10 minutes in the future
    future_time = (datetime.now(timezone.utc) + timedelta(minutes=10)).isoformat()

    notif_payload = {
        "user_id": user_id,
        "subject": "Scheduled Alert",
        "message": "This will be sent later",
        "send_at": future_time,
    }

    response = await async_client.post("/notifications", json=notif_payload)
    assert response.status_code == 200
    assert response.json()["status"] == "queued"

    async with session_factory() as session:
        result = await session.execute(
            select(Notification).where(Notification.user_id == user_id)
        )
        notifications = result.scalars().all()
        assert len(notifications) == 2  # email + sms

        for n in notifications:
            assert n.send_at is not None
            assert n.sent_at is None
            assert n.status == NotificationStatus.pending
