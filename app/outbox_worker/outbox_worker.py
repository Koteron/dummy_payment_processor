import asyncio
import logging
from sqlalchemy import select, update
from faststream.rabbit import RabbitBroker

from app.models.outbox_event import OutboxEvent
from app.models.util.outbox_status import OutboxStatus
from app.config.settings import settings
from app.config.db import get_async_session


logger = logging.getLogger("app")

async def start_outbox_publisher():
    async with RabbitBroker(settings.RABBITMQ_URL) as broker:
        while True:
            async for session in get_async_session():

                if settings.DO_BACKGROUND_CHECKING_LOG:
                    logger.info("Background: Checking for outbox events")

                result = await session.execute(
                    select(OutboxEvent)
                    .where(OutboxEvent.status == OutboxStatus.UNSENT)
                    .limit(settings.BACKGROUND_BATCH_SIZE)
                    .with_for_update(skip_locked=True)
                )

                events = result.scalars().all()

                if not events:
                    if settings.DO_BACKGROUND_CHECKING_LOG:
                        logger.info("Background: No outbox events found")

                    await asyncio.sleep(settings.BACKGROUND_SLEEP_TIME)
                    continue

                try:
                    for event in events:
                        await broker.publish(
                            {
                                "idempotency_key": event.idempotency_key,
                                **event.payload, 
                            },
                            queue=event.event_type,
                        )

                    await session.execute(
                        update(OutboxEvent)
                        .where(OutboxEvent.idempotency_key.in_([e.idempotency_key for e in events]))
                        .values(processed=OutboxStatus.SENT)
                    )

                    await session.commit()

                    logger.info("Background: Processed %d event(s)", len(events))

                except Exception:
                    await session.rollback()
                    logger.exception("Outbox publish failed")
                    await asyncio.sleep(settings.BACKGROUND_SLEEP_TIME)

            await asyncio.sleep(settings.BACKGROUND_SLEEP_TIME)

if __name__ == "__main__":
    asyncio.run(start_outbox_publisher())