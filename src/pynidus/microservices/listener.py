import logging
import asyncio
import inspect
from typing import Dict, Callable, Any, Optional
from .transport.base import TransportStrategy, IncomingMessage
from .decorators import EVENT_HANDLERS
from pynidus.core.container import Container

logger = logging.getLogger(__name__)

from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
from pynidus.tram.models import IncomingMessage as IncomingMessageModel
from sqlalchemy import select
from datetime import datetime, timezone

class MicroserviceListener:
    def __init__(self, transport: TransportStrategy, session_factory: async_sessionmaker[AsyncSession], container: Optional[Container] = None):
        self.transport = transport
        self.session_factory = session_factory
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
                # Extract Message ID
                headers = message.headers or {}
                message_id = headers.get("x-message-id")
                
                if not message_id:
                    logger.warning(f"Received message without x-message-id on {message.channel}. Processing without deduplication.")
                    # Fallback to normal processing
                    if instance:
                        await handler(instance, message.payload)
                    else:
                        await handler(message.payload)
                else:
                    # Deduplication Logic
                    async with self.session_factory() as session:
                        async with session.begin():
                            # Check if exists
                            stmt = select(IncomingMessageModel).where(IncomingMessageModel.id == message_id)
                            result = await session.execute(stmt)
                            existing = result.scalar_one_or_none()
                            
                            if existing:
                                logger.info(f"Duplicate message {message_id} on {message.channel}. Skipping.")
                                if message.ack:
                                    await message.ack()
                                return

                            # Create new record
                            incoming = IncomingMessageModel(
                                id=message_id,
                                channel=message.channel,
                                payload=message.payload,
                                headers=headers,
                                status="PENDING"
                            )
                            session.add(incoming)
                            # Commit to reserve the ID (optimistic locking not needed if we rely on PK constraint)
                            # But we want to process it inside a transaction or after?
                            # Ideally:
                            # 1. Save as PENDING (commit)
                            # 2. Process
                            # 3. Update to PROCESSED (commit)
                            # If 2 fails, we update to FAILED.
                            
                            # For simplicity and atomicity with the handler (if handler does DB work):
                            # We might want to wrap handler in the same transaction?
                            # But handler might have its own transaction logic (e.g. @Transactional).
                            # So let's keep them separate for now or use nested transactions.
                            # Let's stick to the plan: Save PENDING -> Process -> Update PROCESSED.
                        
                        # Now process
                        try:
                            if instance:
                                await handler(instance, message.payload)
                            else:
                                await handler(message.payload)
                                
                            # Update status to PROCESSED
                            async with session.begin():
                                # Re-fetch to attach to session
                                incoming = await session.get(IncomingMessageModel, message_id)
                                if incoming:
                                    incoming.status = "PROCESSED"
                                    incoming.processed_at = datetime.now(timezone.utc)
                                    
                        except Exception as e:
                            logger.error(f"Error processing message {message_id}: {e}")
                            async with session.begin():
                                incoming = await session.get(IncomingMessageModel, message_id)
                                if incoming:
                                    incoming.status = "FAILED"
                                    incoming.error = str(e)
                            raise e # Re-raise to trigger nack

                if message.ack:
                    await message.ack()
            except Exception as e:
                logger.error(f"Error handling message on {message.channel}: {e}")
                if message.nack:
                    await message.nack()
        return wrapper
