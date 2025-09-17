import pytest
import asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.db.session import get_db
from app.db.models import Base  # ensure this imports all models

# Point to test DB (db_test service from docker-compose)
DATABASE_URL = "postgresql+asyncpg://finops:finops123@db_test:5432/finopsdb_test"

engine = create_async_engine(DATABASE_URL, echo=False, future=True)
TestSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

# Dependency override
async def override_get_db():
    async with TestSessionLocal() as session:
        yield session

app.dependency_overrides[get_db] = override_get_db

# Ensure DB schema is fresh before tests
@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    async def init_models():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)
    asyncio.get_event_loop().run_until_complete(init_models())

# AsyncIO backend
@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"

# HTTP client fixture
@pytest.fixture
async def client():
    async with AsyncClient(app=app, base_url="http://test") as c:
        yield c

# Optional: seed some test data
@pytest.fixture
async def seed_data():
    async with TestSessionLocal() as session:
        # Example: insert a fake account
        await session.execute(
            "INSERT INTO accounts (cloud_provider, account_number, account_name) "
            "VALUES ('AWS', '111111111111', 'TestAccount')"
        )
        await session.commit()
        yield
