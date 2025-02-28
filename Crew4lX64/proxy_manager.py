import asyncio
import logging
import aiohttp
import time
import random

class ProxyManager:
    def __init__(self, proxies=None, min_proxy_score=0.7):
        self.proxies = []
        self.proxy_stats = {}
        self.current_index = 0
        self.lock = asyncio.Lock()
        self.min_proxy_score = min_proxy_score
        
        if proxies:
            self.add_proxies(proxies)

    def add_proxies(self, new_proxies):
        for proxy in new_proxies:
            if self._validate_proxy_format(proxy):
                self.proxies.append(proxy)
                self.proxy_stats[proxy] = {
                    'success': 0,
                    'failure': 0,
                    'last_used': 0,
                    'average_response_time': 0
                }

    async def load_from_file(self, filename):
        try:
            with open(filename, 'r') as f:
                new_proxies = [line.strip() for line in f if line.strip()]
            self.add_proxies(new_proxies)
            logging.info(f"Loaded {len(new_proxies)} proxies from {filename}")
        except Exception as e:
            logging.error(f"Failed to load proxies: {e}")

    def _validate_proxy_format(self, proxy):
        if not isinstance(proxy, str):
            return False
        
        # Check for basic proxy format (ip:port or protocol://ip:port)
        parts = proxy.split('://')
        if len(parts) == 2:
            protocol, address = parts
            if protocol not in ['http', 'https', 'socks4', 'socks5']:
                return False
        elif len(parts) == 1:
            address = parts[0]
        else:
            return False
            
        # Validate IP:PORT format
        try:
            ip, port = address.split(':')
            port = int(port)
            if not (0 <= port <= 65535):
                return False
            ip_parts = ip.split('.')
            if len(ip_parts) != 4:
                return False
            for part in ip_parts:
                if not (0 <= int(part) <= 255):
                    return False
            return True
        except:
            return False

    def _calculate_proxy_score(self, proxy):
        stats = self.proxy_stats[proxy]
        total_requests = stats['success'] + stats['failure']
        if total_requests == 0:
            return 1.0  # New proxies get a chance
            
        success_rate = stats['success'] / total_requests
        time_factor = 1.0
        if stats['last_used'] > 0:
            time_since_last_use = time.time() - stats['last_used']
            time_factor = min(1.0, time_since_last_use / 3600)  # Favor proxies not used in the last hour
            
        response_time_score = 1.0
        if stats['average_response_time'] > 0:
            response_time_score = 1.0 / (1 + stats['average_response_time'] / 5)  # Penalize slow proxies
            
        return (success_rate * 0.6 + time_factor * 0.2 + response_time_score * 0.2)

    async def get_next_proxy(self):
        if not self.proxies:
            return None

        async with self.lock:
            # Filter proxies by minimum score
            viable_proxies = [p for p in self.proxies if self._calculate_proxy_score(p) >= self.min_proxy_score]
            if not viable_proxies:
                if len(self.proxies) > 0:
                    logging.warning("No proxies meet minimum score requirement. Using any available proxy.")
                    viable_proxies = self.proxies
                else:
                    return None

            # Choose a proxy using weighted random selection based on scores
            scores = [self._calculate_proxy_score(p) for p in viable_proxies]
            total_score = sum(scores)
            if total_score == 0:
                proxy = random.choice(viable_proxies)
            else:
                weights = [s/total_score for s in scores]
                proxy = random.choices(viable_proxies, weights=weights, k=1)[0]

            self.proxy_stats[proxy]['last_used'] = time.time()
            return proxy

    async def mark_proxy_success(self, proxy, response_time):
        if proxy in self.proxy_stats:
            stats = self.proxy_stats[proxy]
            stats['success'] += 1
            # Update running average of response time
            stats['average_response_time'] = (
                (stats['average_response_time'] * (stats['success'] - 1) + response_time) / 
                stats['success']
            )

    async def mark_proxy_failed(self, proxy):
        async with self.lock:
            if proxy in self.proxy_stats:
                self.proxy_stats[proxy]['failure'] += 1
                if self._calculate_proxy_score(proxy) < self.min_proxy_score:
                    self.proxies.remove(proxy)
                    del self.proxy_stats[proxy]
                    logging.warning(f"Removed low-scoring proxy {proxy}. {len(self.proxies)} remaining.")

    async def verify_proxy(self, proxy):
        try:
            start_time = time.time()
            async with aiohttp.ClientSession() as session:
                async with session.get('https://httpbin.org/ip', 
                                     proxy=proxy, 
                                     timeout=10) as response:
                    if response.status == 200:
                        response_time = time.time() - start_time
                        await self.mark_proxy_success(proxy, response_time)
                        return True
        except:
            await self.mark_proxy_failed(proxy)
            return False
        return False
