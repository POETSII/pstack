import json
import redis


def push_json(redis_cl, queue, obj):
    """Push JSON object to Redis queue."""
    obj_str = json.dumps(obj)
    redis_cl.rpush(queue, obj_str)


def pop_json(redis_cl, queue):
    """Pop JSON object from Redis queue."""
    obj_str = redis_cl.blpop(queue)[1]
    return json.loads(obj_str)


def mget(redis_cl, keys, default=None):
    """Get multiple values."""
    if not keys:
        return []

    return [(item if item else default) for item in redis_cl.mget(keys)]
