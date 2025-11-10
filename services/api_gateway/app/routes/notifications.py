# app/routes/notifications.py
from fastapi import APIRouter, Depends, HTTPException, status
from app.models import NotificationPayload, ResponseEnvelope
from app.redis_client import redis_client
from app.rabbitmq import rabbit_publisher, EMAIL_ROUTING_KEY, PUSH_ROUTING_KEY
from app.circuit_breaker import gateway_cb
import asyncio

router = APIRouter()

@router.post("/send-notification", response_model=ResponseEnvelope)
async def send_notification(payload: NotificationPayload):
    """
    1. Idempotency check - ensure request_id processed only once
    2. Set initial status to queued
    3. Publish to RabbitMQ with appropriate routing_key
    4. Return queued response (gateway doesn't wait for delivery)
    """

    # 1) Idempotency
    acquired = await redis_client.acquire_idempotency(payload.request_id, ttl_seconds=3600)
    if not acquired:
        existing = await redis_client.get_status(payload.request_id)
        return ResponseEnvelope(
            success=False,
            data=existing,
            error="duplicate_request",
            message="This request_id has already been processed or is being processed."
        )

    # 2) set queued status
    await redis_client.set_status(payload.request_id, {"status": "queued", "detail": "enqueued at gateway"})

    # 3) Circuit breaker guard (example: don't publish if exchange is failing)
    if not gateway_cb.allow():
        # mark status as failed_short_circuit
        await redis_client.set_status(payload.request_id, {"status": "failed", "detail": "gateway circuit open"})
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Service temporarily unavailable")

    # 4) publish
    routing_key = EMAIL_ROUTING_KEY if payload.notification_type == "email" else PUSH_ROUTING_KEY

    message = {
        "request_id": payload.request_id,
        "user_id": payload.user_id,
        "template": payload.template,
        "variables": payload.variables,
        "priority": payload.priority,
        "timestamp": asyncio.get_event_loop().time(),
    }

    try:
        await rabbit_publisher.publish(routing_key, message)
        await redis_client.set_status(payload.request_id, {"status": "queued", "detail": f"published to {routing_key}"})
        return ResponseEnvelope(success=True, message="Notification queued", data={"request_id": payload.request_id})
    except Exception as e:
        # mark status as failed and rethrow or return friendly message
        await redis_client.set_status(payload.request_id, {"status": "failed", "detail": str(e)})
        gateway_cb.record_failure()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to queue notification")
