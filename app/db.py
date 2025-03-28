from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from app.config import settings

DATABASE_URL = (
    f"postgresql+asyncpg://{settings.db_user}:{settings.db_password}"
    f"@{settings.db_host}:{settings.db_port}/{settings.db_name}"
)

engine = create_async_engine(DATABASE_URL, echo=True)
AsyncSessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False)

Base = declarative_base()


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
