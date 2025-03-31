from app.notifiers.base import Notifier
import re


class SMSNotifier(Notifier):
    def validate_recipient(self) -> bool:
        """Validate the phone number."""
        phone_regex = r"^\+\d{10,15}$"  # Example: +1234567890
        return re.match(phone_regex, self.recipient) is not None

    def send(self) -> bool:
        """Mock sending an SMS."""
        if not self.validate_recipient():
            raise ValueError(f"Invalid phone number: {self.recipient}")
        print(
            f"[MOCK SMS] To: {self.recipient} (ID: {self.user_id}) | Message: {self.subject} - {self.body}"
        )
        return True
