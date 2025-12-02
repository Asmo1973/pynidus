from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

# Default to in-memory SQLite for simplicity if no URL is provided
DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},  # Needed for SQLite
    echo=False,
)

SessionLocal = sessionmaker(
    bind=engine,
    class_=Session,
    expire_on_commit=False,
    autoflush=False,
)
