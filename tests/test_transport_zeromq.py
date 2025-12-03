import pytest
import asyncio
import json
import zmq
import zmq.asyncio
import sys

# Fix for Windows: zmq.asyncio does not support ProactorEventLoop (default on Py3.8+)
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
from pynidus.microservices.transport.zeromq import ZeroMQTransport

@pytest.mark.asyncio
async def test_zeromq_pub_sub():
    # Use TCP ports with wildcard bind
    # Publisher: Binds PUB to *:5555, Connects SUB to 127.0.0.1:5556
    publisher = ZeroMQTransport(
        pub_addr="tcp://*:5555",
        sub_addr="tcp://127.0.0.1:5556"
    )
    
    # Subscriber: Binds PUB to *:5556, Connects SUB to 127.0.0.1:5555
    subscriber = ZeroMQTransport(
        pub_addr="tcp://*:5556",
        sub_addr="tcp://127.0.0.1:5555"
    )

    import sys
    
    await publisher.connect()
    await subscriber.connect()
    
    received_events = []
    async def handler(message):
        received_events.append(message)

    await subscriber.subscribe("test_topic", handler)
    
    # Give time for connection to be established (TCP takes longer)
    await asyncio.sleep(2.0)
    
    await publisher.publish("test_topic", {"msg": "hello zmq"})
    
    # Give time for message delivery
    await asyncio.sleep(2.0)
    
    assert len(received_events) == 1
    assert received_events[0].payload == {"msg": "hello zmq"}
    assert received_events[0].channel == "test_topic"
    
    await publisher.close()
    await subscriber.close()
            
    assert len(received_events) > 0
    assert received_events[0].payload["msg"] == "hello zmq"
    assert received_events[0].channel == "test_topic"
    
    await publisher.close()
    await subscriber.close()
