from fastapi import APIRouter, Depends, Header
from typing import Annotated

from app.schemas.payment_dtos import (
    GetPaymentResponseDTO,
    CreatePaymentRequestDTO,
    CreatePaymentResponseDTO,
)
from app.services.payment_service import PaymentService, get_payment_service
from app.schemas.error_response import ErrorResponse


payment_router = APIRouter(tags=["payments"])

@payment_router.post("/register/", responses={
    403: {"model": ErrorResponse, "description": "Idempotency key already in use"},
})
async def create(
    dto: CreatePaymentRequestDTO,
    idempotency_key: Annotated[str, Header(None)],
    service: Annotated[PaymentService, Depends(get_payment_service)],
) -> CreatePaymentResponseDTO:
    return await service.create_payment(
        dto=dto, 
        idempotency_key=idempotency_key
    )

@payment_router.post("/register/", responses={
    403: {"model": ErrorResponse, "description": "Idempotency key already in use"},
})
async def create(
    dto: CreatePaymentRequestDTO,
    idempotency_key: Annotated[str, Header(None)],
    service: Annotated[PaymentService, Depends(get_payment_service)],
) -> CreatePaymentResponseDTO:
    return await service.create_payment(
        dto=dto, 
        idempotency_key=idempotency_key
    )

