import logging
from uuid import UUID
from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated

from app.config.db import get_async_session
from app.models.payment import Payment
from app.models.outbox_event import OutboxEvent
from app.config.settings import settings
from app.exceptions.payment_exceptions import (
    PaymentNotFoundException,
    PaymentAlreadyExists
)
from app.schemas.payment_dtos import (
    GetPaymentResponseDTO,
    CreatePaymentRequestDTO,
    CreatePaymentResponseDTO,
)


logger = logging.getLogger("app")

def get_payment_service(session: Annotated[AsyncSession, Depends(get_async_session)]):
    return PaymentService(session)

class PaymentService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_payment(
        self, 
        dto: CreatePaymentRequestDTO, 
        idempotency_key: str
    ) -> CreatePaymentResponseDTO:
        
        result = await self.session.execute(
            insert(Payment)
            .values(
                value=dto.value,
                currency=dto.currency,
                description=dto.description,
                meta=dto.meta,
                idempotency_key=idempotency_key,
                webhook_url=dto.webhook_url,
            )
            .on_conflict_do_nothing(index_elements=["idempotency_key"])
            .returning(
                Payment.id,
                Payment.status,
                Payment.created_at,
            )
        )

        row = result.one_or_none()
        if row is None:
            raise PaymentAlreadyExists(idempotency_key=idempotency_key)

        await self.session.execute(
            insert(OutboxEvent)
            .values(
                payload={"payment_id": row.id},
                event_type="payments.new",
                idempotency_key=idempotency_key,
            )
        )

        await self.session.commit()

        return CreatePaymentResponseDTO(
            payment_id=row.id,
            status=row.status,
            created_at=row.created_at,
        )
        
    async def get_payment_by_id(self, payment_id: UUID) -> GetPaymentResponseDTO:
        result = await self.session.execute(
            select(Payment)
            .where(Payment.id == payment_id)
        )
        payment = result.scalar_one_or_none()

        if payment is None:
            raise PaymentNotFoundException(payment_id=payment_id)
        
        return GetPaymentResponseDTO.model_validate(payment)