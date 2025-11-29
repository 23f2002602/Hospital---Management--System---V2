# backend/utils/cache_utils.py
import json
from functools import wraps
from flask import make_response, jsonify, request
from flask import current_app

def cache_response(cache, key_func, ttl_getter):
    def decorator(fn):
        @wraps(fn)
        def wrapped(*args, **kwargs):
            try:
                key = key_func(*args, **kwargs)
            except Exception:
                return fn(*args, **kwargs)

            try:
                cached = cache.get(key)
            except Exception:
                cached = None

            if cached is not None:
                try:
                    data = json.loads(cached)
                except Exception:
                    data = cached
                resp = make_response(jsonify(data), 200)
                resp.headers["X-Cache"] = "HIT"
                return resp

            result = fn(*args, **kwargs)
            # normalize result -> (data, status)
            if hasattr(result, "get_json"):
                data = result.get_json()
                status = result.status_code
            else:
                try:
                    data, status = result
                except Exception:
                    data = result
                    status = 200

            try:
                cache.set(key, json.dumps(data), timeout=ttl_getter())
            except Exception:
                current_app.logger.exception("cache.set failed for key %s", key)

            resp = make_response(jsonify(data), status)
            resp.headers["X-Cache"] = "MISS"
            return resp
        return wrapped
    return decorator
