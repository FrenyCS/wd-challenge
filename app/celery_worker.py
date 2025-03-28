print("Running celery_worker.py")

from dotenv import load_dotenv
load_dotenv(".env")
print("Loaded .env")

from celery import Celery
from app.config import settings

print("Loaded settings")
print(f"settings.celery_broker_url: {settings.celery_broker_url}")
print(f"settings.celery_result_backend: {settings.celery_result_backend}")

celery_app = Celery(
    "property_alerts",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend
)

celery_app.conf.task_routes = {
    "app.tasks.*": {"queue": "alerts"}
}

print("Celery app ready")