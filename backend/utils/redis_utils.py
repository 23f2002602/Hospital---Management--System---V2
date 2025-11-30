from redis import Redis
from flask import current_app

def redis_client():
    url = current_app.config.get("CACHE_REDIS_URL", "redis://localhost:6379/2")
    return Redis.from_url(url, decode_responses=True)

# Namespace version helpers
def bump_namespace(namespace_key: str):
    """Increment namespace version key (string). Returns new version."""
    r = redis_client()
    return r.incr(namespace_key)

def get_namespace_version(namespace_key: str):
    r = redis_client()
    v = r.get(namespace_key)
    try:
        return int(v) if v is not None else 0
    except Exception:
        return 0