from uuid import UUID, uuid4
from decimal import Decimal
from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy import Numeric, Enum
from sqlalchemy.dialects.postgresql import JSONB
from typing import Any
from datetime import datetime

from app.models.base import Base
from app.models.util.currency import Currency
from app.models.util.payment_status import PaymentStatus


class Payment(Base):
    __tablename__ = "payments"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    value: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    currency: Mapped[Currency] = mapped_column(Enum(Currency, native_enum=False))
    description: Mapped[str] = mapped_column(default="", nullable=False)
    meta: Mapped[list[dict[str, Any]]] = mapped_column(JSONB)
    status: Mapped[PaymentStatus] = mapped_column(Enum(PaymentStatus, native_enum=False), default=PaymentStatus.PENDING)
    idempotency_key: Mapped[str] = mapped_column(unique=True)
    webhook_url: Mapped[str]
    created_at: Mapped[datetime] = mapped_column(default=datetime.now)
    processed_at: Mapped[datetime | None]
