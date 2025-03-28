from pydantic_settings import BaseSettings
from pydantic import EmailStr
from typing import Optional


class Settings(BaseSettings):
    # General
    app_name: str = "Property Alerts Service"
    app_description: str = "Property Alerts Service"
    environment: str = "development"
    version: str = "1.0.0"

    # Email
    smtp_host: str
    smtp_port: int
    smtp_user: str
    smtp_password: str
    sender_email: EmailStr

    # SMS
    twilio_account_sid: Optional[str] = None
    twilio_auth_token: Optional[str] = None
    twilio_from_number: Optional[str] = None

    # Celery
    celery_broker_url: str
    celery_result_backend: Optional[str] = None

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
