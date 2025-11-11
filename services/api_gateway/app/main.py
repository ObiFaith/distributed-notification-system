# app/main.py
from fastapi import FastAPI
from app.routes import notifications, health
from app.redis_client import redis_client
from app.rabbitmq import rabbit_publisher

app = FastAPI(title="Notification API Gateway", version="0.1.0")

app.include_router(notifications.router, prefix="/api")
app.include_router(health.router, prefix="/api")

@app.on_event("startup")
async def startup_event():
    await redis_client.connect()
    await rabbit_publisher.connect()

@app.on_event("shutdown")
async def shutdown_event():
    await rabbit_publisher.close()
    await redis_client.close()
