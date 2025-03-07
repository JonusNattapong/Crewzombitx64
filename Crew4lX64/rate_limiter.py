import asyncio
import time
from collections import defaultdict
from typing import Dict

class DomainStats:
    def __init__(self):
        self.last_request = 0
        self.total_requests = 0
        self.request_times = []
        self.error_count = 0

class RateLimiter:
    def __init__(self, requests_per_second: float = 1.0, burst_size: int = 3):
        self.rate = requests_per_second
        self.burst_size = burst_size
        self.domains: Dict[str, DomainStats] = defaultdict(DomainStats)
        self.last_cleanup = time.time()
        self.cleanup_interval = 3600  # 1 hour

    async def wait(self, url: str) -> None:
        """Wait appropriate time before making request to respect rate limits."""
        try:
            from urllib.parse import urlparse
            domain = urlparse(url).netloc
            
            # Cleanup old domain stats periodically
            current_time = time.time()
            if current_time - self.last_cleanup > self.cleanup_interval:
                self._cleanup_old_domains()
                self.last_cleanup = current_time

            stats = self.domains[domain]
            time_since_last = current_time - stats.last_request

            # Calculate required delay
            if time_since_last < (1.0 / self.rate):
                delay = (1.0 / self.rate) - time_since_last
                
                # Apply burst allowance
                if stats.total_requests < self.burst_size:
                    delay = delay / 2
                
                await asyncio.sleep(delay)

            # Update stats
            stats.last_request = time.time()
            stats.total_requests += 1
            stats.request_times.append(current_time)
            
            # Keep only recent request times
            cutoff = current_time - 60  # Last minute
            stats.request_times = [t for t in stats.request_times if t > cutoff]

        except Exception as e:
            print(f"Rate limiting error: {str(e)}")
            await asyncio.sleep(1.0 / self.rate)  # Default delay on error

    def _cleanup_old_domains(self) -> None:
        """Remove stats for domains not accessed recently."""
        current_time = time.time()
        cutoff = current_time - self.cleanup_interval
        self.domains = {
            domain: stats
            for domain, stats in self.domains.items()
            if stats.last_request > cutoff
        }
