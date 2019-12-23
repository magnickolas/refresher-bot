import asyncio
from concurrent.futures import ThreadPoolExecutor
from functools import wraps


def make_async(f):
    pool = ThreadPoolExecutor()

    @wraps(f)
    def wrapper(*args, **kwargs):
        future = pool.submit(f, *args, **kwargs)
        return asyncio.wrap_future(future)

    return wrapper
