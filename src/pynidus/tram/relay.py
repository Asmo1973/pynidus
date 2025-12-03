import asyncio
import logging
from datetime import datetime, timezone
from typing import Callable, Awaitable
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
from .models import OutboxMessage
from ..microservices.transport.base import TransportStrategy

logger = logging.getLogger(__name__)

class MessageRelay:
    def __init__(
        self,
        session_factory: async_sessionmaker[AsyncSession],
        transport: TransportStrategy,
        poll_interval: float = 1.0,
        batch_size: int = 100
    ):
        self.session_factory = session_factory
        self.transport = transport
        self.poll_interval = poll_interval
        self.batch_size = batch_size
        self._running = False
        self._task: asyncio.Task | None = None

    async def start(self):
        self._running = True
        await self.transport.connect()
        self._task = asyncio.create_task(self._run_loop())
        logger.info("MessageRelay started")

    async def stop(self):
        self._running = False
        if self._task:
            await self._task
        await self.transport.close()
        logger.info("MessageRelay stopped")

    async def _run_loop(self):
        while self._running:
            try:
                await self.process_outbox()
            except Exception as e:
                logger.error(f"Error in MessageRelay loop: {e}", exc_info=True)
            
            await asyncio.sleep(self.poll_interval)

    async def process_outbox(self):
        async with self.session_factory() as session:
            async with session.begin():
                # Fetch pending messages
                # Using FOR UPDATE SKIP LOCKED if supported (Postgres), but for SQLite/Generic we keep it simple
                # For SQLite, concurrency is limited anyway.
                stmt = (
                    select(OutboxMessage)
                    .where(OutboxMessage.status == "PENDING")
                    .order_by(OutboxMessage.created_at)
                    .limit(self.batch_size)
                )
                result = await session.execute(stmt)
                messages = result.scalars().all()

                if not messages:
                    return

                for message in messages:
                    try:
                        # Ensure headers exist and include message ID
                        headers = message.headers or {}
                        headers["x-message-id"] = message.id
                        
                        await self.transport.publish(
                            channel=message.channel,
                            message=message.payload,
                            headers=headers
                        )
                        message.status = "PUBLISHED"
                        message.processed_at = datetime.now(timezone.utc)
                    except Exception as e:
                        logger.error(f"Failed to publish message {message.id}: {e}")
                        message.status = "FAILED"
                        message.error = str(e)
                        # Depending on policy, we might retry or leave it as FAILED
                
                # Commit updates to message status
                await session.commit()
