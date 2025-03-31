import logging
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr  # pylint: disable=unused-import
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.db import get_db
from app.models import Notification, NotificationStatus, UserPreference
from app.tasks.notification_tasks import send_email_task, send_sms_task

router = APIRouter()

logger = logging.getLogger(__name__)


class NotificationPayload(BaseModel):
    user_id: str
    subject: str
    message: str
    send_at: Optional[datetime] = None  # if None, send immediately


@router.post("")
async def create_notification(
    payload: NotificationPayload, db: AsyncSession = Depends(get_db)
):
    # Get user preferences
    result = await db.execute(
        select(UserPreference).where(UserPreference.user_id == payload.user_id)
    )
    preferences = result.scalar_one_or_none()
    if not preferences:
        logger.warning("User preferences not found for user_id: %s", payload.user_id)
        raise HTTPException(status_code=404, detail="User preferences not found")

    now = datetime.now(timezone.utc)
    send_at = payload.send_at or now

    notification_records = []

    # Schedule email if enabled
    if preferences.email_enabled and preferences.email:
        notification = Notification(
            user_id=payload.user_id,
            subject=payload.subject,
            message=payload.message,
            send_at=send_at,
            status=NotificationStatus.pending,
            channel="email",
            recipient=preferences.email,
        )
        db.add(notification)
        notification_records.append((notification, send_email_task))

    # Schedule SMS if enabled
    if preferences.sms_enabled and preferences.phone_number:
        notification = Notification(
            user_id=payload.user_id,
            subject=payload.subject,
            message=payload.message,
            send_at=send_at,
            status=NotificationStatus.pending,
            channel="sms",
            recipient=preferences.phone_number,
        )
        db.add(notification)
        notification_records.append((notification, send_sms_task))

    await db.commit()

    # Trigger tasks via Celery
    for notification, task in notification_records:
        task_args = {
            "user_id": notification.user_id,
            "subject": notification.subject,
            "message": notification.message,
            "notification_id": notification.id,
            "recipient": notification.recipient,
        }

        eta = notification.send_at if notification.send_at > now else None
        task.apply_async(kwargs=task_args, eta=eta)

    logger.info("Notification queued for user_id: %s", payload.user_id)

    return {"status": "queued", "send_at": send_at.isoformat()}
