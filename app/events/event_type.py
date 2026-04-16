from enum import StrEnum


class EventType(StrEnum):
    PAYMENT_CREATED = "payments.new"
    PAYMENT_DEAD_LETTER = "payments.dlq"