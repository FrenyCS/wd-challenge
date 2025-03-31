from typing import Optional

from dotenv import load_dotenv
from pydantic import EmailStr
from pydantic_settings import BaseSettings

# Load .env.example first, then override with .env if exists
load_dotenv(dotenv_path=".env.example", override=False)
load_dotenv(dotenv_path=".env", override=True)


class Settings(BaseSettings):
    # General
    app_name: str = "Property Alerts Service"
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

    # Database
    db_host: str
    db_port: int
    db_user: str
    db_password: str
    db_name: str

    class Config:
        env_file_encoding = "utf-8"


settings = Settings()
