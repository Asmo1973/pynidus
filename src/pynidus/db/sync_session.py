from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from pynidus.core.config import BaseSettings

settings = BaseSettings()
DATABASE_URL = settings.database.url

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},  # Needed for SQLite
    echo=settings.database.echo,
)

SessionLocal = sessionmaker(
    bind=engine,
    class_=Session,
    expire_on_commit=False,
    autoflush=False,
)
