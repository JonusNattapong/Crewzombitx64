import aiohttp
import logging
import asyncio
import concurrent.futures
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
        self._setup_logging()

    def _setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

    async def setup(self, use_browser=False, **kwargs):
        if use_browser:
            self.browser = BrowserManager(**kwargs)
        if not self.session:
            self.session = aiohttp.ClientSession()

    async def close(self):
        if self.session:
            await self.session.close()
        if self.browser and self.browser.driver:
            self.browser.driver.quit()

    async def crawl(self, url: str, depth: int = 1, **kwargs) -> Optional[Dict]:
        if url in self.visited_urls or depth <= 0:
            return None

        if url in self.cache:
            return self.cache[url]

        self.visited_urls.add(url)
        result = {
            'url': url,
            'timestamp': time.time(),
            'content': {},
            'links': [],
            'media': {}
        }

        try:
            html_content = await self._fetch_content(url)
            if not html_content:
                return None

            async with asyncio.TaskGroup() as group:
                structured_task = group.create_task(
                    self.data_extractor.extract_all(html_content)
                )
                media_task = group.create_task(
                    self._extract_media(html_content, url)
                )
                links_task = group.create_task(
                    self._extract_links(html_content, url)
                )

            result['content'] = structured_task.result()
            result['media'] = media_task.result()
            result['links'] = links_task.result()

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

        except Exception as e:
            logging.error(f"Error crawling {url}: {str(e)}")
            return None

        return result

    async def _fetch_content(self, url: str) -> Optional[str]:
        try:
            if self.browser and self.browser.driver:
                return await self._fetch_with_browser(url)
            else:
                return await self._fetch_with_requests(url)
        except Exception as e:
            logging.error(f"Error fetching {url}: {str(e)}")
            return None

    async def _fetch_with_browser(self, url: str) -> str:
        await asyncio.to_thread(self.browser.driver.get, url)
        await asyncio.to_thread(self.browser.adjust_viewport)
        await self.browser.wait_for_element('body')
        await self._handle_lazy_loading()
        return self.browser.driver.page_source

    async def _fetch_with_requests(self, url: str) -> str:
        async with self.session.get(url) as response:
            response.raise_for_status()
            return await response.text()

    async def _handle_lazy_loading(self, max_scrolls: int = 10):
        if not self.browser or not self.browser.driver:
            return

        last_height = await asyncio.to_thread(
            self.browser.driver.execute_script,
            "return document.body.scrollHeight"
        )

        for _ in range(max_scrolls):
            await asyncio.to_thread(
                self.browser.driver.execute_script,
                "window.scrollTo(0, document.body.scrollHeight);"
            )
            await asyncio.sleep(1)

            new_height = await asyncio.to_thread(
                self.browser.driver.execute_script,
                "return document.body.scrollHeight"
            )
            if new_height == last_height:
                break
            last_height = new_height

    async def _extract_media(self, html: str, base_url: str) -> Dict:
        soup = BeautifulSoup(html, 'html.parser')
        media = {
            'images': [],
            'videos': [],
            'audio': [],
            'documents': []
        }

        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = [
                executor.submit(self._extract_images, soup, base_url),
                executor.submit(self._extract_videos, soup, base_url),
                executor.submit(self._extract_audio, soup, base_url),
                executor.submit(self._extract_documents, soup, base_url)
            ]

            for future in concurrent.futures.as_completed(futures):
                media.update(future.result())

        return media

    def _extract_images(self, soup: BeautifulSoup, base_url: str) -> Dict:
        images = []
        for img in soup.find_all('img'):
            src = img.get('src')
            if src:
                image_data = {
                    'url': urljoin(base_url, src),
                    'alt': img.get('alt', ''),
                    'title': img.get('title', ''),
                    'loading': img.get('loading', 'eager'),
                    'srcset': []
                }

                srcset = img.get('srcset', '')
                if srcset:
                    image_data['srcset'] = [
                        {'url': urljoin(base_url, s.strip().split()[0]),
                         'size': s.strip().split()[1] if len(s.strip().split()) > 1 else None}
                        for s in srcset.split(',')
                        if s.strip()
                    ]

                picture = img.find_parent('picture')
                if picture:
                    image_data['sources'] = []
                    for source in picture.find_all('source'):
                        source_data = {
                            'media': source.get('media', ''),
                            'type': source.get('type', ''),
                            'srcset': []
                        }
                        if source.get('srcset'):
                            source_data['srcset'] = [
                                {'url': urljoin(base_url, s.strip().split()[0]),
                                 'size': s.strip().split()[1] if len(s.strip().split()) > 1 else None}
                                for s in source['srcset'].split(',')
                                if s.strip()
                            ]
                        image_data['sources'].append(source_data)

                images.append(image_data)

        return {'images': images}

    def _extract_videos(self, soup: BeautifulSoup, base_url: str) -> Dict:
        videos = []
        for video in soup.find_all(['video', 'iframe[src*="youtube"], iframe[src*="vimeo"]']):
            if video.name == 'video':
                video_data = {
                    'type': 'html5',
                    'controls': video.get('controls', False),
                    'autoplay': video.get('autoplay', False),
                    'loop': video.get('loop', False),
                    'muted': video.get('muted', False),
                    'poster': urljoin(base_url, video.get('poster', '')),
                    'sources': []
                }

                for source in video.find_all('source'):
                    video_data['sources'].append({
                        'url': urljoin(base_url, source.get('src', '')),
                        'type': source.get('type', '')
                    })

                videos.append(video_data)
            else:
                src = video.get('src', '')
                if 'youtube' in src or 'vimeo' in src:
                    videos.append({
                        'type': 'youtube' if 'youtube' in src else 'vimeo',
                        'url': src,
                        'width': video.get('width', ''),
                        'height': video.get('height', ''),
                        'title': video.get('title', '')
                    })

        return {'videos': videos}

    def _extract_audio(self, soup: BeautifulSoup, base_url: str) -> Dict:
        audio_files = []
        for audio in soup.find_all('audio'):
            audio_data = {
                'controls': audio.get('controls', False),
                'autoplay': audio.get('autoplay', False),
                'loop': audio.get('loop', False),
                'muted': audio.get('muted', False),
                'sources': []
            }

            for source in audio.find_all('source'):
                audio_data['sources'].append({
                    'url': urljoin(base_url, source.get('src', '')),
                    'type': source.get('type', '')
                })

            audio_files.append(audio_data)

        return {'audio': audio_files}

    def _extract_documents(self, soup: BeautifulSoup, base_url: str) -> Dict:
        documents = []
        doc_extensions = ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx']

        for link in soup.find_all('a', href=True):
            href = link.get('href', '')
            if any(href.lower().endswith(ext) for ext in doc_extensions):
                documents.append({
                    'url': urljoin(base_url, href),
                    'text': link.get_text(strip=True),
                    'type': href.split('.')[-1].lower()
                })

        return {'documents': documents}

    async def _extract_links(self, html: str, base_url: str) -> List[Dict]:
        soup = BeautifulSoup(html, 'html.parser')
        links = []

        for a in soup.find_all('a', href=True):
            href = a.get('href')
            if href:
                absolute_url = urljoin(base_url, href)
                link_type = 'internal' if urlparse(base_url).netloc in absolute_url else 'external'

                link_data = {
                    'url': absolute_url,
                    'text': a.get_text(strip=True),
                    'type': link_type,
                    'title': a.get('title', ''),
                    'rel': a.get('rel', []),
                    'target': a.get('target', '_self')
                }

                if any(absolute_url.lower().endswith(ext)
                      for ext in ['.pdf', '.doc', '.docx', '.xls', '.xlsx']):
                    link_data['is_document'] = True
                    link_data['document_type'] = absolute_url.split('.')[-1].lower()

                links.append(link_data)

        for iframe in soup.find_all('iframe', src=True):
            src = iframe.get('src')
            if src:
                links.append({
                    'url': urljoin(base_url, src),
                    'type': 'iframe',
                    'title': iframe.get('title', '')
                })

        return links

    async def crawl_with_pagination(self, url, depth=1, page_param="page", max_pages=10):
        """Crawl with pagination support."""
        results = []
        base_url = url
        
        for page in range(1, max_pages + 1):
            paginated_url = f"{base_url}{'&' if '?' in base_url else '?'}{page_param}={page}"
            logging.info(f"Crawling page {page}: {paginated_url}")
            
            result = await self.crawl(paginated_url, depth)
            if result:
                results.append(result)
                
                if self._is_last_page(result):
                    logging.info(f"Reached last page at {page}")
                    break
            else:
                break
                
        return results

    def _is_last_page(self, page_result):
        """Detect if this is the last page based on content analysis."""
        content_length = len(str(page_result.get('content', {})))
        links_count = len(page_result.get('links', []))
        
        if content_length < 1000 or links_count < 5:
            return True
            
        has_next = any('next' in link.get('text', '').lower() for link in page_result.get('links', []))
        return not has_next

    async def _fetch_with_retry(self, url, max_retries=3, backoff_factor=1.5):
        """Fetch URL content with retry mechanism."""
        retries = 0
        last_exception = None
        
        while retries < max_retries:
            try:
                await self.rate_limiter.wait()
                
                if self.browser and self.browser.driver:
                    return await self._fetch_with_browser(url)
                else:
                    async with self.session.get(url, timeout=30) as response:
                        if response.status == 200:
                            return await response.text()
                        
                        if response.status in (429, 503):
                            retry_after = int(response.headers.get('Retry-After', backoff_factor * (2 ** retries)))
                            logging.info(f"Rate limited. Waiting {retry_after} seconds before retry.")
                            await asyncio.sleep(retry_after)
                        else:
                            logging.warning(f"HTTP error {response.status} for {url}")
                            break
                            
            except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                last_exception = e
                logging.warning(f"Request failed (attempt {retries+1}/{max_retries}): {str(e)}")
            
            retries += 1
            await asyncio.sleep(backoff_factor * (2 ** retries))
        
        if last_exception:
            logging.error(f"Failed to fetch {url} after {max_retries} attempts: {str(last_exception)}")
        
        return None

    async def check_robots_txt(self, url):
        """Check if URL is allowed by robots.txt."""
        parsed_url = urlparse(url)
        robots_url = f"{parsed_url.scheme}://{parsed_url.netloc}/robots.txt"
        
        try:
            async with self.session.get(robots_url) as response:
                if response.status == 200:
                    robots_txt = await response.text()
                    return self._can_fetch(robots_txt, parsed_url.path)
        except Exception as e:
            logging.warning(f"Error fetching robots.txt: {e}")
        
        return True

    def _can_fetch(self, robots_txt, path):
        """Parse robots.txt and check if path is allowed."""
        user_agent_sections = robots_txt.split("User-agent:")
        
        for section in user_agent_sections:
            if not section.strip():
                continue
            
            lines = section.strip().split('\n')
            agent = lines[0].strip()
            
            if agent == '*' or agent == 'python-requests':
                for line in lines[1:]:
                    if line.lower().startswith('disallow:'):
                        disallow_path = line.split(':', 1)[1].strip()
                        if disallow_path and path.startswith(disallow_path):
                            return False
        
        return True
