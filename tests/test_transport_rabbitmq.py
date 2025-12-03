import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from pynidus.microservices.transport.rabbitmq import RabbitMQTransport
from pynidus.microservices.transport.base import IncomingMessage

@pytest.mark.asyncio
async def test_rabbitmq_publish():
    with patch("aio_pika.connect_robust", new_callable=AsyncMock) as mock_connect:
        # Setup mocks
        mock_connection = AsyncMock()
        mock_channel = AsyncMock()
        mock_exchange = AsyncMock()
        
        mock_connect.return_value = mock_connection
        mock_connection.channel.return_value = mock_channel
        mock_channel.declare_exchange.return_value = mock_exchange

        # Test
        transport = RabbitMQTransport("amqp://guest:guest@localhost/")
        await transport.connect()
        
        await transport.publish("test_channel", {"data": "test"})
        
        # Verify
        mock_exchange.publish.assert_called_once()
        call_args = mock_exchange.publish.call_args
        message = call_args[0][0]
        routing_key = call_args[1]['routing_key']
        
        assert routing_key == "test_channel"
        assert b'{"data": "test"}' in message.body
        
        await transport.close()

@pytest.mark.asyncio
async def test_rabbitmq_subscribe():
    with patch("aio_pika.connect_robust", new_callable=AsyncMock) as mock_connect:
        # Setup mocks
        mock_connection = AsyncMock()
        mock_channel = AsyncMock()
        mock_queue = AsyncMock()
        
        mock_connect.return_value = mock_connection
        mock_connection.channel.return_value = mock_channel
        mock_channel.declare_queue.return_value = mock_queue

        # Test
        transport = RabbitMQTransport("amqp://guest:guest@localhost/")
        await transport.connect()
        
        handler = AsyncMock()
        await transport.subscribe("test_channel", handler)
        
        # Verify
        mock_channel.declare_queue.assert_called_once()
        mock_queue.bind.assert_called_once()
        mock_queue.consume.assert_called_once()
        
        await transport.close()
