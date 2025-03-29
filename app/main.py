from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.routes import alerts
from app.routes import preferences
from app.routes import notifications
from app.utils.logger import setup_logger
from app.config import settings
from app.db import engine
from app.models import Base


@asynccontextmanager
async def lifespan(app: FastAPI):  # pylint: disable=redefined-outer-name,unused-argument
    # Startup: create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("Tables created")

    yield  # allows the app to start serving

    # Shutdown: (optional) do cleanup here if needed


app = FastAPI(title=settings.app_name, version="1.0.0", lifespan=lifespan)

setup_logger()
app.include_router(alerts.router, prefix="/alerts", tags=["Alerts"])
app.include_router(preferences.router, prefix="/preferences", tags=["Preferences"])
app.include_router(notifications.router, prefix="/notifications", tags=["Notifications"])


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
    return {"message": "Hello World"}
