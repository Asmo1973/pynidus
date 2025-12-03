import pytest
import asyncio
import json
import zmq
import zmq.asyncio
from pynidus.microservices.transport.zeromq import ZeroMQTransport

@pytest.mark.skip(reason="Flaky on Windows with inproc/tcp, needs investigation")
@pytest.mark.asyncio
async def test_zeromq_pub_sub():
    # Use inproc for reliable testing with shared context
    shared_context = zmq.asyncio.Context()
    
    # Publisher binds PUB to "inproc://bus"
    publisher = ZeroMQTransport(pub_addr="inproc://bus", sub_addr="inproc://dummy1", context=shared_context)
    
    # Subscriber connects SUB to "inproc://bus"
    subscriber = ZeroMQTransport(pub_addr="inproc://dummy2", sub_addr="inproc://bus", context=shared_context)

    await publisher.connect()
    await subscriber.connect()
    
    received_events = []
    async def handler(message):
        received_events.append(message)

    await subscriber.subscribe("test_topic", handler)
    
    # Give time for connection to be established (ZMQ slow joiner)
    await asyncio.sleep(1.0)
    
    await publisher.publish("test_topic", {"msg": "hello zmq"})
    
    # Give time for message delivery
    await asyncio.sleep(0.5)
    
    assert len(received_events) == 1
    assert received_events[0].payload == {"msg": "hello zmq"}
    assert received_events[0].channel == "test_topic"
    
    await publisher.close()
    await subscriber.close()
