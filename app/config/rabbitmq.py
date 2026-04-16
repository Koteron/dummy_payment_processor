from faststream.rabbit import RabbitBroker, RabbitQueue, RabbitExchange, ExchangeType

from app.events.event_type import EventType
from app.config.settings import settings


delayed_exchange = RabbitExchange(
    name="payments.delayed",
    type=ExchangeType.X_DELAYED_MESSAGE,
    arguments={
        "x-delayed-type": "direct",
    },
)

payments_queue = RabbitQueue(
    name=EventType.PAYMENT_CREATED,
    durable=True,
    arguments={
        "x-dead-letter-exchange": "",
        "x-dead-letter-routing-key": EventType.PAYMENT_DEAD_LETTER,
    },
)

broker = RabbitBroker(settings.RABBITMQ_URL)
