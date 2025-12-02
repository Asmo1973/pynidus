from typing import Any, Dict, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from .models import OutboxMessage

class TramClient:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def emit(self, channel: str, payload: Any, headers: Optional[Dict[str, Any]] = None) -> OutboxMessage:
        """
        Emits an event by saving it to the outbox table.
        This operation should be part of an active transaction.
        """
        message = OutboxMessage(
            channel=channel,
            payload=payload,
            headers=headers,
            status="PENDING"
        )
        self.session.add(message)
        return message
