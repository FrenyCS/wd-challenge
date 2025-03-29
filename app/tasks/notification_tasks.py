from celery import shared_task
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
import asyncio

from app.models import Notification, NotificationStatus
from app.db import AsyncSessionLocal

# Mock email/SMS notification logic
def mock_send_email(subject: str, body: str, user_id: str):
    print(f"[MOCK EMAIL] To: {user_id}\nSubject: {subject}\nBody: {body}")
    return True

def mock_send_sms(message: str, user_id: str):
    print(f"[MOCK SMS] To: {user_id}\nMessage: {message}")
    return True

@shared_task(name="app.tasks.send_email_task")
def send_email_task(user_id: str, subject: str, message: str, notification_id: int):
    asyncio.run(_process_notification_task(
        notification_id=notification_id,
        user_id=user_id,
        subject=subject,
        message=message,
        channel="email"
    ))

@shared_task(name="app.tasks.send_sms_task")
def send_sms_task(user_id: str, subject: str, message: str, notification_id: int):
    asyncio.run(_process_notification_task(
        notification_id=notification_id,
        user_id=user_id,
        subject=subject,
        message=message,
        channel="sms"
    ))

async def _process_notification_task(notification_id: int, user_id: str, subject: str, message: str, channel: str):
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Notification).where(Notification.id == notification_id))
        notification = result.scalar_one_or_none()

        if not notification:
            print(f"[ERROR] Notification ID {notification_id} not found")
            return

        try:
            if channel == "email":
                mock_send_email(subject, message, user_id)
            elif channel == "sms":
                mock_send_sms(message, user_id)

            notification.status = NotificationStatus.sent
            notification.sent_at = datetime.now(timezone.utc)
        except Exception as e:
            print(f"[ERROR] Failed to send {channel.upper()} notification: {e}")
            notification.status = NotificationStatus.failed

        await session.commit()
