import logging
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, Security
from fastapi.security.api_key import APIKeyHeader

from app.config import settings
from app.db import engine
from app.models import Base
from app.routes import notifications, preferences
from app.utils.logger import setup_logger

setup_logger()
logger = logging.getLogger(__name__)

api_key_header = APIKeyHeader(name="x-api-key", auto_error=False)


def validate_api_key(api_key: str = Security(api_key_header)):
    if api_key != settings.api_key:
        raise HTTPException(status_code=403, detail="Invalid API key")


@asynccontextmanager
async def lifespan(
    app: FastAPI,
):  # pylint: disable=redefined-outer-name,unused-argument
    # Startup: create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Tables created")

    yield  # allows the app to start serving


app = FastAPI(title=settings.app_name, version="1.0.0", lifespan=lifespan)

setup_logger()
app.include_router(
    preferences.router,
    prefix="/preferences",
    tags=["Preferences"],
    dependencies=[Depends(validate_api_key)],
)
app.include_router(
    notifications.router,
    prefix="/notifications",
    tags=["Notifications"],
    dependencies=[Depends(validate_api_key)],
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
    return {
        "message": "Welcome to this app! Add '/docs' to the end of the URL (e.g., https://your-codespace-8000.app.github.dev/docs) to view the API documentation and learn about its usage."
    }
