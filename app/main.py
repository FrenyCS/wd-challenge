from fastapi import FastAPI

from app.routes import alerts
from app.utils.logger import setup_logger
from app.config import settings


app = FastAPI(title=settings.app_name, version=settings.version)

setup_logger()
app.include_router(alerts.router, prefix="/alerts", tags=["Alerts"])


@app.get("/health", tags=["Health"])
def health_check():
    return {
        "status": "ok",
        "environment": settings.environment,
        "app_name": settings.app_name,
        "version": settings.version,
    }


@app.get("/")
async def root():
    return {"message": "Hello World"}
