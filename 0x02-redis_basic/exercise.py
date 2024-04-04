#!/usr/bin/env python3
"""Exercise for Redis"""
import redis
import uuid
from typing import Union, Callable, Optional
from functools import wraps


def count_calls(method: Callable) -> Callable:
    """Decorator count number of calls"""
    key = method.__qualname__

    @wraps(method)
    def wrapper(self, *args, **kwds):
        """Wrapper function"""
        self._redis.incr(key)
        return method(self, *args, **kwds)
    return wrapper


def call_history(method: Callable) -> Callable:
    """Decorator store the history of inputs and outputs"""
    key = method.__qualname__

    @wraps(method)
    def wrapper(self, *args, **kwds):
        """Wrapper function"""
        input = str(args)
        self._redis.rpush("{}:inputs".format(key), input)

        output = str(method(self, *args, **kwds))
        self._redis.rpush("{}:outputs".format(key), output)

        return output
    return wrapper


def replay(method: Callable):
    """Decorator display the history of calls of a particular function"""
    r = redis.Redis()
    key = method.__qualname__

    inputs = r.lrange("{}:inputs".format(key), 0, -1)
    outputs = r.lrange("{}:outputs".format(key), 0, -1)

    print("{} was called {} times:".format(key, r.get(key).decode("utf-8")))

    for i, o in zip(inputs, outputs):
        print("{}(*{}) -> {}".format(key, i.decode("utf-8"),
                                     o.decode("utf-8")))
    return method


class Cache:
    """Cache class"""
    def __init__(self):
        """Constructor"""
        self._redis = redis.Redis()
        self._redis.flushdb()

    @call_history
    @count_calls
    def store(self, data: Union[str, bytes, int, float]) -> str:
        """Store data in Redis"""
        key = str(uuid.uuid4())
        self._redis.mset({key: data})
        return key

    def get(self, key: str, fn: Optional[Callable] = None)\
            -> Union[str, bytes, int, float]:
        """Get data from Redis"""
        data = self._redis.get(key)
        if fn:
            data = fn(data)
        return data

    def get_str(self, key: str) -> str:
        """Convert bytes to str"""
        return self.get(key, str)

    def get_int(self, key: str) -> int:
        """Convert bytes to int"""
        return self.get(key, int)
        
