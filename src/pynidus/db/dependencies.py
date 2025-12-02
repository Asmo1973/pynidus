from typing import AsyncGenerator, Generator
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from .session import AsyncSessionLocal
from .sync_session import SessionLocal

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency for getting an async database session.
    """
    async with AsyncSessionLocal() as session:
        yield session

def get_sync_db() -> Generator[Session, None, None]:
    """
    Dependency for getting a synchronous database session.
    """
    with SessionLocal() as session:
        yield session
