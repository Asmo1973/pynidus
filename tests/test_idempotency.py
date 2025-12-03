import pytest
import asyncio
from unittest.mock import AsyncMock
from pynidus.microservices.listener import MicroserviceListener
from pynidus.microservices.transport.memory import MemoryTransport
from pynidus.tram.models import IncomingMessage
from pynidus.db.base import Base
from sqlalchemy import select

@pytest.mark.asyncio
async def test_idempotency_deduplication(async_session_factory, async_engine):
    # Setup
    transport = MemoryTransport()
    listener = MicroserviceListener(transport, async_session_factory)
    
    # Create tables
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        
    # Mock handler
    handler_mock = AsyncMock()
    
    # Subscribe manually to test wrapper logic
    await transport.connect()
    wrapper = listener._create_handler_wrapper(handler_mock)
    await transport.subscribe("test_topic", wrapper)
    
    # 1. Publish first message
    msg_id = "msg-123"
    payload = {"data": "test"}
    headers = {"x-message-id": msg_id}
    
    await transport.publish("test_topic", payload, headers)
    
    # Wait for processing
    await asyncio.sleep(0.1)
    
    # Verify handler called once
    assert handler_mock.call_count == 1
    
    # Verify DB record
    async with async_session_factory() as session:
        stmt = select(IncomingMessage).where(IncomingMessage.id == msg_id)
        result = await session.execute(stmt)
        record = result.scalar_one_or_none()
        assert record is not None
        assert record.status == "PROCESSED"

    # 2. Publish DUPLICATE message
    await transport.publish("test_topic", payload, headers)
    
    # Wait for processing
    await asyncio.sleep(0.1)
    
    # Verify handler NOT called again
    assert handler_mock.call_count == 1
    
    # Cleanup
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
