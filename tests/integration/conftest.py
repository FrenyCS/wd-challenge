import pytest_asyncio
from httpx import AsyncClient
from app.db import Base, engine


@pytest_asyncio.fixture(scope="module", autouse=True)
async def setup_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield


@pytest_asyncio.fixture
async def async_client():
    async with AsyncClient(base_url="http://app:8000") as client:
        yield client
