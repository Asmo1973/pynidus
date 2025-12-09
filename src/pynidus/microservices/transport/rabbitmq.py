import asyncio
import logging
from typing import Any, Callable, Awaitable, Dict, Optional, List
from .base import TransportStrategy, IncomingMessage
import json

try:
    import aio_pika
except ImportError:
    aio_pika = None

logger = logging.getLogger(__name__)

class RabbitMQTransport(TransportStrategy):
    def __init__(self, url: str, exchange_name: str = "pynidus_events"):
        if aio_pika is None:
            raise ImportError("aio-pika is required for RabbitMQTransport. Install with 'pip install pynidus[rabbitmq]'")
            
        self.url = url
        self.exchange_name = exchange_name
        self.connection: Optional[Any] = None
        self.channel: Optional[Any] = None
        self.exchange: Optional[Any] = None
        self.queues: List[Any] = []

    async def connect(self) -> None:
        logger.info(f"Connecting to RabbitMQ at {self.url}")
        self.connection = await aio_pika.connect_robust(self.url)
        self.channel = await self.connection.channel()
        self.exchange = await self.channel.declare_exchange(
            self.exchange_name, aio_pika.ExchangeType.TOPIC, durable=True
        )
        logger.info("Connected to RabbitMQ")

    async def close(self) -> None:
        if self.connection:
            await self.connection.close()
            logger.info("Closed RabbitMQ connection")

    async def publish(self, channel: str, message: Any, headers: Optional[Dict[str, Any]] = None) -> None:
        if not self.exchange:
            raise ConnectionError("Not connected to RabbitMQ")

        # Ensure message is bytes
        if not isinstance(message, (bytes, str)):
             body = json.dumps(message).encode()
             content_type = "application/json"
        elif isinstance(message, str):
             body = message.encode()
             content_type = "text/plain"
        else:
             body = message
             content_type = "application/octet-stream"

        await self.exchange.publish(
            aio_pika.Message(
                body=body,
                content_type=content_type,
                headers=headers or {}
            ),
            routing_key=channel
        )

    async def subscribe(self, channel: str, handler: Callable[[IncomingMessage], Awaitable[None]]) -> None:
        if not self.channel or not self.exchange:
            raise ConnectionError("Not connected to RabbitMQ")

        # Create a temporary exclusive queue for this subscriber (or durable if needed, but keeping simple for now)
        # Using a generated name for exclusive queues, or we could allow naming for competing consumers.
        queue = await self.channel.declare_queue(exclusive=True)
        await queue.bind(self.exchange, routing_key=channel)
        self.queues.append(queue)

        async def callback(message: aio_pika.IncomingMessage):
            async with message.process():
                # Decode payload
                if message.content_type == "application/json":
                    payload = json.loads(message.body.decode())
                elif message.content_type == "text/plain":
                    payload = message.body.decode()
                else:
                    payload = message.body

                incoming = IncomingMessage(
                    payload=payload,
                    channel=message.routing_key,
                    headers=message.headers,
                    # ack/nack handled by context manager 'async with message.process()'
                )
                await handler(incoming)

        await queue.consume(callback)
        logger.info(f"Subscribed to {channel}")
