import logging
from uuid import UUID
from fastapi import Depends
from sqlalchemy import select, literal_column
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated

from app.config.db import get_async_session
from app.models.payment import Payment
from app.models.outbox_event import OutboxEvent
from app.events.payment_events import PaymentCreatedEventPayload
from app.events.event_type import EventType
from app.exceptions.payment import (
    PaymentNotFoundException,
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
            .on_conflict_do_update(
                index_elements=["idempotency_key"],
                set_={
                    "idempotency_key": Payment.idempotency_key # no-op
                }
            )
            .returning(
                Payment.id,
                Payment.status,
                Payment.created_at,
                literal_column("(xmax = 0)").label("is_inserted"),
            )
        )

        row = result.one()

        event = PaymentCreatedEventPayload(
            payment_idempotency_key=idempotency_key,
        )
        
        if row.is_inserted:
            await self.session.execute(
                insert(OutboxEvent)
                .values(
                    payload=event.model_dump(mode="json"),
                    event_type=EventType.PAYMENT_CREATED,
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
            raise PaymentNotFoundException()
        
        return GetPaymentResponseDTO.model_validate(payment)