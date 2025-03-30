import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine
from app.db import Base

DATABASE_URL = "postgresql+asyncpg://alerts_user:alerts_pass@db:5432/alerts_db"


@pytest_asyncio.fixture(scope="module", autouse=True)
async def setup_db():
    # Build engine inline (bound to the test's event loop)
    engine = create_async_engine(DATABASE_URL, echo=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield


@pytest_asyncio.fixture
async def async_client():
    async with AsyncClient(base_url="http://app:8000") as client:
        yield client
