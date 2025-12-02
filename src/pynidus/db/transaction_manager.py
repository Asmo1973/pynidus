from typing import Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

class SQLAlchemyTransactionManager:
    def __init__(self, session: Session):
        self.session = session

    def begin(self) -> None:
        if not self.session.in_transaction():
            self.session.begin()

    def commit(self) -> None:
        self.session.commit()

    def rollback(self) -> None:
        self.session.rollback()

class AsyncSQLAlchemyTransactionManager:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def begin(self) -> None:
        if not self.session.in_transaction():
            await self.session.begin()

    async def commit(self) -> None:
        await self.session.commit()

    async def rollback(self) -> None:
        await self.session.rollback()
