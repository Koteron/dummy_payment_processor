from fastapi import Request, FastAPI, status
from fastapi.responses import JSONResponse
from sqlalchemy.exc import (
    OperationalError, 
    InterfaceError, 
    IntegrityError,
    NoResultFound,
    SQLAlchemyError,
)

from app.exceptions.payment import (
    PaymentServiceException
)


def register_global_exception_handler(app: FastAPI) -> None:
    @app.exception_handler(OperationalError)
    @app.exception_handler(InterfaceError)
    async def db_fail_handler(request: Request, exc: Exception):
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "detail": "Database connection failed",
            }
        )
    
    @app.exception_handler(NoResultFound)
    async def db_no_result_handler(request: Request, exc: NoResultFound):
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "detail": "No record found",
            }
        )
    
    @app.exception_handler(IntegrityError)
    async def db_integrity_exc_handler(request: Request, exc: IntegrityError):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "detail": "This record already exists or violates database rules",
            }
        )
    
    @app.exception_handler(PaymentServiceException)
    async def payment_service_exc_handler(request: Request, exc: PaymentServiceException):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "detail": exc.detail,
            }
        )

    @app.exception_handler(SQLAlchemyError)
    async def db_general_handler(request: Request, exc: SQLAlchemyError):
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "detail": "An unexpected database error occurred",
            }
        )
