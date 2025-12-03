import logging
import asyncio
import inspect
from typing import Dict, Callable, Any, Optional
from .transport.base import TransportStrategy, IncomingMessage
from .decorators import EVENT_HANDLERS
from pynidus.core.container import Container

logger = logging.getLogger(__name__)

class MicroserviceListener:
    def __init__(self, transport: TransportStrategy, container: Optional[Container] = None):
        self.transport = transport
        self.container = container or Container.get_instance()
        self._running = False

    async def start(self):
        self._running = True
        await self.transport.connect()
        
        # 1. Subscribe to global handlers (legacy/simple functions)
        for pattern, handler in EVENT_HANDLERS.items():
            # Skip if it looks like a method (has dot in qualname)
            # This prevents subscribing to unbound methods that should be handled via Controllers
            if "." in getattr(handler, "__qualname__", ""):
                logger.info(f"Skipping global subscription for method {handler.__qualname__}")
                continue
                
            logger.info(f"Subscribing to {pattern} (Global Handler)")
            asyncio.create_task(self.transport.subscribe(pattern, self._create_handler_wrapper(handler)))

        # 2. Scan registered controllers in Container
        await self._scan_controllers_async()

    async def _scan_controllers_async(self):
        for cls in self.container._providers.values():
            if getattr(cls, "__is_controller__", False):
                await self._register_controller_methods(cls)

    async def _register_controller_methods(self, cls):
        # Resolve instance
        instance = self.container.resolve(cls)
        
        # Inspect all attributes of the class to find decorated methods
        for name in dir(cls):
            try:
                # Get the function from the class (unbound) to check for metadata
                func = getattr(cls, name)
                pattern = getattr(func, "_event_pattern", None)
                
                if pattern:
                    logger.info(f"Subscribing to {pattern} (Controller: {cls.__name__}.{name})")
                    # Pass unbound function and instance to wrapper
                    await self.transport.subscribe(pattern, self._create_handler_wrapper(func, instance))
            except Exception as e:
                logger.warning(f"Error inspecting attribute {name} on {cls.__name__}: {e}")

    async def stop(self):
        self._running = False
        await self.transport.close()

    def _create_handler_wrapper(self, handler: Callable, instance: Any = None):
        async def wrapper(message: IncomingMessage):
            try:
                # We assume the handler accepts the payload.
                if instance:
                    # Call unbound function with instance (self) and payload
                    await handler(instance, message.payload)
                else:
                    # Call bound method or function
                    await handler(message.payload)
                     
                if message.ack:
                    await message.ack()
            except Exception as e:
                logger.error(f"Error handling message on {message.channel}: {e}")
                if message.nack:
                    await message.nack()
        return wrapper
