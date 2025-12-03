import pytest
import pytest_asyncio
from pynidus.db.session import engine as _async_engine, AsyncSessionLocal as _async_session_factory
from pynidus.db.base import Base

@pytest_asyncio.fixture
async def async_engine():
    async with _async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield _async_engine
    async with _async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest_asyncio.fixture
async def async_session_factory(async_engine):
    return _async_session_factory
