from datetime import datetime, timezone
from typing import Optional, Any
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import JSON, String, DateTime
from pynidus.db.base import Base
import uuid

class OutboxMessage(Base):
    __tablename__ = "outbox_messages"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    channel: Mapped[str] = mapped_column(String, nullable=False)
    payload: Mapped[Any] = mapped_column(JSON, nullable=False)
    headers: Mapped[Optional[Any]] = mapped_column(JSON, nullable=True)
    status: Mapped[str] = mapped_column(String, default="PENDING", index=True) # PENDING, PUBLISHED, FAILED
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    processed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    error: Mapped[Optional[str]] = mapped_column(String, nullable=True)
