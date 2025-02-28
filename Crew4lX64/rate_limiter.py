import asyncio
import time
import random
from collections import defaultdict

class RateLimiter:
    def __init__(self, requests_per_second=1, burst_size=3):
        self.base_delay = 1.0 / requests_per_second
        self.burst_size = burst_size
        self.domain_stats = defaultdict(lambda: {
            'last_request_time': 0,
            'requests_in_window': 0,
            'window_start': time.time(),
            'backoff_factor': 1.0,
            'response_times': [],
            'errors': 0
        })
        self.lock = asyncio.Lock()
        self.window_size = 60  # 1 minute window for rate tracking

    def _get_domain(self, url):
        from urllib.parse import urlparse
        return urlparse(url).netloc

    def _calculate_delay(self, domain_stats):
        current_time = time.time()
        
        # Reset window if needed
        if current_time - domain_stats['window_start'] > self.window_size:
            domain_stats['requests_in_window'] = 0
            domain_stats['window_start'] = current_time
            domain_stats['errors'] = max(0, domain_stats['errors'] - 1)  # Decay error count
            
        # Calculate dynamic delay based on various factors
        base_delay = self.base_delay * domain_stats['backoff_factor']
        
        # Add jitter to prevent synchronization
        jitter = random.uniform(-0.1, 0.1) * base_delay
        delay = base_delay + jitter
        
        # Increase delay if error rate is high
        if domain_stats['errors'] > 0:
            delay *= (1 + domain_stats['errors'] * 0.5)
            
        # Consider response times
        if domain_stats['response_times']:
            avg_response_time = sum(domain_stats['response_times']) / len(domain_stats['response_times'])
            if avg_response_time > 1.0:  # If responses are slow
                delay *= min(2.0, avg_response_time)
                
        return max(0.1, delay)  # Minimum delay of 100ms

    async def wait(self, url=None):
        if not url:
            # Fallback to simple rate limiting if no URL provided
            async with self.lock:
                await asyncio.sleep(self.base_delay)
                return

        domain = self._get_domain(url)
        current_time = time.time()

        async with self.lock:
            stats = self.domain_stats[domain]
            
            # Update request count in current window
            if current_time - stats['window_start'] <= self.window_size:
                stats['requests_in_window'] += 1
            else:
                stats['requests_in_window'] = 1
                stats['window_start'] = current_time

            # Calculate appropriate delay
            delay = self._calculate_delay(stats)
            elapsed = current_time - stats['last_request_time']

            # Apply burst allowance
            if stats['requests_in_window'] <= self.burst_size:
                delay = delay * 0.5

            # Wait if needed
            if elapsed < delay:
                await asyncio.sleep(delay - elapsed)

            stats['last_request_time'] = time.time()

    async def report_result(self, url, success, response_time=None):
        domain = self._get_domain(url)
        stats = self.domain_stats[domain]

        if not success:
            stats['errors'] += 1
            stats['backoff_factor'] = min(4.0, stats['backoff_factor'] * 1.5)
        else:
            stats['errors'] = max(0, stats['errors'] - 0.5)
            stats['backoff_factor'] = max(1.0, stats['backoff_factor'] * 0.9)

        if response_time:
            stats['response_times'].append(response_time)
            if len(stats['response_times']) > 10:
                stats['response_times'].pop(0)
