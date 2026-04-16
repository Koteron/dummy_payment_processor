from pydantic import BaseModel


class PaymentCreatedEventPayload(BaseModel):
    payment_idempotency_key: str