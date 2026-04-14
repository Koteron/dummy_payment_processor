"""
Order-Specific Domain Exceptions.

Specialized exceptions for the order lifecycle that map to 
standardized HTTP responses via their parent classes.
"""

from app.exceptions.http_exceptions import NotFoundException, ForbiddenException


class PaymentNotFoundException(NotFoundException):
    def __init__(self, payment_id: int):
        self.payment_id = payment_id
        super().__init__(f"Payment with id=({payment_id}) not found")

class PaymentAlreadyExists(ForbiddenException):
    def __init__(self, idempotency_key: int):
        self.idempotency_key = idempotency_key
        super().__init__(f"Payment with idempotency_key=({idempotency_key}) already exists")
