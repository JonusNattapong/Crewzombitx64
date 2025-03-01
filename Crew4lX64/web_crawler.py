import aiohttp
import logging
import asyncio
import re
import time
from typing import Optional, Dict, List
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from browser_manager import BrowserManager
from content_extractor import ContentExtractor
from rate_limiter import RateLimiter
from proxy_manager import ProxyManager

class WebCrawler:
    def __init__(self):
        self.browser = None
        self.data_extractor = ContentExtractor()
        self.visited_urls = set()
        self.cache = {}
        self.session = None
        self.rate_limiter = RateLimiter()
        self.proxy_manager = None
        self.respect_robots = True
        self.include_pattern = None
        self.exclude_pattern = None
        self.allow_subdomains = False
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

    def _setup_logging(self):
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
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                }
            )

    async def close(self):
        if self.session:
            await self.session.close()
        if self.browser:
            self.browser.close()  # Synchronous call

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

    async def crawl(self, url: str, depth: int = 1, **kwargs) -> Optional[Dict]:
        try:
            if url in self.visited_urls or depth <= 0:
                return None

            if url in self.cache:
                return self.cache[url]

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

            self.visited_urls.add(url)
            result = {
                'url': url,
                'timestamp': time.time(),
                'content': {},
                'links': [],
                'media': {}
            }

            html_content = await self._fetch_content(url)
            if not html_content:
                return None

            try:
                result['content'] = await self.data_extractor.extract_all(html_content)
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

            self.cache[url] = result

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

    async def _extract_links(self, html: str, base_url: str) -> List[Dict]:
        """Extract links from HTML with special handling for GitHub pages"""
        soup = BeautifulSoup(html, 'html.parser')
        links = []
        base_domain = urlparse(base_url).netloc
        is_github = 'github.com' in base_domain

        for a in soup.find_all('a', href=True):
            href = a['href']
            if not href or href.startswith(('#', 'javascript:', 'mailto:', 'tel:')):
                continue

            abs_url = urljoin(base_url, href)
            if not abs_url.startswith(('http://', 'https://')):
                continue

            domain = urlparse(abs_url).netloc
            link_type = 'internal' if domain == base_domain else 'external'

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
        """Check if URL is allowed by robots.txt"""
        if not self.respect_robots:
            return True

        parsed = urlparse(url)
        robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
        
        try:
            async with self.session.get(robots_url) as response:
                if response.status != 200:
                    return True
                    
                robots_content = await response.text()
                return self._check_robots_rules(robots_content, parsed.path)
        except Exception as e:
            logging.warning(f"Error fetching robots.txt: {e}")
            return True

    def _check_robots_rules(self, robots_content: str, path: str) -> bool:
        """Parse robots.txt content and check if path is allowed"""
        for line in robots_content.split('\n'):
            if line.lower().startswith('disallow:'):
                pattern = line.split(':', 1)[1].strip()
                if pattern and path.startswith(pattern):
                    return False
        return True
