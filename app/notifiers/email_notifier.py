import re

from app.notifiers.base import Notifier


class EmailNotifier(Notifier):
    def validate_recipient(self) -> bool:
        """Validate the email address."""
        email_regex = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
        return re.match(email_regex, self.recipient) is not None

    def send(self) -> bool:
        """Mock sending an email."""
        if not self.validate_recipient():
            raise ValueError(f"Invalid email address: {self.recipient}")
        print(
            f"[MOCK EMAIL] To: {self.recipient} (ID: {self.user_id}) | Subject: {self.subject} | Body: {self.body}"
        )
        return True
