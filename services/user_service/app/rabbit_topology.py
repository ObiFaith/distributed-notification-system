# app/rabbit_topology.py
import os
import asyncio
import aio_pika

RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@rabbitmq:5672/")
EX_DIRECT = os.getenv("RABBITMQ_EXCHANGE_DIRECT", "notifications.direct")
EX_FAILED = os.getenv("RABBITMQ_EXCHANGE_FAILED", "notifications.failed")
RK_EMAIL = os.getenv("RK_EMAIL", "email.notify")
RK_PUSH = os.getenv("RK_PUSH", "push.notify")

async def setup_topology():
    conn = await aio_pika.connect_robust(RABBITMQ_URL)
    async with conn:
        ch = await conn.channel()
        await ch.set_qos(prefetch_count=10)

        ex_direct = await ch.declare_exchange(EX_DIRECT, aio_pika.ExchangeType.DIRECT, durable=True)
        ex_failed = await ch.declare_exchange(EX_FAILED, aio_pika.ExchangeType.FANOUT, durable=True)

        # main queues with DLX -> failed
        q_email = await ch.declare_queue(
            "email.queue", durable=True, arguments={"x-dead-letter-exchange": EX_FAILED}
        )
        q_push = await ch.declare_queue(
            "push.queue", durable=True, arguments={"x-dead-letter-exchange": EX_FAILED}
        )
        q_dlq = await ch.declare_queue("notification.failed", durable=True)

        await q_email.bind(ex_direct, RK_EMAIL)
        await q_push.bind(ex_direct, RK_PUSH)
        await q_dlq.bind(ex_failed)

def ensure_topology():
    try:
        asyncio.run(setup_topology())
    except Exception as e:
        # Do not crash app if broker isn’t up yet.
        print(f"[rabbit_topology] skipped/failed: {e}")
