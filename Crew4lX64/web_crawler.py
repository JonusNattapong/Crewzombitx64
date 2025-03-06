import aiohttp
import logging
import asyncio
import re
import time
from typing import Optional, Dict, List
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from Crew4lX64.browser_manager import BrowserManager
from Crew4lX64.rate_limiter import RateLimiter
from Crew4lX64.proxy_manager import ProxyManager
from Crew4lX64.content_extractor import ContentExtractor
from Crew4lX64.arxiv_handler import ArxivHandler

class WebCrawler:
    def __init__(self, max_cache_size: int = 1000, max_retries: int = 3):
        self.browser = None
        self.data_extractor = ContentExtractor()
        self.visited_urls: Dict[str, float] = {}  # URL -> timestamp
        self.cache: Dict[str, Dict] = {}
        self.cache_timestamps: Dict[str, float] = {}  # URL -> timestamp
        self.max_cache_size = max_cache_size
        self.max_retries = max_retries
        self.session = None
        self.rate_limiter = RateLimiter()
        self.proxy_manager = None
        self.arxiv_handler = ArxivHandler()
        self.respect_robots = True
        self.include_pattern = None
        self.exclude_pattern = None
        self.allow_subdomains = False
        self.robots_cache: Dict[str, Dict] = {}  # domain -> {rules, timestamp}
        self.robots_cache_ttl = 3600  # 1 hour
        self.stats = {
            'pages_crawled': 0,
            'errors': 0,
            'start_time': None,
            'total_bytes': 0,
            'success_rate': 0.0
        }
        self.github_base_paths = {
            'repo': '/[^/]+/[^/]+$',
            'tree': '/[^/]+/[^/]+/tree/[^/]+',
            'blob': '/[^/]+/[^/]+/blob/[^/]+',
            'raw': '/[^/]+/[^/]+/raw/[^/]+',
            'issues': '/[^/]+/[^/]+/issues',
            'pulls': '/[^/]+/[^/]+/pulls',
            'releases': '/[^/]+/[^/]+/releases'
        }
        self._setup_logging()

    def _cleanup_cache(self) -> None:
        """Remove old entries from cache if it exceeds max size."""
        if len(self.cache) > self.max_cache_size:
            # Sort by timestamp and keep only the newest entries
            sorted_urls = sorted(
                self.cache_timestamps.items(),
                key=lambda x: x[1],
                reverse=True
            )[:self.max_cache_size]
            
            new_cache = {}
            new_timestamps = {}
            for url, timestamp in sorted_urls:
                new_cache[url] = self.cache[url]
                new_timestamps[url] = timestamp
            
            self.cache = new_cache
            self.cache_timestamps = new_timestamps

    def _cleanup_visited_urls(self, max_age: float = 86400) -> None:
        """Remove visited URLs older than max_age seconds."""
        current_time = time.time()
        self.visited_urls = {
            url: timestamp
            for url, timestamp in self.visited_urls.items()
            if current_time - timestamp < max_age
        }

    def _setup_logging(self) -> None:
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

    async def setup(self, use_browser=False, respect_robots=True, rate_limit=1.0, 
                   use_proxies=False, headless=True, wait_time=2.0, auto_scroll=False, 
                   retry_count=3, retry_delay=1.0, proxy_timeout=10.0, 
                   include_pattern=None, exclude_pattern=None, allow_subdomains=False, **kwargs):
        self.respect_robots = respect_robots
        self.rate_limiter = RateLimiter(requests_per_second=rate_limit)
        self.include_pattern = re.compile(include_pattern) if include_pattern else None
        self.exclude_pattern = re.compile(exclude_pattern) if exclude_pattern else None
        self.allow_subdomains = allow_subdomains
        
        if use_proxies:
            self.proxy_manager = ProxyManager(timeout=proxy_timeout)

        conn = aiohttp.TCPConnector(
            limit=100,
            limit_per_host=10,
            enable_cleanup_closed=True,
            force_close=True,
            ttl_dns_cache=300
        )
            
        if use_browser:
            self.browser = BrowserManager(
                headless=headless,
                wait_time=wait_time,
                auto_scroll=auto_scroll
            )
            if not self.browser.setup_browser():  # Synchronous call
                raise RuntimeError("Failed to setup browser")
            
        if not self.session:
            timeout = aiohttp.ClientTimeout(total=30, connect=10, sock_read=10)
            self.session = aiohttp.ClientSession(
                connector=conn,
                timeout=timeout,
                headers={
                    'User-Agent': 'CrewZombitX64/1.0 (Scholarly Paper Analysis Tool)'
                }
            )
            await self.arxiv_handler.setup()

    async def close(self) -> None:
        """Properly close all resources."""
        try:
            if self.session and not self.session.closed:
                await self.session.close()
            
            if self.browser:
                try:
                    self.browser.close()  # Synchronous call
                except Exception as e:
                    logging.error(f"Error closing browser: {e}")
            
            await self.arxiv_handler.close()
            
            # Save final stats
            if self.stats['pages_crawled'] > 0:
                self.stats['success_rate'] = 1 - (self.stats['errors'] / self.stats['pages_crawled'])
                logging.info(f"Crawling completed. Success rate: {self.stats['success_rate']:.2%}")
                
        except Exception as e:
            logging.error(f"Error during cleanup: {e}")
        
        finally:
            self.session = None
            self.browser = None

    async def get_stats(self) -> Dict:
        """Get current crawling statistics."""
        current_time = time.time()
        return {
            **self.stats,
            'runtime': current_time - (self.stats['start_time'] or current_time),
            'cache_size': len(self.cache),
            'visited_urls': len(self.visited_urls),
            'memory_usage': {
                'cache_size': len(self.cache),
                'visited_urls': len(self.visited_urls),
                'robots_cache': len(self.robots_cache)
            }
        }

    def should_crawl_url(self, url: str, base_domain: str) -> bool:
        """Check if URL should be crawled based on patterns, domain rules and GitHub paths"""
        if not url.startswith(('http://', 'https://')):
            return False
            
        parsed_url = urlparse(url)
        
        # Handle GitHub-specific paths
        if 'github.com' in parsed_url.netloc:
            path = parsed_url.path
            
            # Skip GitHub search and non-repository paths
            if any(segment in path for segment in [
                '/search', '/marketplace', '/sponsors', '/settings',
                '/notifications', '/explore', '/topics'
            ]):
                return False
                
            # Check if path matches any valid GitHub repository pattern
            is_github_path = any(
                re.search(pattern, path)
                for pattern in self.github_base_paths.values()
            )
            
            if not is_github_path:
                return False
        
        if not self.allow_subdomains and parsed_url.netloc != base_domain:
            return False
        elif self.allow_subdomains and base_domain not in parsed_url.netloc:
            return False

        if self.include_pattern and not self.include_pattern.search(url):
            return False

        if self.exclude_pattern and self.exclude_pattern.search(url):
            return False

        return True

    async def crawl(self, url: str, depth: int = 1, cleanup_interval: int = 100, **kwargs) -> Optional[Dict]:
        try:
            # Initialize stats if this is the first crawl
            if not self.stats['start_time']:
                self.stats['start_time'] = time.time()

            current_time = time.time()
            if url in self.visited_urls and current_time - self.visited_urls[url] < 3600:
                return None

            # Check cache with timestamp
            if url in self.cache:
                cache_age = current_time - self.cache_timestamps[url]
                if cache_age < 3600:  # Cache valid for 1 hour
                    return self.cache[url]
                else:
                    # Remove old cache entry
                    del self.cache[url]
                    del self.cache_timestamps[url]

            start_time = time.time()
            base_domain = urlparse(url).netloc

            if not self.should_crawl_url(url, base_domain):
                logging.info(f"Skipping URL (pattern/domain mismatch): {url}")
                return None

            if self.respect_robots:
                allowed = await self.check_robots_txt(url)
                if not allowed:
                    logging.warning(f"URL {url} is not allowed by robots.txt")
                    return None

            # Periodic cleanup
            if self.stats['pages_crawled'] % cleanup_interval == 0:
                self._cleanup_cache()
                self._cleanup_visited_urls()

            self.visited_urls[url] = current_time
            self.stats['pages_crawled'] += 1
            # Enhanced result structure
            result = {
                'url': url,
                'timestamp': time.time(),
                'content': {},
                'links': [],
                'media': {}
            }

            html_content = await self._fetch_content(url)
            if not html_content:
                self.stats['errors'] += 1
                return None

            try:
                extracted_content = await self.data_extractor.extract_all(html_content)
                
                # Include text and HTML content from extract_main_content
                main_content = self.data_extractor.extract_main_content(html_content)
                if main_content:
                  extracted_content['text'] = main_content.get('text', '')
                  extracted_content['html'] = main_content.get('html', '')
                
                result['content'] = extracted_content
                result['media'] = await self._extract_media(html_content, url)
                result['links'] = await self._extract_links(html_content, url)

                # Set titles for article links
                for link in result['links']:
                    if link['url'].endswith('/'):
                        link['url'] = link['url'][:-1]
                    if '/blog/' in link['url']:
                        title = link['url'].split('/')[-1].replace('-', ' ').title()
                        link['text'] = title

                # Filter links based on patterns
                result['links'] = [
                    link for link in result['links'] 
                    if self.should_crawl_url(link['url'], base_domain)
                ]

                # Add load time
                result['load_time'] = time.time() - start_time

            except Exception as e:
                logging.error(f"Error processing {url}: {str(e)}")

            # Update cache with timestamp
            self.cache[url] = result
            self.cache_timestamps[url] = time.time()

            # Update stats
            if 'size' in result:
                self.stats['total_bytes'] += result['size']

            if depth > 1:
                child_tasks = [
                    self.crawl(link['url'], depth - 1, **kwargs)
                    for link in result['links'] if link['url'] not in self.visited_urls
                ]

                if child_tasks:
                    child_results = await asyncio.gather(*child_tasks)
                    for i, child_result in enumerate(child_results):
                        if child_result:
                            result['links'][i]['content'] = child_result

            return result

        except asyncio.CancelledError:
            raise
        except Exception as e:
            logging.error(f"Error crawling {url}: {str(e)}")
            return None

    async def _fetch_content(self, url: str, retries: int = 3) -> Optional[str]:
        """Fetch content with retries and error handling"""
        # Check if URL is from arXiv
        if 'arxiv.org' in url:
            metadata = await self.arxiv_handler.get_paper_metadata(url)
            if metadata:
                # Convert metadata to HTML for consistent processing
                html_content = self._convert_arxiv_metadata_to_html(metadata)
                return html_content
            
        # If not arXiv or metadata fetch failed, proceed with normal fetching
        for attempt in range(retries):
            try:
                if self.browser and self.browser.driver:
                    return await self._fetch_with_browser(url)
                else:
                    return await self._fetch_with_requests(url)
            except aiohttp.ClientError as e:
                if attempt == retries - 1:
                    logging.error(f"Error fetching {url} after {retries} attempts: {str(e)}")
                    return None
                await asyncio.sleep(1 * (attempt + 1))
            except Exception as e:
                logging.error(f"Error fetching {url}: {str(e)}")
                return None

    async def _fetch_with_browser(self, url: str) -> str:
        """Fetch content using Selenium browser with improved error handling"""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                if await self.browser.navigate(url):
                    return self.browser.driver.page_source
                raise Exception("Failed to navigate to URL")
            except Exception as e:
                if attempt == max_retries - 1:
                    raise
                await asyncio.sleep(1 * (attempt + 1))

    async def _fetch_with_requests(self, url: str) -> str:
        """Fetch content using aiohttp with improved error handling"""
        await self.rate_limiter.wait(url)
        
        proxy = None
        if self.proxy_manager:
            proxy = await self.proxy_manager.get_next_proxy()

        try:
            async with self.session.get(url, proxy=proxy, timeout=30) as response:
                response.raise_for_status()
                content = await response.text()
                
                if proxy:
                    await self.proxy_manager.mark_proxy_success(proxy)
                    
                return content
        except Exception as e:
            if proxy:
                await self.proxy_manager.mark_proxy_failed(proxy)
            raise e

    async def _extract_media(self, html: str, base_url: str) -> Dict:
        """Extract media elements from HTML"""
        soup = BeautifulSoup(html, 'html.parser')
        media = {
            'images': [],
            'videos': [],
            'documents': []
        }

        # Extract images
        for img in soup.find_all('img', src=True):
            if any(x in img['src'].lower() for x in ['tracking', 'analytics', 'pixel', 'facebook.com/tr']):
                continue
            media['images'].append({
                'url': urljoin(base_url, img['src']),
                'alt': img.get('alt', ''),
                'title': img.get('title', '')
            })

        # Extract videos
        video_patterns = [
            ('youtube', r'(?:youtube\.com|youtu\.be)'),
            ('vimeo', r'vimeo\.com'),
            ('default', r'\.(?:mp4|webm|ogg)$')
        ]

        for video in soup.find_all(['video', 'iframe', 'source']):
            src = video.get('src', '')
            if not src or any(x in src.lower() for x in ['gtm', 'analytics', 'tracking', 'pixel']):
                continue
                
            video_type = 'default'
            for vtype, pattern in video_patterns:
                if re.search(pattern, src, re.I):
                    video_type = vtype
                    break

            media['videos'].append({
                'url': urljoin(base_url, src),
                'type': video_type,
                'title': video.get('title', '')
            })

        # Extract documents
        doc_extensions = ['.pdf', '.doc', '.docx', '.xls', '.xlsx']
        for link in soup.find_all('a', href=True):
            href = link['href']
            if any(href.lower().endswith(ext) for ext in doc_extensions):
                media['documents'].append({
                    'url': urljoin(base_url, href),
                    'text': link.get_text(strip=True),
                    'type': href.split('.')[-1].lower()
                })

        return media

    def _convert_arxiv_metadata_to_html(self, metadata: Dict) -> str:
        """Convert arXiv metadata to HTML format for consistent processing"""
        html = ['<!DOCTYPE html><html><head><title>{}</title></head><body>'.format(metadata.get('title', ''))]
        
        # Add title
        if metadata.get('title'):
            html.append(f'<h1>{metadata["title"]}</h1>')
            
        # Add authors
        if metadata.get('authors'):
            html.append('<div class="authors">')
            for author in metadata['authors']:
                author_text = author['name']
                if author.get('affiliation'):
                    author_text += f' ({author["affiliation"]})'
                html.append(f'<div class="author">{author_text}</div>')
            html.append('</div>')
            
        # Add categories
        if metadata.get('categories'):
            html.append('<div class="categories">')
            html.append('<h2>Categories</h2>')
            for category in metadata['categories']:
                html.append(f'<span class="category">{category}</span>')
            html.append('</div>')
            
        # Add abstract/summary
        if metadata.get('summary'):
            html.append('<div class="abstract">')
            html.append('<h2>Abstract</h2>')
            html.append(f'<p>{metadata["summary"]}</p>')
            html.append('</div>')
            
        # Add links
        if metadata.get('links'):
            html.append('<div class="links">')
            html.append('<h2>Links</h2>')
            for rel, link_data in metadata['links'].items():
                html.append(f'<a href="{link_data["href"]}" rel="{rel}">{link_data["title"] or rel}</a>')
            html.append('</div>')
            
        # Add additional metadata
        html.append('<div class="metadata">')
        if metadata.get('journal_ref'):
            html.append(f'<p>Journal Reference: {metadata["journal_ref"]}</p>')
        if metadata.get('doi'):
            html.append(f'<p>DOI: {metadata["doi"]}</p>')
        if metadata.get('published'):
            html.append(f'<p>Published: {metadata["published"]}</p>')
        if metadata.get('updated'):
            html.append(f'<p>Updated: {metadata["updated"]}</p>')
        html.append('</div>')
        
        html.append('</body></html>')
        return '\n'.join(html)

    async def _extract_links(self, html: str, base_url: str) -> List[Dict]:
        """Extract links from HTML with special handling for GitHub pages and arXiv links"""
        soup = BeautifulSoup(html, 'html.parser')
        links = []
        base_domain = urlparse(base_url).netloc
        is_github = 'github.com' in base_domain
        is_arxiv = 'arxiv.org' in base_domain

        for a in soup.find_all('a', href=True):
            href = a['href']
            if not href or href.startswith(('#', 'javascript:', 'mailto:', 'tel:')):
                continue

            abs_url = urljoin(base_url, href)
            if not abs_url.startswith(('http://', 'https://')):
                continue

            domain = urlparse(abs_url).netloc
            link_type = 'internal' if domain == base_domain else 'external'

            # Handle arXiv-specific links
            if 'arxiv.org' in domain:
                link_type = 'arxiv'

            # Special handling for GitHub links
            if is_github:
                path = urlparse(abs_url).path
                
                # Determine GitHub-specific link type
                for path_type, pattern in self.github_base_paths.items():
                    if re.search(pattern, path):
                        link_type = f'github_{path_type}'
                        break

                # Skip certain GitHub links
                if any(segment in path for segment in [
                    '/search', '/marketplace', '/sponsors', '/settings',
                    '/notifications', '/explore', '/topics'
                ]):
                    continue

            links.append({
                'url': abs_url,
                'text': a.get_text(strip=True),
                'type': link_type,
                'title': a.get('title', '')
            })

        return links

    async def check_robots_txt(self, url: str) -> bool:
        """Check if URL is allowed by robots.txt with caching and proper parsing."""
        if not self.respect_robots:
            return True

        parsed = urlparse(url)
        domain = parsed.netloc
        robots_url = f"{parsed.scheme}://{domain}/robots.txt"
        
        current_time = time.time()
        
        # Check cache
        if domain in self.robots_cache:
            cache_entry = self.robots_cache[domain]
            if current_time - cache_entry['timestamp'] < self.robots_cache_ttl:
                return self._check_cached_rules(cache_entry['rules'], 'CrewZombitX64', parsed.path)
            else:
                # Cache expired, remove it
                del self.robots_cache[domain]
        
        try:
            async with self.session.get(robots_url, timeout=10) as response:
                if response.status != 200:
                    # Cache the "allow all" result
                    self.robots_cache[domain] = {
                        'timestamp': current_time,
                        'rules': {'*': {'allow': ['*'], 'disallow': []}}
                    }
                    return True
                
                robots_content = await response.text()
                rules = self._parse_robots_txt(robots_content)
                
                # Cache the parsed rules
                self.robots_cache[domain] = {
                    'timestamp': current_time,
                    'rules': rules
                }
                
                return self._check_cached_rules(rules, 'CrewZombitX64', parsed.path)
                
        except Exception as e:
            logging.warning(f"Error fetching robots.txt for {domain}: {str(e)}")
            # Cache the error state (allow all) for a shorter time
            self.robots_cache[domain] = {
                'timestamp': current_time,
                'rules': {'*': {'allow': ['*'], 'disallow': []}},
                'error': str(e)
            }
            return True

    def _check_cached_rules(self, rules: Dict, user_agent: str, path: str) -> bool:
        """Check if path is allowed using cached robots.txt rules."""
        # First try to match the specific user agent
        if user_agent in rules:
            agent_rules = rules[user_agent]
        # Then try the wildcard rules
        elif '*' in rules:
            agent_rules = rules['*']
        else:
            return True  # No applicable rules found
        
        # Check if path matches any allow rule first
        for allow_pattern in agent_rules.get('allow', []):
            if self._matches_pattern(path, allow_pattern):
                return True
                
        # Then check if it matches any disallow rule
        for disallow_pattern in agent_rules.get('disallow', []):
            if self._matches_pattern(path, disallow_pattern):
                return False
                
        return True  # Allowed by default

    def _matches_pattern(self, path: str, pattern: str) -> bool:
        """Check if a path matches a robots.txt pattern."""
        if pattern == '*':
            return True
            
        # Convert robots.txt pattern to regex
        pattern = pattern.replace('.', r'\.')
        pattern = pattern.replace('*', '.*')
        pattern = pattern.replace('$', r'\$')
        pattern = f'^{pattern}'
        
        try:
            return bool(re.match(pattern, path))
        except re.error:
            return False

    def _parse_robots_txt(self, content: str) -> Dict:
        """Parse robots.txt content into structured rules."""
        rules = {}
        current_agent = '*'
        
        for line in content.split('\n'):
            # Remove comments and whitespace
            line = line.split('#')[0].strip().lower()
            if not line:
                continue
                
            # Split into fields
            if ':' in line:
                field, value = line.split(':', 1)
                field = field.strip()
                value = value.strip()
                
                if field == 'user-agent':
                    current_agent = value
                    if current_agent not in rules:
                        rules[current_agent] = {'allow': [], 'disallow': []}
                elif field == 'allow' and value:
                    rules[current_agent]['allow'].append(value)
                elif field == 'disallow' and value:
                    rules[current_agent]['disallow'].append(value)
                elif field == 'crawl-delay':
                    try:
                        rules[current_agent]['crawl-delay'] = float(value)
                    except ValueError:
                        pass
                        
        return rules
