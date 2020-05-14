import asyncio
from functools import partial
from functools import wraps


def make_async(f):
    @wraps(f)
    async def run(*args, **kwargs):
        loop = asyncio.get_event_loop()
        pf = partial(f, *args, **kwargs)
        return await loop.run_in_executor(None, pf)

    return run
