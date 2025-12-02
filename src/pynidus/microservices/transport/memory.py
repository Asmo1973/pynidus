import asyncio
from typing import Any, Callable, Awaitable, Dict, Optional, List
from .base import TransportStrategy, IncomingMessage

class MemoryTransport(TransportStrategy):
    def __init__(self):
        self.connected = False
        self.subscribers: Dict[str, List[Callable[[IncomingMessage], Awaitable[None]]]] = {}
        self.published_messages: List[Dict] = []

    async def connect(self) -> None:
        self.connected = True

    async def close(self) -> None:
        self.connected = False

    async def publish(self, channel: str, message: Any, headers: Optional[Dict[str, Any]] = None) -> None:
        if not self.connected:
            raise ConnectionError("Not connected")
        
        self.published_messages.append({"channel": channel, "message": message, "headers": headers})
        
        # Dispatch to subscribers immediately (simulating broker)
        if channel in self.subscribers:
            incoming = IncomingMessage(payload=message, channel=channel, headers=headers)
            for handler in self.subscribers[channel]:
                asyncio.create_task(handler(incoming))

    async def subscribe(self, channel: str, handler: Callable[[IncomingMessage], Awaitable[None]]) -> None:
        if not self.connected:
            raise ConnectionError("Not connected")
        
        if channel not in self.subscribers:
            self.subscribers[channel] = []
        self.subscribers[channel].append(handler)
