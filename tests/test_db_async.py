import pytest
from sqlalchemy import select
from pynidus.db.base import Base
from pynidus.db.session import engine, AsyncSessionLocal
from sqlalchemy.orm import Mapped, mapped_column

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]

@pytest.mark.asyncio
async def test_async_db_connection():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as session:
        new_user = User(name="Async User")
        session.add(new_user)
        await session.commit()

        result = await session.execute(select(User).where(User.name == "Async User"))
        user = result.scalar_one()
        assert user.name == "Async User"
        assert user.id is not None
