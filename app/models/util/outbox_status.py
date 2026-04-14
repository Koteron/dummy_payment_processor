from enum import StrEnum, auto

class OutboxStatus(StrEnum):
    UNSENT = auto()
    PROCESSING = auto()
    SENT = auto()