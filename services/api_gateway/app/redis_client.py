# app/redis_client.py
import redis.asyncio as aioredis # this is async redis client library for pythpn 
import os    # neccessary for 
import json
from typing import Optional

REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")

"""Created a class that for using redis which is a fast in memory data store,
we can of think of it as "temporary memory"
we need this because the API gateway keep tracks of things that shouldn't be 
stored permanently in a database but are important for the main time."""

class RedisClient:
    #this is how to create a class in python, creates an empty connection attribute
    def __init__(self):
        self.redis = None
        
    #this part is a method in the class that helps with opening and closing a redis connection to the redis server 
    #utf 8 ensure text encoding while decode_response makes sure that redis returns strings and not bytes

    async def connect(self):
        self.redis = await aioredis.from_url(REDIS_URL, encoding="utf-8", decode_responses=True)

    async def close(self):
        if self.redis:
            await self.redis.close()

    """probabaly the most important part of the redis connection is this : 
    the code below prevents duplicate request, it helps in locking a unique id
    using setnx(set if doesnt exists)
    """


    # Idempotency: setnx -> if key not exists, set and return True else False
    async def acquire_idempotency(self, request_id: str, ttl_seconds: int = 3600) -> bool:
        # returns True if it acquired lock (i.e., not seen before)
        set_result = await self.redis.setnx(f"idempotency:{request_id}", "1")
        if set_result:
            await self.redis.expire(f"idempotency:{request_id}", ttl_seconds)
            return True
        return False

    """
    Whenever your API Gateway changes the status of a request — for example:
    when its queued in RabbitMQ, when it fails to publish,
    or when its retried,it stores that info temporarily in Redis.
    """
    # status storage: notification_status:{request_id} -> json
    async def set_status(self, request_id: str, status_obj: dict, ttl_seconds: int = 3600):
        await self.redis.set(f"notification_status:{request_id}", json.dumps(status_obj), ex=ttl_seconds)

    async def get_status(self, request_id: str) -> Optional[dict]:
        raw = await self.redis.get(f"notification_status:{request_id}")
        if raw:
            return json.loads(raw)
        return None

redis_client = RedisClient()
