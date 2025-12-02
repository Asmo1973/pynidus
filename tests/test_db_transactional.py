import pytest
from sqlalchemy import select
from pynidus.db.base import Base
from pynidus.db.session import engine as async_engine, AsyncSessionLocal
from pynidus.db.sync_session import engine as sync_engine, SessionLocal
from pynidus.db.transaction_manager import SQLAlchemyTransactionManager, AsyncSQLAlchemyTransactionManager
from pynidus.common.decorators.transactional import Transactional
from sqlalchemy.orm import Mapped, mapped_column

class TransactionalUser(Base):
    __tablename__ = "transactional_users"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]

class AsyncUserService:
    def __init__(self):
        self.session = AsyncSessionLocal()
        self.transaction_manager = AsyncSQLAlchemyTransactionManager(self.session)

    @Transactional()
    async def create_user(self, name: str):
        user = TransactionalUser(name=name)
        self.session.add(user)
        return user

    @Transactional()
    async def create_user_error(self, name: str):
        user = TransactionalUser(name=name)
        self.session.add(user)
        raise ValueError("Error creating user")

class SyncUserService:
    def __init__(self):
        self.session = SessionLocal()
        self.transaction_manager = SQLAlchemyTransactionManager(self.session)

    @Transactional()
    def create_user(self, name: str):
        user = TransactionalUser(name=name)
        self.session.add(user)
        return user

    @Transactional()
    def create_user_error(self, name: str):
        user = TransactionalUser(name=name)
        self.session.add(user)
        raise ValueError("Error creating user")

@pytest.mark.asyncio
async def test_async_transactional_success():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    service = AsyncUserService()
    await service.create_user("Async Transactional User")
    
    # Verify persistence
    result = await service.session.execute(select(TransactionalUser).where(TransactionalUser.name == "Async Transactional User"))
    user = result.scalar_one()
    assert user.name == "Async Transactional User"
    await service.session.close()

@pytest.mark.asyncio
async def test_async_transactional_rollback():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    service = AsyncUserService()
    with pytest.raises(ValueError):
        await service.create_user_error("Async Rollback User")
    
    # Verify rollback
    result = await service.session.execute(select(TransactionalUser).where(TransactionalUser.name == "Async Rollback User"))
    assert result.scalar_one_or_none() is None
    await service.session.close()

def test_sync_transactional_success():
    Base.metadata.create_all(sync_engine)

    service = SyncUserService()
    service.create_user("Sync Transactional User")
    
    # Verify persistence
    result = service.session.execute(select(TransactionalUser).where(TransactionalUser.name == "Sync Transactional User"))
    user = result.scalar_one()
    assert user.name == "Sync Transactional User"
    service.session.close()

def test_sync_transactional_rollback():
    Base.metadata.create_all(sync_engine)

    service = SyncUserService()
    with pytest.raises(ValueError):
        service.create_user_error("Sync Rollback User")
    
    # Verify rollback
    result = service.session.execute(select(TransactionalUser).where(TransactionalUser.name == "Sync Rollback User"))
    assert result.scalar_one_or_none() is None
    service.session.close()
