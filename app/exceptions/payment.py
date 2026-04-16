from fastapi import status


class PaymentServiceException(Exception):
    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR
    detail: str = "Internal server error"

class PaymentNotFoundException(PaymentServiceException):
    status_code: int = status.HTTP_404_NOT_FOUND
    detail: str = "Payment with not found."

class APIKeyException(PaymentServiceException):
    status_code: int = status.HTTP_401_UNAUTHORIZED
    detail: str = "Invalid api key"
