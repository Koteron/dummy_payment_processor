from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field
from decimal import Decimal
from typing import Any, Annotated
from datetime import datetime

from app.models.util.payment_enums import Currency,PaymentStatus


class GetPaymentResponseDTO(BaseModel):
    id: UUID
    value: Decimal
    currency: Currency
    description: str
    meta: dict[str, Any]
    status: PaymentStatus
    idempotency_key: str
    webhook_url: str
    created_at: datetime
    processed_at: datetime | None

    model_config = ConfigDict(from_attributes=True)

class CreatePaymentRequestDTO(BaseModel):
    value: Annotated[Decimal, Field(gt=Decimal("0"))]
    currency: Currency
    description: str
    meta: dict[str, Any]
    webhook_url: str

class CreatePaymentResponseDTO(BaseModel):
    payment_id: UUID
    status: PaymentStatus
    created_at: datetime

class ProcessedPaymentNotification(CreatePaymentResponseDTO):
    processed_at: datetime
    idempotency_key: str