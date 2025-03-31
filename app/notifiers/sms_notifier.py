import logging
import re

from app.notifiers.base import Notifier

logger = logging.getLogger(__name__)


class SMSNotifier(Notifier):
    def validate_recipient(self) -> bool:
        """Validate the phone number."""
        phone_regex = r"^\+\d{10,15}$"  # Example: +1234567890
        return re.match(phone_regex, self.recipient) is not None

    def send(self) -> bool:
        """Mock sending an SMS."""
        if not self.validate_recipient():
            raise ValueError(f"Invalid phone number: {self.recipient}")
        logger.info(
            "[MOCK SMS] To: %s (ID: %s) | Message: %s - %s",
            self.recipient,
            self.user_id,
            self.subject,
            self.body,
        )
        return True
