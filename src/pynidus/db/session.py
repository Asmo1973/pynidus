from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from pynidus.core.config import BaseSettings

settings = BaseSettings()
DATABASE_URL = settings.database.url

engine = create_async_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},  # Needed for SQLite
    echo=settings.database.echo,
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)
