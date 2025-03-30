import nest_asyncio

nest_asyncio.apply()

from celery import shared_task
from datetime import datetime, timezone
from sqlalchemy.future import select
from sqlalchemy.exc import SQLAlchemyError
import asyncio
from app.db import AsyncSessionLocal
from app.models import Notification, NotificationStatus


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

            # Simulate sending
            if channel == "email":
                mock_send_email(
                    user_id=user_id, email=recipient, subject=subject, body=message
                )
            else:
                # For SMS, we can format the message to include the subject
                message = f"{subject} - {message}"
                mock_send_sms(user_id=user_id, phone_number=recipient, message=message)

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
