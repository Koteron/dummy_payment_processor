import uvicorn
from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.exceptions.global_handler import register_global_exception_handler
from app.config.logging import setup_logging
from app.routers.payment_router import payment_router


@asynccontextmanager
async def lifespan(app):
    setup_logging()
    yield

app = FastAPI(lifespan=lifespan)

app.include_router(payment_router, prefix="/api/v1")

register_global_exception_handler(app)


if __name__ == "__main__":
    uvicorn.run("app.app:app", host="0.0.0.0", port=8000)
