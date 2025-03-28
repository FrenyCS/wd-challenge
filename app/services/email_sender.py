from typing import List
import logging

logger = logging.getLogger(__name__)


def send_email(subject: str, body: str, to_emails: List[str]) -> bool:
    logger.info("[MOCK] Sending email")
    logger.debug(f"Subject: {subject}")
    logger.debug(f"To: {to_emails}")
    logger.debug(f"Body: {body}")
    return True
