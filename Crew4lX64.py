import os
import re
import json
import time
import logging
import asyncio
import aiohttp
import requests
import ssl
import concurrent.futures
from functools import lru_cache
from typing import Dict, List, Optional, Union
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from urllib.parse import urljoin, urlparse
from rank_bm25 import BM25Okapi
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
from nltk.tokenize import sent_tokenize, word_tokenize
from jsonpath_ng import parse as jsonpath_parse
from lxml import etree, html
import nltk

# For LLM integration
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    from ollama import Client as OllamaClient
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False

try:
    nltk.data.find('tokenizers/punkt')
    nltk.data.find('tokenizers/averaged_perceptron_tagger')
except LookupError:
    nltk.download('punkt')
    nltk.download('averaged_perceptron_tagger')

class SchemaGenerator:
    """Generates extraction schemas using LLM models."""
    
    def __init__(self, use_ollama=True, model="mistral"):
        self.use_ollama = use_ollama and OLLAMA_AVAILABLE
        self.model = model
        if self.use_ollama:
            self.client = OllamaClient()
        elif OPENAI_AVAILABLE:
            self.openai_client = openai.OpenAI()
        else:
            logging.warning("No LLM clients available. Schema generation will be limited.")

    @lru_cache(maxsize=100)
    async def generate_schema(self, html_sample: str, data_type: str) -> Dict:
        """Generate extraction schema using LLM."""
        prompt = self._create_schema_prompt(html_sample, data_type)
        
        try:
            if self.use_ollama:
                response = await self._get_ollama_response(prompt)
            elif OPENAI_AVAILABLE:
                response = await self._get_openai_response(prompt)
            else:
                return self._generate_basic_schema(html_sample)
            
            return self._parse_schema_response(response)
        except Exception as e:
            logging.error(f"Schema generation failed: {str(e)}")
            return self._generate_basic_schema(html_sample)

    def _create_schema_prompt(self, html_sample: str, data_type: str) -> str:
        """Create optimized prompt for schema generation."""
        return f"""Analyze this HTML and create an extraction schema for {data_type}.
Consider these aspects:
1. CSS selectors for direct element access
2. XPath expressions for complex patterns
3. JSONPath for structured data
4. Microdata/metadata patterns

HTML Sample:
{html_sample}

Return a JSON schema with:
{{
    "selectors": {{"field_name": "css_selector"}},
    "xpath": {{"field_name": "xpath_expression"}},
    "jsonpath": {{"field_name": "jsonpath_expression"}},
    "metadata": {{"field_name": "metadata_pattern"}}
}}"""

    async def _get_ollama_response(self, prompt: str) -> str:
        """Get response from Ollama model."""
        response = await asyncio.to_thread(
            self.client.generate,
            model=self.model,
            prompt=prompt
        )
        return response['response']

    async def _get_openai_response(self, prompt: str) -> str:
        """Get response from OpenAI model."""
        response = await self.openai_client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content

    def _parse_schema_response(self, response: str) -> Dict:
        """Parse and validate LLM response into usable schema."""
        try:
            # Extract JSON from response (handle cases where LLM adds explanatory text)
            json_match = re.search(r'\{[\s\S]*\}', response)
            if json_match:
                schema = json.loads(json_match.group(0))
                return self._validate_schema(schema)
        except json.JSONDecodeError as e:
            logging.error(f"Invalid schema format: {str(e)}")
        return {}

    def _validate_schema(self, schema: Dict) -> Dict:
        """Validate and clean up the generated schema."""
        valid_schema = {}
        required_sections = ['selectors', 'xpath', 'jsonpath', 'metadata']
        
        for section in required_sections:
            if section in schema and isinstance(schema[section], dict):
                valid_schema[section] = {
                    k: v for k, v in schema[section].items()
                    if isinstance(k, str) and isinstance(v, str)
                }
        
        return valid_schema

    def _generate_basic_schema(self, html_sample: str) -> Dict:
        """Generate basic schema without LLM."""
        soup = BeautifulSoup(html_sample, 'html.parser')
        schema = {
            'selectors': {},
            'xpath': {},
            'jsonpath': {},
            'metadata': {}
        }

        # Basic metadata extraction
        for meta in soup.find_all('meta', attrs={'name': True, 'content': True}):
            name = meta['name']
            schema['selectors'][f"meta_{name}"] = f"meta[name='{name}']"

        # Find main content areas
        for tag in ['main', 'article', 'div[class*="content"]']:
            if soup.select(tag):
                schema['selectors']['main_content'] = tag
                break

        return schema

class DataExtractor:
    """Handles structured data extraction using various strategies."""
    
    def __init__(self):
        self.vectorizer = TfidfVectorizer()
        self.schema_generator = SchemaGenerator()
        self._setup_ssl_context()

    def _setup_ssl_context(self):
        """Setup SSL context with custom validation."""
        self.ssl_context = ssl.create_default_context()
        self.ssl_context.check_hostname = True
        self.ssl_context.verify_mode = ssl.CERT_REQUIRED
        
        # Custom certificate path support
        cert_path = os.getenv('CUSTOM_CERT_PATH')
        if cert_path and os.path.exists(cert_path):
            self.ssl_context.load_verify_locations(cert_path)

    @lru_cache(maxsize=1000)
    def chunk_by_topic(self, text: str, chunk_size: int = 1000) -> List[str]:
        """Split text into topic-based chunks with caching."""
        sentences = sent_tokenize(text)
        chunks = []
        current_chunk = []
        current_size = 0

        for sentence in sentences:
            sentence_size = len(sentence)
            if current_size + sentence_size > chunk_size and current_chunk:
                chunks.append(' '.join(current_chunk))
                current_chunk = []
                current_size = 0
            current_chunk.append(sentence)
            current_size += sentence_size

        if current_chunk:
            chunks.append(' '.join(current_chunk))

        return chunks

    async def extract_all(self, html: str, data_type: str = None) -> Dict:
        """Comprehensive data extraction using all available methods."""
        schema = await self.schema_generator.generate_schema(html, data_type) if data_type else {}
        
        # Run extractions in parallel
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = [
                executor.submit(self._extract_structured_data, html, schema),
                executor.submit(self._extract_json_ld, html),
                executor.submit(self._extract_microdata, html)
            ]
            
            results = {}
            for future in concurrent.futures.as_completed(futures):
                results.update(future.result())
        
        return results

    def _extract_structured_data(self, html: str, schema: Dict) -> Dict:
        """Extract data using schema-based approach."""
        result = {}
        soup = BeautifulSoup(html, 'html.parser')
        tree = html.fromstring(html.encode())

        # CSS Selectors
        if 'selectors' in schema:
            for key, selector in schema['selectors'].items():
                elements = soup.select(selector)
                result[key] = [e.get_text(strip=True) for e in elements]
                if len(result[key]) == 1:
                    result[key] = result[key][0]

        # XPath
        if 'xpath' in schema:
            for key, xpath in schema['xpath'].items():
                elements = tree.xpath(xpath)
                result[key] = [e.text_content().strip() for e in elements if e.text_content()]
                if len(result[key]) == 1:
                    result[key] = result[key][0]

        return {'structured': result}

    def _extract_json_ld(self, html: str) -> Dict:
        """Extract JSON-LD data."""
        soup = BeautifulSoup(html, 'html.parser')
        json_ld_data = []

        for script in soup.find_all('script', type='application/ld+json'):
            try:
                data = json.loads(script.string)
                json_ld_data.append(data)
            except json.JSONDecodeError:
                continue

        return {'json_ld': json_ld_data}

    def _extract_microdata(self, html: str) -> Dict:
        """Extract Microdata."""
        soup = BeautifulSoup(html, 'html.parser')
        microdata = {}

        for element in soup.find_all(attrs={"itemscope": True}):
            item_type = element.get("itemtype", "")
            if not item_type:
                continue

            properties = {}
            for prop in element.find_all(attrs={"itemprop": True}):
                prop_name = prop["itemprop"]
                
                # Handle different property types
                if prop.name in ['meta', 'link']:
                    prop_value = prop.get('content') or prop.get('href')
                elif prop.name in ['img', 'audio', 'video']:
                    prop_value = prop.get('src')
                elif prop.name == 'time':
                    prop_value = prop.get('datetime')
                else:
                    prop_value = prop.get_text(strip=True)

                if prop_value:
                    if prop_name in properties:
                        if isinstance(properties[prop_name], list):
                            properties[prop_name].append(prop_value)
                        else:
                            properties[prop_name] = [properties[prop_name], prop_value]
                    else:
                        properties[prop_name] = prop_value

            if properties:
                if item_type in microdata:
                    if isinstance(microdata[item_type], list):
                        microdata[item_type].append(properties)
                    else:
                        microdata[item_type] = [microdata[item_type], properties]
                else:
                    microdata[item_type] = properties

        return {'microdata': microdata}

class BrowserManager:
    """Manages browser interactions and sessions."""
    
    def __init__(self, headless=True):
        self.options = Options()
        if headless:
            self.options.add_argument('--headless')
        self.options.add_argument('--no-sandbox')
        self.options.add_argument('--disable-dev-shm-usage')
        self.driver = None
        self._setup_options()

    def _setup_options(self):
        """Setup additional browser options for better performance and security."""
        # Performance optimizations
        self.options.add_argument('--disable-gpu')
        self.options.add_argument('--disable-software-rasterizer')
        self.options.add_argument('--disable-dev-shm-usage')
        
        # Security options
        self.options.add_argument('--disable-web-security')
        self.options.add_argument('--allow-running-insecure-content')
        
        # Add custom SSL certificates if specified
        cert_path = os.getenv('CUSTOM_CERT_PATH')
        if cert_path:
            self.options.add_argument(f'--ignore-certificate-errors-spki-list={cert_path}')

    def setup_browser(self, proxy=None, user_agent=None):
        """Configure browser with enhanced options."""
        if proxy:
            if isinstance(proxy, dict):
                # Handle authenticated proxies
                auth_proxy = f"{proxy['username']}:{proxy['password']}@{proxy['host']}:{proxy['port']}"
                self.options.add_argument(f'--proxy-server={auth_proxy}')
            else:
                self.options.add_argument(f'--proxy-server={proxy}')

        if user_agent:
            self.options.add_argument(f'--user-agent={user_agent}')

        self.driver = webdriver.Chrome(options=self.options)
        return self.driver

    def adjust_viewport(self):
        """Dynamically adjust viewport based on content."""
        if self.driver:
            total_height = self.driver.execute_script("""
                return Math.max(
                    document.body.scrollHeight,
                    document.documentElement.scrollHeight,
                    document.body.offsetHeight,
                    document.documentElement.offsetHeight,
                    document.body.clientHeight,
                    document.documentElement.clientHeight
                );
            """)
            
            width = self.driver.execute_script("""
                return Math.max(
                    document.body.scrollWidth,
                    document.documentElement.scrollWidth,
                    document.body.offsetWidth,
                    document.documentElement.offsetWidth,
                    document.body.clientWidth,
                    document.documentElement.clientWidth
                );
            """)
            
            self.driver.set_window_size(width, total_height)

    async def wait_for_element(self, selector: str, timeout: int = 10) -> Optional[webdriver.remote.webelement.WebElement]:
        """Asynchronously wait for element with timeout."""
        if not self.driver:
            return None

        try:
            return await asyncio.to_thread(
                WebDriverWait(self.driver, timeout).until,
                EC.presence_of_element_located((By.CSS_SELECTOR, selector))
            )
        except TimeoutException:
            logging.warning(f"Element not found: {selector}")
            return None
        except Exception as e:
            logging.error(f"Error waiting for element: {str(e)}")
            return None

class WebCrawler:
    """Advanced web crawling and content extraction."""
    
    def __init__(self):
        self.browser = None
        self.data_extractor = DataExtractor()
        self.visited_urls = set()
        self.cache = {}
        self.session = None
        self._setup_logging()

    def _setup_logging(self):
        """Configure logging with proper formatting."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

    async def setup(self, use_browser=False, **kwargs):
        """Asynchronous setup of crawler components."""
        if use_browser:
            self.browser = BrowserManager(**kwargs)
        
        # Setup aiohttp session for async requests
        if not self.session:
            self.session = aiohttp.ClientSession()

    async def close(self):
        """Cleanup resources."""
        if self.session:
            await self.session.close()
        if self.browser and self.browser.driver:
            self.browser.driver.quit()

    async def crawl(self, url: str, depth: int = 1, **kwargs) -> Optional[Dict]:
        """Enhanced asynchronous crawling with parallel processing."""
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

            # Process different aspects in parallel
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

            # Cache result
            self.cache[url] = result

            # Recursively crawl linked pages
            if depth > 1:
                child_tasks = []
                for link in result['links']:
                    if link['url'] not in self.visited_urls:
                        child_tasks.append(
                            self.crawl(link['url'], depth - 1, **kwargs)
                        )
                
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
        """Fetch page content with proper error handling."""
        try:
            if self.browser and self.browser.driver:
                return await self._fetch_with_browser(url)
            else:
                return await self._fetch_with_requests(url)
        except Exception as e:
            logging.error(f"Error fetching {url}: {str(e)}")
            return None

    async def _fetch_with_browser(self, url: str) -> str:
        """Fetch content using Selenium with enhanced features."""
        await asyncio.to_thread(self.browser.driver.get, url)
        await asyncio.to_thread(self.browser.adjust_viewport)
        
        # Wait for dynamic content
        await self.browser.wait_for_element('body')
        await self._handle_lazy_loading()
        
        return self.browser.driver.page_source

    async def _fetch_with_requests(self, url: str) -> str:
        """Fetch content using aiohttp."""
        async with self.session.get(url) as response:
            response.raise_for_status()
            return await response.text()

    async def _handle_lazy_loading(self, max_scrolls: int = 10):
        """Handle lazy loading content."""
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
            await asyncio.sleep(1)  # Wait for content to load

            new_height = await asyncio.to_thread(
                self.browser.driver.execute_script,
                "return document.body.scrollHeight"
            )
            if new_height == last_height:
                break
            last_height = new_height

    async def _extract_media(self, html: str, base_url: str) -> Dict:
        """Extract media elements with enhanced features."""
        soup = BeautifulSoup(html, 'html.parser')
        media = {
            'images': [],
            'videos': [],
            'audio': [],
            'documents': []
        }

        # Process in parallel
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
        """Extract image content with responsive handling."""
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

                # Handle srcset
                srcset = img.get('srcset', '')
                if srcset:
                    image_data['srcset'] = [
                        {'url': urljoin(base_url, s.strip().split()[0]),
                         'size': s.strip().split()[1] if len(s.strip().split()) > 1 else None}
                        for s in srcset.split(',')
                        if s.strip()
                    ]

                # Handle picture element
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
        """Extract video content with enhanced metadata."""
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
            else:  # iframe
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
        """Extract audio content with metadata."""
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
        """Extract document links."""
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
        """Extract and analyze links."""
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
                
                # Check if link points to a document
                if any(absolute_url.lower().endswith(ext) 
                      for ext in ['.pdf', '.doc', '.docx', '.xls', '.xlsx']):
                    link_data['is_document'] = True
                    link_data['document_type'] = absolute_url.split('.')[-1].lower()
                
                links.append(link_data)

        # Extract iframe sources
        for iframe in soup.find_all('iframe', src=True):
            src = iframe.get('src')
            if src:
                links.append({
                    'url': urljoin(base_url, src),
                    'type': 'iframe',
                    'title': iframe.get('title', '')
                })

        return links

async def main():
    """Asynchronous main execution function."""
    crawler = WebCrawler()
    await crawler.setup(use_browser=True, headless=True)

    try:
        url = input("Enter URL to crawl: ")
        result = await crawler.crawl(url, depth=2)

        if result:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            os.makedirs("scraped_output", exist_ok=True)

            # Save full data as JSON
            json_file = f"scraped_output/data_{timestamp}.json"
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)

            print(f"\n✅ Content saved to:")
            print(f"  📊 Full data: {json_file}")
        else:
            print("❌ Failed to crawl URL")

    finally:
        await crawler.close()

if __name__ == "__main__":
    asyncio.run(main())
