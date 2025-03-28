
from celery import Celery
from app.config import settings


celery_app = Celery(
    "property_alerts",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
)

celery_app.conf.task_routes = {"app.tasks.*": {"queue": "alerts"}}
