from celery import shared_task
from typing import List


@shared_task(name="app.tasks.send_email_task")
def send_email_task(subject: str, body: str, to_emails: List[str]) -> bool:
    print("[MOCK - CELERY] Sending email")
    print(f"Subject: {subject}")
    print(f"To: {to_emails}")
    print(f"Body: {body}")
    return True


@shared_task(name="app.tasks.send_sms_task")
def send_sms_task(message: str, to_numbers: List[str]) -> bool:
    print("[MOCK - CELERY] Sending SMS")
    print(f"To: {to_numbers}")
    print(f"Message: {message}")
    return True
