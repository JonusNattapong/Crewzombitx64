import asyncio
import time
import random
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import logging

@dataclass
class DomainStats:
    """Statistics for a specific domain."""
    last_request_time: float = field(default_factory=time.time)
    requests_in_window: int = 0
    window_start: float = field(default_factory=time.time)
    backoff_factor: float = 1.0
    response_times: List[float] = field(default_factory=list)
    errors: float = 0
    last_cleanup: float = field(default_factory=time.time)
    total_requests: int = 0
    success_count: int = 0
    fail_count: int = 0
    avg_response_time: float = 0.0
    circuit_breaker_trips: int = 0
    last_circuit_trip: Optional[float] = None

class RateLimiter:
    """Advanced rate limiter with circuit breaker and adaptive throttling."""
    def __init__(self, requests_per_second=1, burst_size=3):
        self.base_delay = 1.0 / requests_per_second
        self.burst_size = burst_size
        self.domain_stats: Dict[str, DomainStats] = defaultdict(DomainStats)
        self.lock = asyncio.Lock()
        self.window_size = 60  # 1 minute window for rate tracking

    def _get_domain(self, url):
        from urllib.parse import urlparse
        return urlparse(url).netloc

    async def _cleanup_old_stats(self) -> None:
        """Clean up stats for domains that haven't been accessed recently."""
        current_time = time.time()
        cleanup_threshold = current_time - (60 * 60)  # 1 hour
        domains_to_remove = []

        for domain, stats in self.domain_stats.items():
            if stats.last_request_time < cleanup_threshold:
                domains_to_remove.append(domain)
            elif current_time - stats.last_cleanup > 300:  # 5 minutes
                # Trim response times list
                if stats.response_times:
                    stats.response_times = stats.response_times[-10:]
                stats.last_cleanup = current_time

        for domain in domains_to_remove:
            del self.domain_stats[domain]

    def _is_circuit_open(self, stats: DomainStats) -> bool:
        """Check if circuit breaker is open for a domain."""
        if stats.last_circuit_trip is None:
            return False

        # Circuit resets after 30 seconds
        if time.time() - stats.last_circuit_trip > 30:
            stats.last_circuit_trip = None
            stats.circuit_breaker_trips = max(0, stats.circuit_breaker_trips - 1)
            return False

        return True

    def _calculate_delay(self, stats: DomainStats) -> float:
        current_time = time.time()
        
        # Reset window if needed
        if current_time - stats.window_start > self.window_size:
            stats.requests_in_window = 0
            stats.window_start = current_time
            stats.errors = max(0, stats.errors - 1)  # Decay error count
            
        # Calculate dynamic delay based on various factors
        base_delay = self.base_delay * stats.backoff_factor
        
        # Calculate error rate
        total_requests = stats.success_count + stats.fail_count
        error_rate = stats.fail_count / total_requests if total_requests > 0 else 0

        # Add jitter to prevent synchronization
        jitter = random.uniform(-0.1, 0.1) * base_delay
        delay = base_delay + jitter
        
        # Increase delay based on error rate
        if error_rate > 0.1:  # More than 10% errors
            delay *= (1 + error_rate * 2)
        
        # Consider response times
        if stats.avg_response_time > 1.0:  # If responses are slow
            delay *= min(2.0, stats.avg_response_time)

        # Add extra delay if circuit breaker was recently tripped
        if stats.circuit_breaker_trips > 0:
            delay *= (1 + stats.circuit_breaker_trips * 0.5)
                
        return max(0.1, delay)  # Minimum delay of 100ms

    async def wait(self, url: Optional[str] = None) -> None:
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

    async def report_result(self, url: str, success: bool, response_time: Optional[float] = None) -> None:
        """Report the result of a request to update statistics and circuit breaker."""
        domain = self._get_domain(url)
        stats = self.domain_stats[domain]
        
        # Update request counts
        stats.total_requests += 1
        if success:
            stats.success_count += 1
            stats.errors = max(0, stats.errors - 0.5)
            stats.backoff_factor = max(1.0, stats.backoff_factor * 0.9)
        else:
            stats.fail_count += 1
            stats.errors += 1
            stats.backoff_factor = min(4.0, stats.backoff_factor * 1.5)
            
            # Check for circuit breaker conditions
            error_rate = stats.fail_count / stats.total_requests
            if error_rate > 0.5 and stats.total_requests >= 10:  # 50% errors after 10 requests
                stats.circuit_breaker_trips += 1
                stats.last_circuit_trip = time.time()
                logging.warning(f"Circuit breaker tripped for domain {domain}. Error rate: {error_rate:.2%}")

        # Update response time statistics
        if response_time:
            stats.response_times.append(response_time)
            # Keep only last 10 response times
            if len(stats.response_times) > 10:
                stats.response_times.pop(0)
            # Update moving average
            stats.avg_response_time = sum(stats.response_times) / len(stats.response_times)

        # Periodically clean up old stats
        await self._cleanup_old_stats()
