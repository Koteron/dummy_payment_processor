from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.exceptions.global_handler import register_global_exception_handler


@asynccontextmanager
def lifespan(app):
    yield

app = FastAPI(lifespan=lifespan)

register_global_exception_handler(app)