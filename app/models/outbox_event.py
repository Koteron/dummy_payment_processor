from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Index, DateTime
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime, timezone
from typing import Any

from app.models.base import Base
from app.models.util.outbox_status import OutboxStatus
from app.events.event_type import EventType


class OutboxEvent(Base):
    __tablename__ = "outbox_events"

    idempotency_key: Mapped[str] = mapped_column(primary_key=True)
    event_type: Mapped[EventType]
    payload: Mapped[dict[str, Any]] = mapped_column(JSONB)
    status: Mapped[OutboxStatus] = mapped_column(default=OutboxStatus.UNSENT)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        Index("ix_outbox_status_created_at", "status", "created_at"),
    )

