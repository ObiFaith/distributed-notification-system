# app/rabbitmq.py
"""This is basically like my messenger that is carrying validated requests from the API Gateway to RabbitMQ"""
import aio_pika #an asynchronous Python library for connecting to RabbitMQ.
import os
import asyncio
import json
from tenacity import retry, wait_exponential, stop_after_attempt  #a retry library. It lets us automatically retry if publishing fails (e.g., network issues)

#Tries to read the RabbitMQ connection URL from environment variables (RABBIT_URL).
RABBIT_URL = os.getenv("RABBIT_URL", "amqp://guest:guest@rabbitmq:5672/")

"""Below defines how our messages are organized inside RabbitMQ:
    | Term            | Meaning                                                               |
| --------------- | --------------------------------------------------------------------- |
| **Exchange**    | The "post office" that routes messages to the right queues.           |
| **Routing Key** | The "address label" that decides where a message goes.                |
| **Queue**       | The actual mailbox that holds messages until a service consumes them. |

In this project:

notifications.direct is the exchange (type = direct).

When the gateway sends a message with routing key "email", it goes to email.queue.

When it sends a message with "push", it goes to push.queue.

If something fails permanently, it goes to failed.queue.

"""

EXCHANGE_NAME = "notifications.direct"
EMAIL_ROUTING_KEY = "email"
PUSH_ROUTING_KEY = "push"
FAILED_ROUTING_KEY = "failed"

class RabbitPublisher:
    def __init__(self):
        self.connection = None
        self.channel = None
        self.exchange = None

    @retry(wait=wait_exponential(multiplier=1, min=1, max=10), stop=stop_after_attempt(10))
    async def connect(self):
        """Try connecting to RabbitMQ until it succeeds"""
        print("⏳ Connecting to RabbitMQ...")
        self.connection = await aio_pika.connect_robust(RABBIT_URL, ssl=True, ssl_options=None)
        self.channel = await self.connection.channel()
        self.exchange = await self.channel.declare_exchange(
            EXCHANGE_NAME, aio_pika.ExchangeType.DIRECT, durable=True
        )
        print("✅ Connected to RabbitMQ!")

    async def close(self):
        if self.connection:
            await self.connection.close()

    @retry(wait=wait_exponential(multiplier=1, min=1, max=10), stop=stop_after_attempt(5))
    async def publish(self, routing_key: str, message_body: dict):
        if not self.exchange:
            await self.connect()
        message = aio_pika.Message(
            body=json.dumps(message_body).encode(),
            delivery_mode=aio_pika.DeliveryMode.PERSISTENT
        )
        await self.exchange.publish(message, routing_key=routing_key)

rabbit_publisher = RabbitPublisher()