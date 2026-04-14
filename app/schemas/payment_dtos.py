from uuid import UUID
from pydantic import BaseModel
from decimal import Decimal
from typing import Any
from datetime import datetime

from app.models.util.currency import Currency
from app.models.util.payment_status import PaymentStatus


class GetPaymentResponseDTO(BaseModel):
    id: UUID
    value: Decimal
    currency: Currency
    description: str
    meta: list[dict[str, Any]]
    status: PaymentStatus
    idempotency_key: str
    webhook_url: str
    created_at: datetime
    processed_at: datetime | None

    model_config = {
        "from_attributes": True
    }

class CreatePaymentRequestDTO(BaseModel):
    value: Decimal
    currency: Currency
    description: str
    meta: list[dict[str, Any]]
    webhook_url: str

class CreatePaymentResponseDTO(BaseModel):
    payment_id: UUID
    status: PaymentStatus
    created_at: datetime