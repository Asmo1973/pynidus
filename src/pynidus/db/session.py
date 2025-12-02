from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

# Default to in-memory SQLite for simplicity if no URL is provided, 
# but typically this would come from configuration.
DATABASE_URL = "sqlite+aiosqlite:///./test.db"

engine = create_async_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},  # Needed for SQLite
    echo=False,
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)
