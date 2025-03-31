from abc import ABC, abstractmethod


class Notifier(ABC):
    def __init__(self, user_id: str, recipient: str, subject: str, body: str):
        self.user_id = user_id  # Unique identifier for the user or notification
        self.recipient = recipient
        self.subject = subject
        self.body = body

    @abstractmethod
    def validate_recipient(self) -> bool:
        """Validate the recipient (e.g., email or phone number)."""

    @abstractmethod
    def send(self) -> bool:
        """Send the notification."""
