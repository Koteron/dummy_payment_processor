import asyncio
import logging
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from faststream.rabbit import RabbitBroker
from aiormq import AMQPConnectionError 
from contextlib import aclosing

from app.models.outbox_event import OutboxEvent
from app.models.util.outbox_status import OutboxStatus
from app.config.settings import settings
from app.config.db import get_async_session
from app.config.logging import setup_logging
from app.config.rabbitmq import broker


logger = logging.getLogger("app")

async def _process_outbox_batch(session: AsyncSession, started_broker: RabbitBroker) -> bool:
    if settings.OUTBOX_WORKER_DO_CHECKING_LOG:
        logger.info("Checking for outbox events...")

    result = await session.execute(
        select(OutboxEvent)
        .where(OutboxEvent.status == OutboxStatus.UNSENT)
        .limit(settings.OUTBOX_WORKER_BATCH_SIZE)
        .with_for_update(skip_locked=True)
    )

    events = result.scalars().all()

    if not events:
        if settings.OUTBOX_WORKER_DO_CHECKING_LOG:
            logger.info("No outbox events found")

        await asyncio.sleep(settings.OUTBOX_WORKER_QUERY_SLEEP_TIME)
        return False

    for event in events:
        await started_broker.publish(
            event.payload,
            queue=event.event_type,
        )

    await session.execute(
        update(OutboxEvent)
        .where(OutboxEvent.idempotency_key.in_([e.idempotency_key for e in events]))
        .values(status=OutboxStatus.SENT)
    )

    await session.commit()

    logger.info("Processed %d event(s)", len(events))

    return True


async def start_outbox_publisher():
    async with broker as started_broker:
        while True:
            if not broker._connection or not broker._connection.connected.is_set():
                if settings.OUTBOX_WORKER_DO_CHECKING_LOG:
                    logger.warning("Broker disconnected, querying paused...")
                await asyncio.sleep(settings.OUTBOX_WORKER_QUERY_SLEEP_TIME)
                continue
            try:
                async with aclosing(get_async_session()) as session_gen:
                    session = await anext(session_gen)
                    if not await _process_outbox_batch(session, started_broker):
                        await asyncio.sleep(settings.OUTBOX_WORKER_QUERY_SLEEP_TIME)
            except (SQLAlchemyError, ConnectionError, OSError):
                logger.error(
                    "Database error, retrying in %ds...",
                    settings.OUTBOX_WORKER_QUERY_SLEEP_TIME
                )
                await asyncio.sleep(settings.OUTBOX_WORKER_QUERY_SLEEP_TIME)
                continue
            

async def main():
    for _ in range(settings.CONNECTION_RETRIES):
        try:
            await start_outbox_publisher()
            return
        except AMQPConnectionError:
            logger.error(
                "RabbitMQ unreachable, retrying in %ds...",
                settings.OUTBOX_WORKER_STARTUP_SLEEP_TIME
            )
            await asyncio.sleep(settings.OUTBOX_WORKER_STARTUP_SLEEP_TIME)

    logger.error("App failed to start")

if __name__ == "__main__":
    setup_logging()
    asyncio.run(main())
