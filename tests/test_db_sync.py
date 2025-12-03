import pytest
from sqlalchemy import select
from pynidus.db.base import Base
from pynidus.db.sync_session import engine, SessionLocal
from sqlalchemy.orm import Mapped, mapped_column

class SyncUser(Base):
    __tablename__ = "sync_users"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]

@pytest.fixture(autouse=True)
def clean_db():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    yield
    Base.metadata.drop_all(engine)

def test_sync_db_connection():
    # Tables are created by fixture
    with SessionLocal() as session:
        new_user = SyncUser(name="Sync User")
        session.add(new_user)
        session.commit()

        result = session.execute(select(SyncUser).where(SyncUser.name == "Sync User"))
        user = result.scalar_one()
        assert user.name == "Sync User"
        assert user.id is not None
