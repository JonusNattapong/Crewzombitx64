import asyncio
import time

class RateLimiter:
    def __init__(self, requests_per_second=1):
        self.delay = 1.0 / requests_per_second
        self.last_request_time = 0
        self.lock = asyncio.Lock()

    async def wait(self):
        async with self.lock:
            elapsed = time.time() - self.last_request_time
            if elapsed < self.delay:
                await asyncio.sleep(self.delay - elapsed)
            self.last_request_time = time.time()
