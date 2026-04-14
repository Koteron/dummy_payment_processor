"""
Global Exception Mapping and Response Handling.

This module provides a centralized mechanism for converting custom 
domain exceptions into standardized FastAPI JSON responses with 
appropriate HTTP status codes.
"""

from fastapi import Request, FastAPI
from fastapi.responses import JSONResponse

from app.exceptions.http_exceptions import NotFoundException, ForbiddenException, UnauthorizedException, BadRequestException


def register_global_exception_handler(app: FastAPI) -> None:
    """
    Registers custom exception handlers to the FastAPI application instance.

    By attaching these handlers, the service layer can raise domain-specific 
    exceptions (like NotFoundException) without needing to import 
    FastAPI-specific JSONResponse logic.

    Args:
        app: The root FastAPI application instance.
    """

    @app.exception_handler(NotFoundException)
    async def not_found_handler(
        request: Request,
        exc: NotFoundException
    ):
        return JSONResponse(
            status_code=404,
            content={"detail": str(exc)}
        )
    
    @app.exception_handler(ForbiddenException)
    async def forbidden_handler(
        request: Request,
        exc: ForbiddenException
    ):
        return JSONResponse(
            status_code=403,
            content={"detail": str(exc)}
        )
    
    @app.exception_handler(UnauthorizedException)
    async def unauthorized_handler(
        request: Request,
        exc: UnauthorizedException
    ):
        return JSONResponse(
            status_code=401,
            content={"detail": str(exc)}
        )
    
    @app.exception_handler(BadRequestException)
    async def _handler(
        request: Request,
        exc: BadRequestException
    ):
        return JSONResponse(
            status_code=400,
            content={"detail": str(exc)}
        )
