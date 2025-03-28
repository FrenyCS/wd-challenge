# app/services/sms_sender.py
from typing import List
import logging

logger = logging.getLogger(__name__)


def send_sms(message: str, to_numbers: List[str]) -> bool:
    logger.info("[MOCK] Sending SMS")
    logger.debug(f"To: {to_numbers}")
    logger.debug(f"Message: {message}")
    return True
