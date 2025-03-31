import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.config import settings
from app.db import engine
from app.models import Base
from app.routes import notifications, preferences
from app.utils.logger import setup_logger

setup_logger()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(
    app: FastAPI,
):  # pylint: disable=redefined-outer-name,unused-argument
    # Startup: create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Tables created")

    yield  # allows the app to start serving

    # Shutdown: (optional) do cleanup here if needed


app = FastAPI(title=settings.app_name, version="1.0.0", lifespan=lifespan)

setup_logger()
app.include_router(preferences.router, prefix="/preferences", tags=["Preferences"])
app.include_router(
    notifications.router, prefix="/notifications", tags=["Notifications"]
)


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
    # replace this with usage instructions
    return {
        "message": "Welcome to this app! Add '/docs' to the end of the URL (e.g., https://your-codespace-8000.app.github.dev/docs) to view the API documentation and learn about its usage."
    }
