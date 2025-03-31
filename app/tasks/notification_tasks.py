import nest_asyncio

nest_asyncio.apply()

import asyncio
from datetime import datetime, timezone

from celery import shared_task
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.future import select

from app.db import AsyncSessionLocal
from app.models import Notification, NotificationStatus
from app.notifiers.email_notifier import EmailNotifier
from app.notifiers.sms_notifier import SMSNotifier


def mock_send_email(user_id: str, email: str, subject: str, body: str):
    print(
        f"[MOCK EMAIL] To: {user_id} | Email: {email} | Subject: {subject} | Body: {body}"
    )
    return True


def mock_send_sms(user_id: str, phone_number: str, message: str):
    print(
        f"[MOCK SMS] To: {user_id} | Phone number: {phone_number} | Message: {message}"
    )
    return True


@shared_task(name="app.tasks.send_email_task")
def send_email_task(
    user_id: str, subject: str, message: str, recipient: str, notification_id: int
):
    asyncio.run(
        process_notification(
            notification_id, user_id, subject, message, "email", recipient
        )
    )


@shared_task(name="app.tasks.send_sms_task")
def send_sms_task(
    user_id: str, subject: str, message: str, recipient: str, notification_id: int
):
    asyncio.run(
        process_notification(
            notification_id, user_id, subject, message, "sms", recipient
        )
    )


async def process_notification(
    notification_id, user_id, subject, message, channel, recipient
):
    async with AsyncSessionLocal() as session:
        try:
            result = await session.execute(
                select(Notification).where(Notification.id == notification_id)
            )
            notification = result.scalar_one_or_none()
            if not notification:
                print(f"[ERROR] Notification {notification_id} not found")
                return

            # Use the appropriate Notifier implementation
            notifier = (
                EmailNotifier(user_id, recipient, subject, message)
                if channel == "email"
                else SMSNotifier(user_id, recipient, subject, message)
            )

            # Validate and send
            if notifier.validate_recipient():
                notifier.send()
            else:
                raise ValueError(f"Invalid recipient for {channel.upper()}")

            # Update status and sent_at
            notification.status = NotificationStatus.sent
            notification.sent_at = datetime.now(timezone.utc)
            await session.commit()
        except SQLAlchemyError as e:
            print(
                f"[ERROR] Database error while sending {channel.upper()} notification: {e}"
            )
            notification.status = NotificationStatus.failed
            await session.commit()
        except Exception as e:  # pylint: disable=broad-exception-caught
            print(
                f"[ERROR] Unexpected error while sending {channel.upper()} notification: {e}"
            )
            notification.status = NotificationStatus.failed
            await session.commit()
