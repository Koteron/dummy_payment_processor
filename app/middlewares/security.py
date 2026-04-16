from fastapi import Header

from app.exceptions.payment import APIKeyException
from app.config.settings import settings


def verify_api_key(x_api_key: str = Header(None)):
    if x_api_key != settings.API_SECRET:
        raise APIKeyException()