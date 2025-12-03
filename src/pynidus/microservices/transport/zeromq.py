import asyncio
import logging
import zmq
import zmq.asyncio
from typing import Any, Callable, Awaitable, Dict, Optional, List
from .base import TransportStrategy, IncomingMessage
import json

logger = logging.getLogger(__name__)

class ZeroMQTransport(TransportStrategy):
    def __init__(self, pub_port: int = 5555, sub_port: int = 5555, host: str = "127.0.0.1", pub_addr: Optional[str] = None, sub_addr: Optional[str] = None, context: Optional[zmq.asyncio.Context] = None):
        self.pub_port = pub_port
        self.sub_port = sub_port
        self.host = host
        
        # Allow overriding full address (e.g. for inproc://)
        self.pub_addr = pub_addr or f"tcp://{host}:{pub_port}"
        self.sub_addr = sub_addr or f"tcp://{host}:{sub_port}"
        
        self.context: Optional[zmq.asyncio.Context] = context
        self.pub_socket: Optional[zmq.asyncio.Socket] = None
        self.sub_socket: Optional[zmq.asyncio.Socket] = None
        self.handlers: Dict[str, List[Callable[[IncomingMessage], Awaitable[None]]]] = {}
        self._listen_task: Optional[asyncio.Task] = None

    async def connect(self) -> None:
        if not self.context:
            self.context = zmq.asyncio.Context()
        
        # Publisher Socket
        self.pub_socket = self.context.socket(zmq.PUB)
        self.pub_socket.bind(self.pub_addr)
        
        # Subscriber Socket
        self.sub_socket = self.context.socket(zmq.SUB)
        self.sub_socket.connect(self.sub_addr)
        
        self._listen_task = asyncio.create_task(self._listen())
        logger.info(f"ZeroMQ Transport connected (PUB: {self.pub_addr}, SUB: {self.sub_addr})")

    async def close(self) -> None:
        if self._listen_task:
            self._listen_task.cancel()
            try:
                await self._listen_task
            except asyncio.CancelledError:
                pass
        
        if self.pub_socket:
            self.pub_socket.close()
        if self.sub_socket:
            self.sub_socket.close()
        if self.context:
            self.context.term()
        logger.info("Closed ZeroMQ connection")

    async def publish(self, channel: str, message: Any, headers: Optional[Dict[str, Any]] = None) -> None:
        if not self.pub_socket:
            raise ConnectionError("Not connected to ZeroMQ")

        # Format: "channel payload_json"
        if not isinstance(message, (bytes, str)):
             payload = json.dumps(message)
        elif isinstance(message, bytes):
             payload = message.decode()
        else:
             payload = message
        
        parts = [
            channel.encode(),
            json.dumps(headers or {}).encode(),
            payload.encode()
        ]
        
        
        await self.pub_socket.send_multipart(parts)

    async def subscribe(self, channel: str, handler: Callable[[IncomingMessage], Awaitable[None]]) -> None:
        if not self.sub_socket:
            raise ConnectionError("Not connected to ZeroMQ")

        self.sub_socket.setsockopt(zmq.SUBSCRIBE, channel.encode())
        
        if channel not in self.handlers:
            self.handlers[channel] = []
        self.handlers[channel].append(handler)
        logger.info(f"Subscribed to {channel}")

    async def _listen(self):
        while True:
            try:
                if not self.sub_socket:
                    break
                    
                parts = await self.sub_socket.recv_multipart()
                logger.info(f"Received multipart: {parts}")
                if len(parts) < 3:
                    continue
                    
                channel = parts[0].decode()
                headers = json.loads(parts[1].decode())
                payload_raw = parts[2].decode()
                
                # Try to parse JSON payload
                try:
                    payload = json.loads(payload_raw)
                except json.JSONDecodeError:
                    payload = payload_raw

                incoming = IncomingMessage(
                    payload=payload,
                    channel=channel,
                    headers=headers
                )

                if channel in self.handlers:
                    for handler in self.handlers[channel]:
                        asyncio.create_task(handler(incoming))
                        
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in ZeroMQ listener: {e}")
                await asyncio.sleep(0.1)
