import nest_asyncio
nest_asyncio.apply()

from celery import shared_task
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
import asyncio
from app.db import AsyncSessionLocal
from app.models import Notification, NotificationStatus


def mock_send_email(subject: str, body: str, user_id: str):
    print(f"[MOCK EMAIL] To: {user_id} | Subject: {subject} | Body: {body}")
    return True

def mock_send_sms(message: str, user_id: str):
    print(f"[MOCK SMS] To: {user_id} | Message: {message}")
    return True


@shared_task(name="app.tasks.send_email_task")
def send_email_task(user_id: str, subject: str, message: str, notification_id: int):
    asyncio.run(process_notification(notification_id, user_id, subject, message, "email"))

@shared_task(name="app.tasks.send_sms_task")
def send_sms_task(user_id: str, subject: str, message: str, notification_id: int):
    asyncio.run(process_notification(notification_id, user_id, subject, message, "sms"))


async def process_notification(notification_id, user_id, subject, message, channel):
    async with AsyncSessionLocal() as session:
        try:
            result = await session.execute(
                select(Notification).where(Notification.id == notification_id)
            )
            notification = result.scalar_one_or_none()
            if not notification:
                print(f"[ERROR] Notification {notification_id} not found")
                return

            # Simulate sending
            if channel == "email":
                mock_send_email(subject, message, user_id)
            else:
                mock_send_sms(message, user_id)

            # Update status and sent_at
            notification.status = NotificationStatus.sent
            notification.sent_at = datetime.now(timezone.utc)
            await session.commit()
        except Exception as e:
            print(f"[ERROR] Failed to send {channel.upper()} notification: {e}")
            notification.status = NotificationStatus.failed
            await session.commit()