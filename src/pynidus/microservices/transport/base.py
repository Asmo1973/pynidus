from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Callable, Awaitable, Dict, Optional

@dataclass
class IncomingMessage:
    payload: Any
    channel: str
    headers: Optional[Dict[str, Any]] = None
    ack: Optional[Callable[[], Awaitable[None]]] = None
    nack: Optional[Callable[[], Awaitable[None]]] = None

class TransportStrategy(ABC):
    @abstractmethod
    async def connect(self) -> None:
        """Establish connection to the broker."""
        pass

    @abstractmethod
    async def close(self) -> None:
        """Close connection to the broker."""
        pass

    @abstractmethod
    async def publish(self, channel: str, message: Any, headers: Optional[Dict[str, Any]] = None) -> None:
        """Publish a message to a channel/topic."""
        pass

    @abstractmethod
    async def subscribe(self, channel: str, handler: Callable[[IncomingMessage], Awaitable[None]]) -> None:
        """Subscribe to a channel/topic."""
        pass
