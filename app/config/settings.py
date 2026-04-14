from pydantic import model_validator
from pydantic_settings import BaseSettings
from typing import Optional
from typing_extensions import Self


class Settings(BaseSettings):

    API_SECRET: str

    DB_USER: str = "user"
    DB_PASSWORD: str = "password"
    DB_HOST: str = "localhost"
    DB_NAME: str = "mydb"
    DB_PORT: int = 5432

    RABBITMQ_USER: str = "user"
    RABBITMQ_PASSWORD: str = "password"
    RABBITMQ_HOST: str = "localhost"
    RABBITMQ_PORT: int = 5672

    RABBITMQ_URL: Optional[str] = None
    DATABASE_URL: Optional[str] = None

    LOG_LEVEL: str = "INFO"
    BACKGROUND_SLEEP_TIME: float = 1.0
    BACKGROUND_BATCH_SIZE: int = 50
    DO_BACKGROUND_CHECKING_LOG: bool = True
    DO_BACKGROUND_WORKER_AMOUNT: int = 2

    @model_validator(mode="after")
    def assemble_urls(self) -> Self:
        if not self.DATABASE_URL:
            self.DATABASE_URL = (
                f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@"
                f"{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
            )
        if not self.RABBITMQ_URL:
            self.RABBITMQ_URL = (
                f"amqp://{self.RABBITMQ_USER}:{self.RABBITMQ_PASSWORD}@"
                f"{self.RABBITMQ_HOST}:{self.RABBITMQ_PORT}/"
            )
        return self

settings = Settings()