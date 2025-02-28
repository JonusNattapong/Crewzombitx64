import asyncio
import logging

class ProxyManager:
    def __init__(self, proxies=None):
        self.proxies = proxies or []
        self.current_index = 0
        self.lock = asyncio.Lock()

    async def load_from_file(self, filename):
        try:
            with open(filename, 'r') as f:
                self.proxies = [line.strip() for line in f if line.strip()]
            logging.info(f"Loaded {len(self.proxies)} proxies from {filename}")
        except Exception as e:
            logging.error(f"Failed to load proxies: {e}")

    async def get_next_proxy(self):
        if not self.proxies:
            return None

        async with self.lock:
            proxy = self.proxies[self.current_index]
            self.current_index = (self.current_index + 1) % len(self.proxies)
            return proxy

    async def mark_proxy_failed(self, proxy):
        async with self.lock:
            if proxy in self.proxies:
                self.proxies.remove(proxy)
                logging.warning(f"Removed failed proxy {proxy}. {len(self.proxies)} remaining.")
