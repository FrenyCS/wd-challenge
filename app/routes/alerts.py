# app/routes/alerts.py
from fastapi import APIRouter
from pydantic import BaseModel, EmailStr
from typing import List, Optional

from app.tasks.notification_tasks import send_email_task, send_sms_task

router = APIRouter()


class AlertRequest(BaseModel):
    subject: str
    message: str
    email_recipients: Optional[List[EmailStr]] = []
    sms_recipients: Optional[List[str]] = []


@router.post("/")
def trigger_alerts(alert: AlertRequest):
    if alert.email_recipients:
        send_email_task.delay(
            subject=alert.subject,
            body=alert.message,
            to_emails=alert.email_recipients,
        )

    if alert.sms_recipients:
        send_sms_task.delay(
            message=alert.message,
            to_numbers=alert.sms_recipients,
        )

    return {"status": "queued", "details": "Alerts submitted to Celery"}
