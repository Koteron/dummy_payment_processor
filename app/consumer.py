import asyncio
import logging
import random
import httpx
from faststream import FastStream
from faststream.rabbit import RabbitMessage
from sqlalchemy import select, update
from sqlalchemy.exc import SQLAlchemyError
from typing import Annotated
from datetime import datetime, timezone
from aiormq import AMQPConnectionError 
from contextlib import aclosing

from app.config.settings import settings
from app.events.payment_events import PaymentCreatedEventPayload
from app.schemas.payment_dtos import ProcessedPaymentNotification
from app.config.db import get_async_session
from app.config.logging import setup_logging
from app.models.payment import Payment
from app.models.util.payment_enums import PaymentStatus
from app.events.event_type import EventType
from app.config.rabbitmq import broker, payments_queue, delayed_exchange


logger = logging.getLogger("app")


async def _notify_webhook(url: str, payment: Payment):
    webhook_payload = ProcessedPaymentNotification(
        payment_id=payment.id,
        status=payment.status,
        idempotency_key=payment.idempotency_key,
        created_at=payment.created_at,
        processed_at=payment.processed_at,
    )
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.post(url, json=webhook_payload.model_dump(mode="json"))
            response.raise_for_status()
    except httpx.ConnectError:
        logger.error(f"Could not connect to webhook-url=({url})")
    except httpx.ReadTimeout:
        logger.error(f"Did not recieve response from webhook server url=({url})")
    except (httpx.InvalidURL, httpx.UnsupportedProtocol):
        logger.error(f"Could not send webhook notification, url=({url}) is invalid")
    except Exception:
        logger.exception(f"There was an error while sending webhook notification url=({url})")


async def _simulate_payment_processing() -> bool:
    await asyncio.sleep(random.uniform(
            settings.CONSUMER_MIN_PROCESS_TIME, 
            settings.CONSUMER_MAX_PROCESS_TIME,
        ))
    return random.random() < settings.CONSUMER_SUCCESS_PROBABILITY


@broker.subscriber(
    queue=payments_queue,
    exchange=delayed_exchange
)
async def handle_payment(event: PaymentCreatedEventPayload, context: Annotated[RabbitMessage, "context"]):
    retry = context.headers.get("retry", 0)
    try:
        async with aclosing(get_async_session()) as session_gen:
            session = await anext(session_gen)
            result = await session.execute(
                select(Payment)
                .where(Payment.idempotency_key == event.payment_idempotency_key)
                .with_for_update()
            )
            payment = result.scalar_one_or_none()

            if payment is None:
                logger.error(f"Could not find payment with "
                            f"idempotency_key=({event.payment_idempotency_key}) in database")
                await context.nack(requeue=False)
                return
            
            if payment.status == PaymentStatus.SUCCEEDED or payment.status == PaymentStatus.FAILED:
                logger.warning(f"Payment with idempotency_key=({event.payment_idempotency_key})"
                            f"is processed already and its status is {payment.status}")
                await context.ack()
                return
            
            if await _simulate_payment_processing():
                logger.info(f"Payment with idempotency_key=({event.payment_idempotency_key}) processed successfully")
                new_status = PaymentStatus.SUCCEEDED
            elif retry >= settings.CONSUMER_MAX_EVENT_RETRIES:
                logger.warning(f"Event for payment with idempotency_key=({event.payment_idempotency_key}) "
                            "exeeded its retries, marking it as FAILED")
                new_status = PaymentStatus.FAILED
            else:
                logger.warning(f"Processing payment with idempotency_key=({event.payment_idempotency_key}) "
                                "failed, retrying...")
                await broker.publish(
                    event.model_dump(),
                    queue=EventType.PAYMENT_CREATED,
                    exchange=delayed_exchange,
                    headers={
                        "retry": retry + 1,
                        "x-delay": settings.CONSUMER_DELAY_EXP_BASE * (2**retry) * 1000,
                    },
                )
                await context.ack()
                return
                
            await session.execute(
                update(Payment)
                .where(Payment.idempotency_key == event.payment_idempotency_key)
                .values(
                    status=new_status,
                    processed_at=datetime.now(timezone.utc),
                )
            )

            await session.commit()

            if new_status == PaymentStatus.SUCCEEDED:
                await context.ack()
            else:
                await context.nack(requeue=False)

            await _notify_webhook(
                url=payment.webhook_url,
                payment=payment,
            )

            logger.info(f"Event with idempotency_key=({event.payment_idempotency_key}) processed")

    except (SQLAlchemyError, OSError):
        logger.error("Database failed, requeueing the message...")
        await context.nack(requeue=True)
        return


@broker.subscriber(EventType.PAYMENT_DEAD_LETTER)
async def dlq_handler(msg: dict):
    print("DEAD LETTER: ", msg)


async def main():
    app = FastStream(broker)
    for _ in range(settings.CONNECTION_RETRIES):
        try:
            await app.run()
            return
        except AMQPConnectionError:
            logger.error(f"Startup failed, could not connect to RabbitMQ, host=({settings.RABBITMQ_HOST})")
            await asyncio.sleep(2)

    raise RuntimeError("App failed to start")


if __name__ == "__main__":
    setup_logging()
    asyncio.run(main())