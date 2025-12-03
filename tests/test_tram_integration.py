import pytest
import asyncio
from sqlalchemy import select
from pynidus.db.base import Base
from pynidus.db.session import engine, AsyncSessionLocal
from pynidus.tram.client import TramClient
from pynidus.tram.relay import MessageRelay
from pynidus.tram.models import OutboxMessage
from pynidus.microservices.transport.memory import MemoryTransport
from pynidus.microservices.listener import MicroserviceListener
from pynidus.microservices.decorators import EventPattern

# Global state for verification
RECEIVED_EVENTS = []

@EventPattern("test_channel")
async def handle_test_event(payload):
    RECEIVED_EVENTS.append(payload)

import pytest_asyncio

@pytest_asyncio.fixture(autouse=True)
async def clean_db():
    # Reset global state
    RECEIVED_EVENTS.clear()
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.mark.asyncio
async def test_tram_flow():
    # 1. Setup Database (handled by fixture)

    # 2. Setup Components
    transport = MemoryTransport()
    listener = MicroserviceListener(transport)
    relay = MessageRelay(AsyncSessionLocal, transport, poll_interval=0.1)
    
    # 3. Start Listener (Consumer)
    await listener.start()

    # 4. Emit Event (Producer)
    async with AsyncSessionLocal() as session:
        async with session.begin():
            client = TramClient(session)
            await client.emit("test_channel", {"data": "hello tram"})
            # Event is now in DB (PENDING) but not published

    # Verify DB state
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(OutboxMessage).where(OutboxMessage.status == "PENDING"))
        messages = result.scalars().all()
        assert len(messages) == 1
        assert messages[0].payload == {"data": "hello tram"}

    # 5. Run Relay (Background Process)
    # We run it manually for one cycle to avoid infinite loops in tests
    await relay.start()
    await asyncio.sleep(0.2) # Give it time to poll and publish
    await relay.stop()

    # 6. Verify Event Received (Consumer)
    # The MemoryTransport dispatches immediately, so listener should have caught it
    assert len(RECEIVED_EVENTS) == 1
    assert RECEIVED_EVENTS[0] == {"data": "hello tram"}

    # 7. Verify DB State (Published)
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(OutboxMessage).where(OutboxMessage.status == "PUBLISHED"))
        messages = result.scalars().all()
        assert len(messages) == 1

    await listener.stop()
