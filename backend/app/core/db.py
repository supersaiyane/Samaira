from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

# Base class for models
Base = declarative_base()

# Async engine (ensure asyncpg driver in DATABASE_URL)
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=True if settings.DB_DEBUG else False,  # toggle debug logging
    future=True
)

# Async session factory
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)

# Dependency for FastAPI routes
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
