from uuid import UUID
from fastapi import APIRouter, Depends, Header
from typing import Annotated

from app.schemas.payment_dtos import (
    GetPaymentResponseDTO,
    CreatePaymentRequestDTO,
    CreatePaymentResponseDTO,
)
from app.services.payment_service import PaymentService, get_payment_service
from app.schemas.error_response import ErrorResponse
from app.middlewares.security import verify_api_key


payment_router = APIRouter(
    tags=["payments"], 
    prefix="/payments",
    dependencies=[Depends(verify_api_key)]
)

@payment_router.post("", status_code=202)
async def create_payment(
    dto: CreatePaymentRequestDTO,
    service: Annotated[PaymentService, Depends(get_payment_service)],
    idempotency_key: str = Header(),
) -> CreatePaymentResponseDTO:
    return await service.create_payment(
        dto=dto, 
        idempotency_key=idempotency_key
    )

@payment_router.get("/{payment_id}", responses={
    404: {"model": ErrorResponse, "description": "Payment not found"},
})
async def get_payment(
    payment_id: UUID,
    service: Annotated[PaymentService, Depends(get_payment_service)],
) -> GetPaymentResponseDTO:
    return await service.get_payment_by_id(payment_id=payment_id)

