import asyncio
import logging
import aiohttp
import time
import random
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple
from datetime import datetime, timedelta
from enum import Enum
import json
from pathlib import Path

class ProxyRotationStrategy(Enum):
    """Strategy for selecting the next proxy."""
    ROUND_ROBIN = "round_robin"
    WEIGHTED_RANDOM = "weighted_random"
    LEAST_USED = "least_used"
    BEST_PERFORMANCE = "best_performance"

@dataclass
class ProxyStats:
    """Statistics for a specific proxy."""
    success: int = 0
    failure: int = 0
    last_used: float = field(default_factory=time.time)
    average_response_time: float = 0.0
    last_check: float = field(default_factory=time.time)
    consecutive_failures: int = 0
    total_bytes: int = 0
    is_available: bool = True
    protocols: Set[str] = field(default_factory=set)
    locations: Set[str] = field(default_factory=set)
    verification_attempts: int = 0

class ProxyManager:
    """Advanced proxy manager with health monitoring and rotation strategies."""
    def __init__(self, proxies: Optional[List[str]] = None, 
                 min_proxy_score: float = 0.7,
                 rotation_strategy: ProxyRotationStrategy = ProxyRotationStrategy.WEIGHTED_RANDOM):
        self.proxies: List[str] = []
        self.proxy_stats: Dict[str, ProxyStats] = {}
        self.current_index: int = 0
        self.lock = asyncio.Lock()
        self.min_proxy_score = min_proxy_score
        self.rotation_strategy = rotation_strategy
        self.health_check_interval = 300  # 5 minutes
        self.max_consecutive_failures = 3
        self.verification_timeout = 10
        
        if proxies:
            self.add_proxies(proxies)

    def add_proxies(self, new_proxies: List[str]) -> None:
        for proxy in new_proxies:
            if self._validate_proxy_format(proxy):
                self.proxies.append(proxy)
                self.proxy_stats[proxy] = {
                    'success': 0,
                    'failure': 0,
                    'last_used': 0,
                    'average_response_time': 0
                }

    async def load_from_file(self, filename: str) -> None:
        try:
            with open(filename, 'r') as f:
                new_proxies = [line.strip() for line in f if line.strip()]
            self.add_proxies(new_proxies)
            logging.info(f"Loaded {len(new_proxies)} proxies from {filename}")
        except Exception as e:
            logging.error(f"Failed to load proxies: {e}")

    def _validate_proxy_format(self, proxy: str) -> bool:
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

    def _calculate_proxy_score(self, proxy: str) -> float:
        """Calculate a proxy's health score based on multiple factors."""
        stats = self.proxy_stats[proxy]
        total_requests = stats.success + stats.failure
        if total_requests == 0:
            return 1.0  # New proxies get a chance
            
        # Calculate success rate with more weight on recent performance
        success_rate = stats.success / total_requests
        if stats.consecutive_failures > 0:
            success_rate *= (0.5 ** stats.consecutive_failures)
            
        # Time factor - favor proxies not used recently
        time_factor = 1.0
        if stats.last_used > 0:
            time_since_last_use = time.time() - stats.last_used
            time_factor = min(1.0, time_since_last_use / 3600)
            
        # Response time score
        response_time_score = 1.0
        if stats.average_response_time > 0:
            response_time_score = 1.0 / (1 + stats.average_response_time / 5)
            
        # Availability factor
        availability = 0.2 if not stats.is_available else 1.0
        
        # Protocol diversity bonus (more protocols = more versatile proxy)
        protocol_bonus = min(1.0, len(stats.protocols) * 0.2)
        
        # Final weighted score
        return (
            success_rate * 0.4 +
            time_factor * 0.15 +
            response_time_score * 0.15 +
            availability * 0.2 +
            protocol_bonus * 0.1
        )

    async def get_next_proxy(self) -> Optional[str]:
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

    async def mark_proxy_success(self, proxy: str, response_time: float, bytes_transferred: int = 0) -> None:
        if proxy in self.proxy_stats:
            stats = self.proxy_stats[proxy]
            stats['success'] += 1
            # Update running average of response time
            stats['average_response_time'] = (
                (stats['average_response_time'] * (stats['success'] - 1) + response_time) / 
                stats['success']
            )

    async def mark_proxy_failed(self, proxy: str) -> None:
        """Mark a proxy as failed and update its statistics."""
        async with self.lock:
            if proxy in self.proxy_stats:
                stats = self.proxy_stats[proxy]
                stats.failure += 1
                stats.consecutive_failures += 1
                stats.last_used = time.time()
                
                # Handle consecutive failures
                if stats.consecutive_failures >= self.max_consecutive_failures:
                    stats.is_available = False
                    logging.warning(f"Proxy {proxy} marked as unavailable after {stats.consecutive_failures} consecutive failures")
                
                # Remove proxy if score is too low
                if self._calculate_proxy_score(proxy) < self.min_proxy_score:
                    self.proxies.remove(proxy)
                    del self.proxy_stats[proxy]
                    logging.warning(f"Removed low-scoring proxy {proxy}. {len(self.proxies)} remaining.")
                
                # Trigger health check if too many proxies are unavailable
                available_proxies = sum(1 for p in self.proxies if self.proxy_stats[p].is_available)
                if available_proxies < len(self.proxies) * 0.5:  # Less than 50% available
                    asyncio.create_task(self._check_unavailable_proxies())

    async def verify_proxy(self, proxy: str) -> Tuple[bool, Optional[float]]:
        """Verify if a proxy is working and measure its response time."""
        try:
            start_time = time.time()
            timeout = aiohttp.ClientTimeout(total=self.verification_timeout)
            
            async with aiohttp.ClientSession(timeout=timeout) as session:
                try:
                    async with session.get('https://httpbin.org/ip', proxy=proxy) as response:
                        if response.status == 200:
                            response_time = time.time() - start_time
                            # Update proxy protocols based on what worked
                            if proxy.startswith('http://'):
                                self.proxy_stats[proxy].protocols.add('http')
                            elif proxy.startswith('https://'):
                                self.proxy_stats[proxy].protocols.add('https')
                            return True, response_time
                except aiohttp.ClientError as e:
                    logging.debug(f"Proxy verification failed for {proxy}: {str(e)}")
                    return False, None
                
            return False, None
        except Exception as e:
            logging.error(f"Proxy verification error for {proxy}: {str(e)}")
            return False, None

    async def verify_proxies_batch(self, batch_size: int = 10) -> None:
        """Verify multiple proxies concurrently."""
        if not self.proxies:
            return

        async def verify_proxy_task(proxy: str) -> None:
            success, response_time = await self.verify_proxy(proxy)
            if success and response_time is not None:
                await self.mark_proxy_success(proxy, response_time)
            else:
                await self.mark_proxy_failed(proxy)

        # Verify proxies in batches
        for i in range(0, len(self.proxies), batch_size):
            batch = self.proxies[i:i + batch_size]
            tasks = [verify_proxy_task(proxy) for proxy in batch]
            await asyncio.gather(*tasks)

    async def _check_unavailable_proxies(self) -> None:
        """Periodically check unavailable proxies to see if they've recovered."""
        unavailable_proxies = [
            proxy for proxy in self.proxies 
            if not self.proxy_stats[proxy].is_available
        ]
        
        for proxy in unavailable_proxies:
            success, response_time = await self.verify_proxy(proxy)
            if success and response_time is not None:
                stats = self.proxy_stats[proxy]
                stats.is_available = True
                stats.consecutive_failures = 0
                await self.mark_proxy_success(proxy, response_time)
                logging.info(f"Proxy {proxy} is available again")

    async def save_state(self, filename: str = 'proxy_state.json') -> None:
        """Save proxy manager state to file."""
        state = {
            'proxies': self.proxies,
            'stats': {
                proxy: {
                    'success': stats.success,
                    'failure': stats.failure,
                    'average_response_time': stats.average_response_time,
                    'is_available': stats.is_available,
                    'protocols': list(stats.protocols),
                    'locations': list(stats.locations)
                }
                for proxy, stats in self.proxy_stats.items()
            }
        }
        
        try:
            with open(filename, 'w') as f:
                json.dump(state, f, indent=2)
        except Exception as e:
            logging.error(f"Failed to save proxy state: {e}")

    async def load_state(self, filename: str = 'proxy_state.json') -> None:
        """Load proxy manager state from file."""
        try:
            with open(filename, 'r') as f:
                state = json.load(f)
                
            self.proxies = state['proxies']
            self.proxy_stats = {
                proxy: ProxyStats(
                    success=stats['success'],
                    failure=stats['failure'],
                    average_response_time=stats['average_response_time'],
                    is_available=stats['is_available'],
                    protocols=set(stats['protocols']),
                    locations=set(stats['locations'])
                )
                for proxy, stats in state['stats'].items()
            }
        except Exception as e:
            logging.error(f"Failed to load proxy state: {e}")
