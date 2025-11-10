# app/routes/health.py
from fastapi import APIRouter
from app.models import ResponseEnvelope
from app.redis_client import redis_client
from app.rabbitmq import rabbit_publisher

router = APIRouter()

@router.get("/health")
async def health():
    """
    Basic health check that ensures:
    - Redis reachable
    - RabbitMQ connection established
    - Return basic status
    """
    status = {"redis": False, "rabbitmq": False}
    try:
        # quick check
        if redis_client.redis:
            await redis_client.redis.ping()
            status["redis"] = True
    except Exception:
        status["redis"] = False

    try:
        if rabbit_publisher.connection:
            status["rabbitmq"] = True
    except Exception:
        status["rabbitmq"] = False

    ok = all(status.values())
    return ResponseEnvelope(success=ok, message="health check", data=status)

@router.get("/status/{request_id}", response_model=ResponseEnvelope)
async def get_status(request_id: str):
    s = await redis_client.get_status(request_id)
    if not s:
        return ResponseEnvelope(success=False, message="Not found", error="not_found")
    return ResponseEnvelope(success=True, message="status fetched", data=s)
