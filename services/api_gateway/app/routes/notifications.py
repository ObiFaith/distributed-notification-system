# app/routes/notifications.py
from fastapi import APIRouter, Depends, HTTPException, status
from app.models import NotificationPayload, ResponseEnvelope
from app.redis_client import redis_client
from app.rabbitmq import rabbit_publisher, EMAIL_ROUTING_KEY, PUSH_ROUTING_KEY
from app.circuit_breaker import gateway_cb
import asyncio
import json, traceback
from fastapi.encoders import jsonable_encoder
import time



router = APIRouter()

@router.post("/v1/notifications", response_model=ResponseEnvelope)
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

    # message = {
    #     "request_id": payload.request_id,
    #     "user_id": str(payload.user_id),
    #     "template": payload.template_code,
    #     "variables": payload.variables.dict(),
    #     "priority": payload.priority,
    #     "timestamp": float(asyncio.get_event_loop().time()),
    # }

    # # Quick test: try serializing BEFORE calling RabbitMQ
    # try:
    #     # Try direct json.dumps first (what rabbit publisher does)
    #     json.dumps(message)
    # except Exception as ser_e:
    #     print("🧪 SERIALIZATION FAILED with json.dumps():", ser_e)
    #     print("Full traceback:\n", traceback.format_exc())

    #     # Try fastapi/pydantic helper to see if that fixes it
    # try:
    #     safe = jsonable_encoder(message)
    #     print("jsonable_encoder converted message successfully. Sample:", safe)
    #     print("Try json.dumps(jsonable_encoder(message)) ...")
    #     json.dumps(safe)  # if this fails we'll see the error
    # except Exception as enc_e:
    #     print("jsonable_encoder also failed:", enc_e)
    #     print("Full traceback:\n", traceback.format_exc())
    # # raise or continue to fail fast for debugging
    # raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    #                     detail=f"Serialization failed:{ser_e}")
    
    # try:
    #     await rabbit_publisher.publish(routing_key, message)
    #     await redis_client.set_status(payload.request_id, {"status": "queued", "detail": f"published to {routing_key}"})
    #     return ResponseEnvelope(success=True, message="Notification queued", data={"request_id": payload.request_id})
    # except Exception as e:
    #     # mark status as failed and rethrow or return friendly message
    #     await redis_client.set_status(payload.request_id, {"status": "failed", "detail": str(e)})
    #     gateway_cb.record_failure()
    #     print(f"[DEBUG] Publish error: {e}")
    #     raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=f"Failed to queue notification:{str(e)}")



# ... inside send_notification(payload: NotificationPayload) after routing_key computed ...

    # Build raw message using Pydantic objects (keep them as-is)
    raw_message = {
        "request_id": payload.request_id,
        "user_id": payload.user_id,               # UUID ok here; we'll encode below
        "template": payload.template_code,        # use template_code field
        "variables": payload.variables,           # Pydantic model instance
        "priority": payload.priority,
        "metadata": payload.metadata,
        "timestamp": time.time(),                 # safe float unix time
    }

    # Serialize safely using FastAPI helper (handles UUID, HttpUrl, Enums, Pydantic models, datetimes)
    try:
        safe_message = jsonable_encoder(raw_message)   # converts to plain JSON-friendly python types
        # double-check JSON serializability (will raise if still something unexpected)
        _ = json.dumps(safe_message)
    except Exception as e:
        # print full traceback to logs so you can inspect exactly what failed
        tb = traceback.format_exc()
        print("🔥 Serialization failed after jsonable_encoder. Traceback:\n", tb)
        # write status to redis and raise friendly exception
        await redis_client.set_status(payload.request_id, {"status": "failed", "detail": f"serialization_error: {str(e)}"})
        gateway_cb.record_failure()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Serialization failed: {str(e)}")

    # Now publish (safe_message is JSON serializable)
    try:
        await rabbit_publisher.publish(routing_key, safe_message)
        await redis_client.set_status(payload.request_id, {"status": "queued", "detail": f"published to {routing_key}"})
        return ResponseEnvelope(success=True, message="Notification queued", data={"request_id": payload.request_id})
    except Exception as e:
        # log full exception & traceback
        tb = traceback.format_exc()
        print(f"[DEBUG] Publish error: {e}\n{tb}")
        await redis_client.set_status(payload.request_id, {"status": "failed", "detail": str(e)})
        gateway_cb.record_failure()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to queue notification: {str(e)}")
