from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.core.secrets_manager import CURRENT_SECRETS
import asyncio

_engine = None
_SessionLocal = None

def get_connection_url():
    return (
        f"postgresql+asyncpg://{CURRENT_SECRETS['DB_USER']}:{CURRENT_SECRETS['DB_PASSWORD']}"
        f"@{CURRENT_SECRETS['DB_HOST']}:{CURRENT_SECRETS['DB_PORT']}/{CURRENT_SECRETS['DB_NAME']}"
    )

def init_engine():
    global _engine, _SessionLocal
    conn_url = get_connection_url()
    _engine = create_async_engine(conn_url, echo=False, future=True)
    _SessionLocal = sessionmaker(
        autocommit=False, autoflush=False, bind=_engine, class_=AsyncSession
    )

def get_db():
    if _SessionLocal is None:
        init_engine()
    return _SessionLocal()

async def refresh_engine_if_needed():
    """
    Periodically check if secrets changed.
    If yes → rebuild engine with new creds.
    """
    global _engine, _SessionLocal
    while True:
        new_url = get_connection_url()
        if str(_engine.url) != new_url:
            print("🔄 DB creds rotated, reconnecting engine...")
            init_engine()
        await asyncio.sleep(60)  # check every 1 min
