from fastapi import FastAPI
import uvicorn

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
        "description": settings.app_description,
    }


@app.get("/")
async def root():
    return {"message": "Hello World"}


if __name__ == "__main__":
    # TODO: Add logging
    uvicorn.run(app, port=8080, host="0.0.0.0")
