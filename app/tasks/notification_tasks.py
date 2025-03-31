import nest_asyncio

nest_asyncio.apply()

import asyncio
import logging
from datetime import datetime, timezone

from celery import shared_task
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.future import select

from app.db import AsyncSessionLocal
from app.models import Notification, NotificationStatus
from app.notifiers.email_notifier import EmailNotifier
from app.notifiers.sms_notifier import SMSNotifier

logger = logging.getLogger(__name__)


def mock_send_email(user_id: str, email: str, subject: str, body: str):
    logger.info(
        "[MOCK EMAIL] To: %s | Email: %s | Subject: %s | Body: %s",
        user_id,
        email,
        subject,
        body,
    )
    return True


def mock_send_sms(user_id: str, phone_number: str, message: str):
    logger.info(
        "[MOCK SMS] To: %s | Phone number: %s | Message: %s",
        user_id,
        phone_number,
        message,
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
                logger.error(
                    "Notification %s not found", notification_id
                )
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
            logger.info(
                "%s notification sent successfully", channel.upper()
            )
        except SQLAlchemyError as e:
            logger.error(
                "Database error while sending %s notification: %s", channel.upper(), e
            )
            notification.status = NotificationStatus.failed
            await session.commit()
        except Exception as e:  # pylint: disable=broad-exception-caught
            logger.error(
                "Unexpected error while sending %s notification: %s", channel.upper(), e
            )
            notification.status = NotificationStatus.failed
            await session.commit()
