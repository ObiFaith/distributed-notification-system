# app/messaging.py
import os
import json
import uuid
import asyncio
import aio_pika
from datetime import datetime, timezone

RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@rabbitmq:5672/")
EX_DIRECT = os.getenv("RABBITMQ_EXCHANGE_DIRECT", "notifications.direct")

async def _publish_async(routing_key: str, payload: dict):
    conn = await aio_pika.connect_robust(RABBITMQ_URL)
    async with conn:
        ch = await conn.channel(publisher_confirms=True)
        ex = await ch.declare_exchange(EX_DIRECT, aio_pika.ExchangeType.DIRECT, durable=True)
        msg = aio_pika.Message(
            body=json.dumps(payload).encode("utf-8"),
            content_type="application/json",
            correlation_id=payload["correlation_id"],
            headers={"idempotency_key": payload["idempotency_key"], "attempt": 0},
            delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
        )
        await ex.publish(msg, routing_key=routing_key)

def publish_notification(
    notification_type: str,
    routing_key: str,
    user_id: str,
    template_code: str,
    language: str,
    data: dict,
    idempotency_key: str | None = None,
    priority: str = "normal",
) -> str:
    """
    Sync wrapper callable from Flask routes. Returns correlation_id.
    """
    cid = str(uuid.uuid4())
    idk = idempotency_key or str(uuid.uuid4())
    payload = {
        "correlation_id": cid,
        "idempotency_key": idk,
        "type": notification_type,  # "email" | "push"
        "requested_at": datetime.now(timezone.utc).isoformat(),
        "priority": priority,
        "user_id": user_id,
        "template_code": template_code,
        "language": language,
        "data": data,
        "options": {"ttl_seconds": 86400},
    }
    asyncio.run(_publish_async(routing_key, payload))
    return cid
