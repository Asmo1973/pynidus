import logging
import asyncio
from typing import Dict, Callable, Any
from .transport.base import TransportStrategy, IncomingMessage
from .decorators import EVENT_HANDLERS

logger = logging.getLogger(__name__)

class MicroserviceListener:
    def __init__(self, transport: TransportStrategy):
        self.transport = transport
        self._running = False

    async def start(self):
        self._running = True
        await self.transport.connect()
        
        # Subscribe to all registered patterns
        for pattern, handler in EVENT_HANDLERS.items():
            logger.info(f"Subscribing to {pattern}")
            await self.transport.subscribe(pattern, self._create_handler_wrapper(handler))

    async def stop(self):
        self._running = False
        await self.transport.close()

    def _create_handler_wrapper(self, handler: Callable):
        async def wrapper(message: IncomingMessage):
            try:
                # In a real app, we might need to instantiate a controller class here
                # or use dependency injection to get the instance.
                # For simplicity, we assume the handler is a standalone function or bound method
                # if registered correctly (which is tricky with decorators on methods).
                
                # If the handler is a method on a class, EVENT_HANDLERS will hold the unbound function
                # unless we handle instance creation. 
                # For this MVP, let's assume handlers are simple functions or static methods,
                # or we manually register bound methods.
                
                # TODO: Integrate with DI container to resolve controller instances.
                
                await handler(message.payload)
                if message.ack:
                    await message.ack()
            except Exception as e:
                logger.error(f"Error handling message on {message.channel}: {e}")
                if message.nack:
                    await message.nack()
        return wrapper
