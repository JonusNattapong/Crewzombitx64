# import os
# import re
# import json
# import time
# import logging
# import asyncio
# import aiohttp
# import requests
# import ssl
# import concurrent.futures
# import argparse
# from functools import lru_cache
# from typing import Dict, List, Optional, Union
# from bs4 import BeautifulSoup
# from selenium import webdriver
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.common.exceptions import TimeoutException
# from urllib.parse import urljoin, urlparse
# from rank_bm25 import BM25Okapi
# from sklearn.metrics.pairwise import cosine_similarity
# from sklearn.feature_extraction.text import TfidfVectorizer
# from nltk.tokenize import sent_tokenize, word_tokenize
# from jsonpath_ng import parse as jsonpath_parse
# from lxml import etree, html
# import nltk
# import csv
# # For LLM integration
# try:
#     import openai
#     OPENAI_AVAILABLE = True
# except ImportError:
#     OPENAI_AVAILABLE = False

# try:
#     from ollama import Client as OllamaClient
#     OLLAMA_AVAILABLE = True
# except ImportError:
#     OLLAMA_AVAILABLE = False

# try:
#     nltk.data.find('tokenizers/punkt')
#     nltk.data.find('tokenizers/averaged_perceptron_tagger')
# except LookupError:
#     nltk.download('punkt')
#     nltk.download('averaged_perceptron_tagger')

# async def main():
#     """Asynchronous main execution function with enhanced capabilities."""
#     parser = argparse.ArgumentParser(description='Advanced Web Crawler')
#     parser.add_argument('--url', help='URL to crawl', required=False)
#     parser.add_argument('--depth', type=int, default=2, help='Crawl depth')
#     parser.add_argument('--browser', action='store_true', help='Use browser for rendering')
#     parser.add_argument('--output-format', choices=['json', 'csv', 'both'], default='json', help='Output format')
#     parser.add_argument('--rate-limit', type=float, default=1.0, help='Requests per second')
#     parser.add_argument('--proxies', help='File with proxy list (one per line)')
#     parser.add_argument('--user-agents', help='File with user agents (one per line)')
#     parser.add_argument('--respect-robots', action='store_true', help='Respect robots.txt')
#     parser.add_argument('--max-pages', type=int, default=10, help='Maximum pages to crawl with pagination')
#     args = parser.parse_args()
    
#     # Initialize components
#     crawler = WebCrawler()
#     rate_limiter = RateLimiter(requests_per_second=args.rate_limit)
#     content_extractor = ContentExtractor()
#     data_exporter = DataExporter()
    
#     # Setup proxy rotation if specified
#     proxy_manager = None
#     if args.proxies:
#         proxy_manager = ProxyManager()
#         await proxy_manager.load_from_file(args.proxies)
    
#     # Setup user agent rotation if specified
#     user_agents = []
#     if args.user_agents:
#         try:
#             with open(args.user_agents, 'r') as f:
#                 user_agents = [line.strip() for line in f if line.strip()]
#         except Exception as e:
#             logging.error(f"Failed to load user agents: {e}")
    
#     # Integrate components with crawler
#     crawler.rate_limiter = rate_limiter
#     crawler.content_extractor = content_extractor
#     crawler.proxy_manager = proxy_manager
#     crawler.user_agents = user_agents
#     crawler.respect_robots = args.respect_robots
    
#     await crawler.setup(use_browser=args.browser, headless=True)
    
#     try:
#         # Get URL from args or prompt
#         url = args.url or input("Enter URL to crawl: ")
        
#         print(f"🕷️ Starting crawler on {url} with depth {args.depth}")
#         print(f"⚙️ Configuration: Browser: {args.browser}, Rate limit: {args.rate_limit} req/sec, Robots.txt: {args.respect_robots}")
        
#         # Check if pagination parameter is detected
#         if '?' in url and ('page=' in url or 'p=' in url):
#             print("📄 Pagination detected. Using paginated crawl...")
#             page_param = re.search(r'[?&](page|p)=', url)
#             page_param = page_param.group(1) if page_param else 'page'
#             result = await crawler.crawl_with_pagination(url, depth=args.depth, page_param=page_param, max_pages=args.max_pages)
#         else:
#             result = await crawler.crawl(url, depth=args.depth)

#         if result:
#             timestamp = time.strftime("%Y%m%d_%H%M%S")
#             os.makedirs("scraped_output", exist_ok=True)
            
#             # Generate domain-based filename
#             domain = urlparse(url).netloc.replace('.', '_')
#             base_filename = f"scraped_output/{domain}_{timestamp}"
            
#             # Export in requested format(s)
#             print(f"\n✅ Content scraped successfully!")
            
#             if args.output_format in ('json', 'both'):
#                 json_file = await data_exporter.export_to_json(result, f"{base_filename}.json")
#                 print(f"  📊 JSON data: {json_file}")
                
#             if args.output_format in ('csv', 'both'):
#                 csv_file = await data_exporter.export_to_csv(result, f"{base_filename}.csv")
#                 print(f"  📈 CSV data: {csv_file}")
            
#             # Print summary statistics
#             print("\n📊 Summary Statistics:")
#             if isinstance(result, list):
#                 total_pages = len(result)
#                 total_links = sum(len(page.get('links', [])) for page in result)
#                 print(f"  📄 Pages crawled: {total_pages}")
#                 print(f"  🔗 Links found: {total_links}")
#             else:
#                 print(f"  🔗 Links found: {len(result.get('links', []))}")
#                 print(f"  🖼️ Images found: {len(result.get('media', {}).get('images', []))}")
#                 print(f"  📹 Videos found: {len(result.get('media', {}).get('videos', []))}")
#         else:
#             print("❌ Failed to crawl URL")

#     finally:
#         await crawler.close()

# def load_config(config_file='crawler_config.json'):
#     """Load configuration from file with fallback to defaults."""
#     defaults = {
#         'user_agent': 'PythonWebCrawler/1.0',
#         'rate_limit': 1.0,
#         'respect_robots': True,
#         'max_depth': 2,
#         'timeout': 30,
#         'allow_cookies': False,
#         'follow_redirects': True,
#         'max_redirects': 5,
#         'max_retries': 3,
#         'headers': {
#             'Accept': 'text/html,application/xhtml+xml,application/xml',
#             'Accept-Language': 'en-US,en;q=0.9',
#             'DNT': '1'
#         }
#     }
    
#     try:
#         if os.path.exists(config_file):
#             with open(config_file, 'r') as f:
#                 config = json.load(f)
#                 # Merge with defaults
#                 for key, value in defaults.items():
#                     if key not in config:
#                         config[key] = value
#                 return config
#     except Exception as e:
#         logging.warning(f"Failed to load config: {e}")
        
#     return defaults

# class SecurityManager:
#     """Handle security aspects of web scraping."""
    
#     @staticmethod
#     def sanitize_url(url):
#         """Sanitize URL to prevent SSRF and other injection attacks."""
#         parsed = urlparse(url)
        
#         # Prevent internal/local network access
#         hostname = parsed.netloc.lower()
#         if hostname in ('localhost', '127.0.0.1', '::1') or hostname.startswith('192.168.') or hostname.startswith('10.'):
#             raise ValueError("Access to local/internal networks not allowed")
            
#         # Only allow http and https schemes
#         if parsed.scheme not in ('http', 'https'):
#             raise ValueError("Only HTTP and HTTPS URLs are supported")
            
#         return url
    
#     @staticmethod
#     def redact_sensitive_data(data):
#         """Redact potentially sensitive information from scraped data."""
#         # Patterns to detect sensitive data
#         patterns = {
#             'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
#             'phone': r'\b(\+\d{1,2}\s?)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}\b',
#             'ssn': r'\b\d{3}-\d{2}-\d{4}\b',
#             'credit_card': r'\b(?:\d{4}[ -]?){3}\d{4}\b'
#         }
        
#         if isinstance(data, dict):
#             return {k: SecurityManager.redact_sensitive_data(v) for k, v in data.items()}
#         elif isinstance(data, list):
#             return [SecurityManager.redact_sensitive_data(item) for item in data]
#         elif isinstance(data, str):
#             text = data
#             for name, pattern in patterns.items():
#                 text = re.sub(pattern, f"[REDACTED_{name.upper()}]", text)
#             return text
#         else:
#             return data


# class DataExporter:
#     """Handle different export formats for scraped data."""
    
#     @staticmethod
#     async def export_to_json(data, filename):
#         """Export data to JSON file."""
#         with open(filename, 'w', encoding='utf-8') as f:
#             json.dump(data, f, indent=2, ensure_ascii=False)
#         return filename
        
#     @staticmethod
#     async def export_to_csv(data, filename):
#         """Export data to CSV file."""
#         # Flatten nested structures
#         flattened_data = DataExporter._flatten_data(data)
        
#         # Write to CSV
#         with open(filename, 'w', newline='', encoding='utf-8') as f:
#             if flattened_data:
#                 writer = csv.DictWriter(f, fieldnames=flattened_data[0].keys())
#                 writer.writeheader()
#                 writer.writerows(flattened_data)
#         return filename
    
#     @staticmethod
#     def _flatten_data(data):
#         """Convert nested data structure to flat records for CSV export."""
#         if isinstance(data, list):
#             return [DataExporter._flatten_dict(item) for item in data]
#         else:
#             return [DataExporter._flatten_dict(data)]
    
#     @staticmethod
#     def _flatten_dict(d, parent_key='', sep='_'):
#         """Flatten nested dictionaries."""
#         items = []
#         for k, v in d.items():
#             new_key = f"{parent_key}{sep}{k}" if parent_key else k
            
#             if isinstance(v, dict):
#                 items.extend(DataExporter._flatten_dict(v, new_key, sep).items())
#             elif isinstance(v, list):
#                 if all(isinstance(x, dict) for x in v):
#                     # Handle list of objects by joining their values
#                     for i, item in enumerate(v):
#                         items.extend(DataExporter._flatten_dict(item, f"{new_key}{sep}{i}", sep).items())
#                 else:
#                     # Join simple lists into a string
#                     items.append((new_key, ', '.join(str(x) for x in v)))
#             else:
#                 items.append((new_key, v))
#         return dict(items)

# class ProxyManager:
#     def __init__(self, proxies=None):
#         """Initialize with a list of proxies or load from file."""
#         self.proxies = proxies or []
#         self.current_index = 0
#         self.lock = asyncio.Lock()
        
#     async def load_from_file(self, filename):
#         """Load proxies from a file."""
#         try:
#             with open(filename, 'r') as f:
#                 self.proxies = [line.strip() for line in f if line.strip()]
#             logging.info(f"Loaded {len(self.proxies)} proxies from {filename}")
#         except Exception as e:
#             logging.error(f"Failed to load proxies: {e}")
    
#     async def get_next_proxy(self):
#         """Get the next proxy in the rotation."""
#         if not self.proxies:
#             return None
            
#         async with self.lock:
#             proxy = self.proxies[self.current_index]
#             self.current_index = (self.current_index + 1) % len(self.proxies)
#             return proxy
            
#     async def mark_proxy_failed(self, proxy):
#         """Mark a proxy as failed and remove it from rotation."""
#         async with self.lock:
#             if proxy in self.proxies:
#                 self.proxies.remove(proxy)
#                 logging.warning(f"Removed failed proxy {proxy}. {len(self.proxies)} remaining.")


# class ContentExtractor:
#     """Advanced content extraction with boilerplate removal."""
    
#     def __init__(self):
#         """Initialize with common boilerplate patterns."""
#         self.boilerplate_selectors = [
#             'header', 'footer', 'nav', '.sidebar', '#sidebar', 
#             '.navigation', '.menu', '.ad', '.advertisement',
#             '.cookie-banner', '.popup', '#cookie-consent'
#         ]
    
#     def extract_main_content(self, html):
#         """Extract main content from HTML with boilerplate removal."""
#         soup = BeautifulSoup(html, 'html.parser')
        
#         # Remove script and style elements
#         for element in soup.find_all(['script', 'style', 'noscript']):
#             element.decompose()
        
#         # Remove common boilerplate elements
#         for selector in self.boilerplate_selectors:
#             for element in soup.select(selector):
#                 element.decompose()
        
#         # Find main content area candidates
#         candidates = []
        
#         # Method 1: Check for semantic elements
#         for tag in ['article', 'main', 'section', '[role="main"]']:
#             elements = soup.select(tag)
#             for element in elements:
#                 candidates.append({
#                     'element': element,
#                     'score': self._calculate_content_score(element),
#                     'method': 'semantic'
#                 })
        
#         # Method 2: Find div with most paragraph content
#         for div in soup.find_all('div'):
#             paragraphs = div.find_all('p')
#             if len(paragraphs) >= 3:  # At least 3 paragraphs to be considered
#                 candidates.append({
#                     'element': div,
#                     'score': self._calculate_content_score(div),
#                     'method': 'paragraph_density'
#                 })
        
#         # Method 3: Check for content class hints
#         for element in soup.select('div[class*="content"], div[class*="article"], div[id*="content"], div[id*="article"]'):
#             candidates.append({
#                 'element': element,
#                 'score': self._calculate_content_score(element) * 1.5,  # Bonus for named content
#                 'method': 'class_hint'
#             })
        
#         # Sort candidates by score (highest first)
#         candidates.sort(key=lambda x: x['score'], reverse=True)
        
#         # Extract the best candidate's content, or use body if nothing found
#         if candidates:
#             main_content = candidates[0]['element']
#             logging.info(f"Content identified via: {candidates[0]['method']} (score: {candidates[0]['score']})")
#         else:
#             main_content = soup.body
#             logging.warning("No clear main content found, using body")
        
#         # Get clean text
#         text = self._extract_clean_text(main_content)
        
#         # Return structured result
#         return {
#             'text': text,
#             'html': str(main_content),
#             'word_count': len(text.split()),
#             'title': soup.title.get_text() if soup.title else ""
#         }
    
#     def _calculate_content_score(self, element):
#         """Calculate a content quality score for an element."""
#         text_length = len(element.get_text(strip=True))
        
#         # Count paragraph tags
#         p_count = len(element.find_all('p'))
        
#         # Count other content tags
#         content_tags = len(element.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'ul', 'ol', 'dl', 'table']))
        
#         # Count links - too many links might indicate a menu/navigation
#         links = len(element.find_all('a'))
#         link_density = links / max(1, text_length) * 1000
        
#         # Images can be content
#         image_count = len(element.find_all('img'))
        
#         # Calculate score (higher is better)
#         score = text_length * 1.0  # Base score is text length
#         score += p_count * 30      # Each paragraph adds value
#         score += content_tags * 25  # Content tags add value
#         score += image_count * 10   # Images add some value
#         score -= link_density * 50  # Penalize high link density
        
#         # Bonus for direct paragraphs (not nested in other elements)
#         direct_p_count = sum(1 for child in element.children if child.name == 'p')
#         score += direct_p_count * 20
        
#         return score
    
#     def _extract_clean_text(self, element):
#         """Extract clean text without extra whitespace."""
#         # Get visible text
#         texts = []
#         for text in element.stripped_strings:
#             if text:
#                 texts.append(text)
        
#         # Join with appropriate spacing
#         text = ' '.join(texts)
        
#         # Normalize whitespace
#         text = re.sub(r'\s+', ' ', text)
#         return text.strip()

# async def crawl_with_pagination(self, url, depth=1, page_param="page", max_pages=10):
#     """Crawl with pagination support."""
#     results = []
#     base_url = url
    
#     for page in range(1, max_pages + 1):
#         # Construct paginated URL
#         paginated_url = f"{base_url}{'&' if '?' in base_url else '?'}{page_param}={page}"
#         logging.info(f"Crawling page {page}: {paginated_url}")
        
#         result = await self.crawl(paginated_url, depth)
#         if result:
#             results.append(result)
            
#             # Check if this is the last page (no more content or different structure)
#             if self._is_last_page(result):
#                 logging.info(f"Reached last page at {page}")
#                 break
#         else:
#             # Failed to get content, assume we've reached the end
#             break
            
#     return results

# def _is_last_page(self, page_result):
#     """Detect if this is the last page based on content analysis."""
#     # Example implementation - check for indicators of last page
#     content_length = len(str(page_result.get('content', {})))
#     links_count = len(page_result.get('links', []))
    
#     # If page has significantly less content or links
#     if content_length < 1000 or links_count < 5:
#         return True
        
#     # Check for "next" link absence
#     has_next = any('next' in link.get('text', '').lower() for link in page_result.get('links', []))
#     return not has_next

# async def _fetch_with_retry(self, url, max_retries=3, backoff_factor=1.5):
#     retries = 0
#     last_exception = None
    
#     while retries < max_retries:
#         try:
#             await self.rate_limiter.wait()  # Use the rate limiter
            
#             if self.browser and self.browser.driver:
#                 return await self._fetch_with_browser(url)
#             else:
#                 async with self.session.get(url, timeout=30) as response:
#                     if response.status == 200:
#                         return await response.text()
                    
#                     # Handle status codes
#                     if response.status in (429, 503):  # Rate limited or service unavailable
#                         retry_after = int(response.headers.get('Retry-After', backoff_factor * (2 ** retries)))
#                         logging.info(f"Rate limited. Waiting {retry_after} seconds before retry.")
#                         await asyncio.sleep(retry_after)
#                     else:
#                         logging.warning(f"HTTP error {response.status} for {url}")
#                         break
                        
#         except (aiohttp.ClientError, asyncio.TimeoutError) as e:
#             last_exception = e
#             logging.warning(f"Request failed (attempt {retries+1}/{max_retries}): {str(e)}")
        
#         retries += 1
#         await asyncio.sleep(backoff_factor * (2 ** retries))
    
#     if last_exception:
#         logging.error(f"Failed to fetch {url} after {max_retries} attempts: {str(last_exception)}")
    
#     return None

# async def check_robots_txt(self, url):
#     parsed_url = urlparse(url)
#     robots_url = f"{parsed_url.scheme}://{parsed_url.netloc}/robots.txt"
    
#     try:
#         async with self.session.get(robots_url) as response:
#             if response.status == 200:
#                 robots_txt = await response.text()
#                 return self._can_fetch(robots_txt, parsed_url.path)
#     except Exception as e:
#         logging.warning(f"Error fetching robots.txt: {e}")
    
#     return True  # Default to allowing if robots.txt cannot be fetched

# def _can_fetch(self, robots_txt, path):
#     # Simple robots.txt parser implementation
#     user_agent_sections = robots_txt.split("User-agent:")
    
#     for section in user_agent_sections:
#         if not section.strip():
#             continue
        
#         lines = section.strip().split('\n')
#         agent = lines[0].strip()
        
#         if agent == '*' or agent == 'python-requests':
#             for line in lines[1:]:
#                 if line.lower().startswith('disallow:'):
#                     disallow_path = line.split(':', 1)[1].strip()
#                     if disallow_path and path.startswith(disallow_path):
#                         return False
    
#     return True

# class RateLimiter:
#     def __init__(self, requests_per_second=1):
#         self.delay = 1.0 / requests_per_second
#         self.last_request_time = 0
#         self.lock = asyncio.Lock()
    
#     async def wait(self):
#         async with self.lock:
#             elapsed = time.time() - self.last_request_time
#             if elapsed < self.delay:
#                 await asyncio.sleep(self.delay - elapsed)
#             self.last_request_time = time.time()

# class SchemaGenerator:
#     """Generates extraction schemas using LLM models."""
    
#     def __init__(self, use_ollama=True, model="mistral"):
#         self.use_ollama = use_ollama and OLLAMA_AVAILABLE
#         self.model = model
#         if self.use_ollama:
#             self.client = OllamaClient()
#         elif OPENAI_AVAILABLE:
#             self.openai_client = openai.OpenAI()
#         else:
#             logging.warning("No LLM clients available. Schema generation will be limited.")

#     @lru_cache(maxsize=100)
#     async def generate_schema(self, html_sample: str, data_type: str) -> Dict:
#         """Generate extraction schema using LLM."""
#         prompt = self._create_schema_prompt(html_sample, data_type)
        
#         try:
#             if self.use_ollama:
#                 response = await self._get_ollama_response(prompt)
#             elif OPENAI_AVAILABLE:
#                 response = await self._get_openai_response(prompt)
#             else:
#                 return self._generate_basic_schema(html_sample)
            
#             return self._parse_schema_response(response)
#         except Exception as e:
#             logging.error(f"Schema generation failed: {str(e)}")
#             return self._generate_basic_schema(html_sample)

#     def _create_schema_prompt(self, html_sample: str, data_type: str) -> str:
#         """Create optimized prompt for schema generation."""
#         return f"""Analyze this HTML and create an extraction schema for {data_type}.
# Consider these aspects:
# 1. CSS selectors for direct element access
# 2. XPath expressions for complex patterns
# 3. JSONPath for structured data
# 4. Microdata/metadata patterns

# HTML Sample:
# {html_sample}

# Return a JSON schema with:
# {{
#     "selectors": {{"field_name": "css_selector"}},
#     "xpath": {{"field_name": "xpath_expression"}},
#     "jsonpath": {{"field_name": "jsonpath_expression"}},
#     "metadata": {{"field_name": "metadata_pattern"}}
# }}"""

#     async def _get_ollama_response(self, prompt: str) -> str:
#         """Get response from Ollama model."""
#         response = await asyncio.to_thread(
#             self.client.generate,
#             model=self.model,
#             prompt=prompt
#         )
#         return response['response']

#     async def _get_openai_response(self, prompt: str) -> str:
#         """Get response from OpenAI model."""
#         response = await self.openai_client.chat.completions.create(
#             model="gpt-4",
#             messages=[{"role": "user", "content": prompt}]
#         )
#         return response.choices[0].message.content

#     def _parse_schema_response(self, response: str) -> Dict:
#         """Parse and validate LLM response into usable schema."""
#         try:
#             # Extract JSON from response (handle cases where LLM adds explanatory text)
#             json_match = re.search(r'\{[\s\S]*\}', response)
#             if json_match:
#                 schema = json.loads(json_match.group(0))
#                 return self._validate_schema(schema)
#         except json.JSONDecodeError as e:
#             logging.error(f"Invalid schema format: {str(e)}")
#         return {}

#     def _validate_schema(self, schema: Dict) -> Dict:
#         """Validate and clean up the generated schema."""
#         valid_schema = {}
#         required_sections = ['selectors', 'xpath', 'jsonpath', 'metadata']
        
#         for section in required_sections:
#             if section in schema and isinstance(schema[section], dict):
#                 valid_schema[section] = {
#                     k: v for k, v in schema[section].items()
#                     if isinstance(k, str) and isinstance(v, str)
#                 }
        
#         return valid_schema

#     def _generate_basic_schema(self, html_sample: str) -> Dict:
#         """Generate basic schema without LLM."""
#         soup = BeautifulSoup(html_sample, 'html.parser')
#         schema = {
#             'selectors': {},
#             'xpath': {},
#             'jsonpath': {},
#             'metadata': {}
#         }

#         # Basic metadata extraction
#         for meta in soup.find_all('meta', attrs={'name': True, 'content': True}):
#             name = meta['name']
#             schema['selectors'][f"meta_{name}"] = f"meta[name='{name}']"

#         # Find main content areas
#         for tag in ['main', 'article', 'div[class*="content"]']:
#             if soup.select(tag):
#                 schema['selectors']['main_content'] = tag
#                 break

#         return schema

# class DataExtractor:
#     """Handles structured data extraction using various strategies."""
    
#     def __init__(self):
#         self.vectorizer = TfidfVectorizer()
#         self.schema_generator = SchemaGenerator()
#         self._setup_ssl_context()

#     def _setup_ssl_context(self):
#         """Setup SSL context with custom validation."""
#         self.ssl_context = ssl.create_default_context()
#         self.ssl_context.check_hostname = True
#         self.ssl_context.verify_mode = ssl.CERT_REQUIRED
        
#         # Custom certificate path support
#         cert_path = os.getenv('CUSTOM_CERT_PATH')
#         if cert_path and os.path.exists(cert_path):
#             self.ssl_context.load_verify_locations(cert_path)

#     @lru_cache(maxsize=1000)
#     def chunk_by_topic(self, text: str, chunk_size: int = 1000) -> List[str]:
#         """Split text into topic-based chunks with caching."""
#         sentences = sent_tokenize(text)
#         chunks = []
#         current_chunk = []
#         current_size = 0

#         for sentence in sentences:
#             sentence_size = len(sentence)
#             if current_size + sentence_size > chunk_size and current_chunk:
#                 chunks.append(' '.join(current_chunk))
#                 current_chunk = []
#                 current_size = 0
#             current_chunk.append(sentence)
#             current_size += sentence_size

#         if current_chunk:
#             chunks.append(' '.join(current_chunk))

#         return chunks

#     async def extract_all(self, html: str, data_type: str = None) -> Dict:
#         """Comprehensive data extraction using all available methods."""
#         schema = await self.schema_generator.generate_schema(html, data_type) if data_type else {}
        
#         # Run extractions in parallel
#         with concurrent.futures.ThreadPoolExecutor() as executor:
#             futures = [
#                 executor.submit(self._extract_structured_data, html, schema),
#                 executor.submit(self._extract_json_ld, html),
#                 executor.submit(self._extract_microdata, html)
#             ]
            
#             results = {}
#             for future in concurrent.futures.as_completed(futures):
#                 results.update(future.result())
        
#         return results

#     def _extract_structured_data(self, html: str, schema: Dict) -> Dict:
#         """Extract data using schema-based approach."""
#         result = {}
#         soup = BeautifulSoup(html, 'html.parser')
#         tree = html.fromstring(html.encode())

#         # CSS Selectors
#         if 'selectors' in schema:
#             for key, selector in schema['selectors'].items():
#                 elements = soup.select(selector)
#                 result[key] = [e.get_text(strip=True) for e in elements]
#                 if len(result[key]) == 1:
#                     result[key] = result[key][0]

#         # XPath
#         if 'xpath' in schema:
#             for key, xpath in schema['xpath'].items():
#                 elements = tree.xpath(xpath)
#                 result[key] = [e.text_content().strip() for e in elements if e.text_content()]
#                 if len(result[key]) == 1:
#                     result[key] = result[key][0]

#         return {'structured': result}

#     def _extract_json_ld(self, html: str) -> Dict:
#         """Extract JSON-LD data."""
#         soup = BeautifulSoup(html, 'html.parser')
#         json_ld_data = []

#         for script in soup.find_all('script', type='application/ld+json'):
#             try:
#                 data = json.loads(script.string)
#                 json_ld_data.append(data)
#             except json.JSONDecodeError:
#                 continue

#         return {'json_ld': json_ld_data}

#     def _extract_microdata(self, html: str) -> Dict:
#         """Extract Microdata."""
#         soup = BeautifulSoup(html, 'html.parser')
#         microdata = {}

#         for element in soup.find_all(attrs={"itemscope": True}):
#             item_type = element.get("itemtype", "")
#             if not item_type:
#                 continue

#             properties = {}
#             for prop in element.find_all(attrs={"itemprop": True}):
#                 prop_name = prop["itemprop"]
                
#                 # Handle different property types
#                 if prop.name in ['meta', 'link']:
#                     prop_value = prop.get('content') or prop.get('href')
#                 elif prop.name in ['img', 'audio', 'video']:
#                     prop_value = prop.get('src')
#                 elif prop.name == 'time':
#                     prop_value = prop.get('datetime')
#                 else:
#                     prop_value = prop.get_text(strip=True)

#                 if prop_value:
#                     if prop_name in properties:
#                         if isinstance(properties[prop_name], list):
#                             properties[prop_name].append(prop_value)
#                         else:
#                             properties[prop_name] = [properties[prop_name], prop_value]
#                     else:
#                         properties[prop_name] = prop_value

#             if properties:
#                 if item_type in microdata:
#                     if isinstance(microdata[item_type], list):
#                         microdata[item_type].append(properties)
#                     else:
#                         microdata[item_type] = [microdata[item_type], properties]
#                 else:
#                     microdata[item_type] = properties

#         return {'microdata': microdata}

# class BrowserManager:
#     """Manages browser interactions and sessions."""
    
#     def __init__(self, headless=True):
#         self.options = Options()
#         if headless:
#             self.options.add_argument('--headless')
#         self.options.add_argument('--no-sandbox')
#         self.options.add_argument('--disable-dev-shm-usage')
#         self.driver = None
#         self._setup_options()

#     def _setup_options(self):
#         """Setup additional browser options for better performance and security."""
#         # Performance optimizations
#         self.options.add_argument('--disable-gpu')
#         self.options.add_argument('--disable-software-rasterizer')
#         self.options.add_argument('--disable-dev-shm-usage')
        
#         # Security options
#         self.options.add_argument('--disable-web-security')
#         self.options.add_argument('--allow-running-insecure-content')
        
#         # Add custom SSL certificates if specified
#         cert_path = os.getenv('CUSTOM_CERT_PATH')
#         if cert_path:
#             self.options.add_argument(f'--ignore-certificate-errors-spki-list={cert_path}')

#     def setup_browser(self, proxy=None, user_agent=None):
#         """Configure browser with enhanced options."""
#         if proxy:
#             if isinstance(proxy, dict):
#                 # Handle authenticated proxies
#                 auth_proxy = f"{proxy['username']}:{proxy['password']}@{proxy['host']}:{proxy['port']}"
#                 self.options.add_argument(f'--proxy-server={auth_proxy}')
#             else:
#                 self.options.add_argument(f'--proxy-server={proxy}')

#         if user_agent:
#             self.options.add_argument(f'--user-agent={user_agent}')

#         self.driver = webdriver.Chrome(options=self.options)
#         return self.driver

#     def adjust_viewport(self):
#         """Dynamically adjust viewport based on content."""
#         if self.driver:
#             total_height = self.driver.execute_script("""
#                 return Math.max(
#                     document.body.scrollHeight,
#                     document.documentElement.scrollHeight,
#                     document.body.offsetHeight,
#                     document.documentElement.offsetHeight,
#                     document.body.clientHeight,
#                     document.documentElement.clientHeight
#                 );
#             """)
            
#             width = self.driver.execute_script("""
#                 return Math.max(
#                     document.body.scrollWidth,
#                     document.documentElement.scrollWidth,
#                     document.body.offsetWidth,
#                     document.documentElement.offsetWidth,
#                     document.body.clientWidth,
#                     document.documentElement.clientWidth
#                 );
#             """)
            
#             self.driver.set_window_size(width, total_height)

#     async def wait_for_element(self, selector: str, timeout: int = 10) -> Optional[webdriver.remote.webelement.WebElement]:
#         """Asynchronously wait for element with timeout."""
#         if not self.driver:
#             return None

#         try:
#             return await asyncio.to_thread(
#                 WebDriverWait(self.driver, timeout).until,
#                 EC.presence_of_element_located((By.CSS_SELECTOR, selector))
#             )
#         except TimeoutException:
#             logging.warning(f"Element not found: {selector}")
#             return None
#         except Exception as e:
#             logging.error(f"Error waiting for element: {str(e)}")
#             return None

# class WebCrawler:
#     """Advanced web crawling and content extraction."""
    
#     def __init__(self):
#         self.browser = None
#         self.data_extractor = DataExtractor()
#         self.visited_urls = set()
#         self.cache = {}
#         self.session = None
#         self._setup_logging()

#     def _setup_logging(self):
#         """Configure logging with proper formatting."""
#         logging.basicConfig(
#             level=logging.INFO,
#             format='%(asctime)s - %(levelname)s - %(message)s',
#             datefmt='%Y-%m-%d %H:%M:%S'
#         )

#     async def setup(self, use_browser=False, **kwargs):
#         """Asynchronous setup of crawler components."""
#         if use_browser:
#             self.browser = BrowserManager(**kwargs)
        
#         # Setup aiohttp session for async requests
#         if not self.session:
#             self.session = aiohttp.ClientSession()

#     async def close(self):
#         """Cleanup resources."""
#         if self.session:
#             await self.session.close()
#         if self.browser and self.browser.driver:
#             self.browser.driver.quit()

#     async def crawl(self, url: str, depth: int = 1, **kwargs) -> Optional[Dict]:
#         """Enhanced asynchronous crawling with parallel processing."""
#         if url in self.visited_urls or depth <= 0:
#             return None

#         if url in self.cache:
#             return self.cache[url]

#         self.visited_urls.add(url)
#         result = {
#             'url': url,
#             'timestamp': time.time(),
#             'content': {},
#             'links': [],
#             'media': {}
#         }

#         try:
#             html_content = await self._fetch_content(url)
#             if not html_content:
#                 return None

#             # Process different aspects in parallel
#             async with asyncio.TaskGroup() as group:
#                 structured_task = group.create_task(
#                     self.data_extractor.extract_all(html_content)
#                 )
#                 media_task = group.create_task(
#                     self._extract_media(html_content, url)
#                 )
#                 links_task = group.create_task(
#                     self._extract_links(html_content, url)
#                 )

#             result['content'] = structured_task.result()
#             result['media'] = media_task.result()
#             result['links'] = links_task.result()

#             # Cache result
#             self.cache[url] = result

#             # Recursively crawl linked pages
#             if depth > 1:
#                 child_tasks = []
#                 for link in result['links']:
#                     if link['url'] not in self.visited_urls:
#                         child_tasks.append(
#                             self.crawl(link['url'], depth - 1, **kwargs)
#                         )
                
#                 if child_tasks:
#                     child_results = await asyncio.gather(*child_tasks)
#                     for i, child_result in enumerate(child_results):
#                         if child_result:
#                             result['links'][i]['content'] = child_result

#         except Exception as e:
#             logging.error(f"Error crawling {url}: {str(e)}")
#             return None

#         return result

#     async def _fetch_content(self, url: str) -> Optional[str]:
#         """Fetch page content with proper error handling."""
#         try:
#             if self.browser and self.browser.driver:
#                 return await self._fetch_with_browser(url)
#             else:
#                 return await self._fetch_with_requests(url)
#         except Exception as e:
#             logging.error(f"Error fetching {url}: {str(e)}")
#             return None

#     async def _fetch_with_browser(self, url: str) -> str:
#         """Fetch content using Selenium with enhanced features."""
#         await asyncio.to_thread(self.browser.driver.get, url)
#         await asyncio.to_thread(self.browser.adjust_viewport)
        
#         # Wait for dynamic content
#         await self.browser.wait_for_element('body')
#         await self._handle_lazy_loading()
        
#         return self.browser.driver.page_source

#     async def _fetch_with_requests(self, url: str) -> str:
#         """Fetch content using aiohttp."""
#         async with self.session.get(url) as response:
#             response.raise_for_status()
#             return await response.text()

#     async def _handle_lazy_loading(self, max_scrolls: int = 10):
#         """Handle lazy loading content."""
#         if not self.browser or not self.browser.driver:
#             return

#         last_height = await asyncio.to_thread(
#             self.browser.driver.execute_script,
#             "return document.body.scrollHeight"
#         )

#         for _ in range(max_scrolls):
#             await asyncio.to_thread(
#                 self.browser.driver.execute_script,
#                 "window.scrollTo(0, document.body.scrollHeight);"
#             )
#             await asyncio.sleep(1)  # Wait for content to load

#             new_height = await asyncio.to_thread(
#                 self.browser.driver.execute_script,
#                 "return document.body.scrollHeight"
#             )
#             if new_height == last_height:
#                 break
#             last_height = new_height

#     async def _extract_media(self, html: str, base_url: str) -> Dict:
#         """Extract media elements with enhanced features."""
#         soup = BeautifulSoup(html, 'html.parser')
#         media = {
#             'images': [],
#             'videos': [],
#             'audio': [],
#             'documents': []
#         }

#         # Process in parallel
#         with concurrent.futures.ThreadPoolExecutor() as executor:
#             futures = [
#                 executor.submit(self._extract_images, soup, base_url),
#                 executor.submit(self._extract_videos, soup, base_url),
#                 executor.submit(self._extract_audio, soup, base_url),
#                 executor.submit(self._extract_documents, soup, base_url)
#             ]

#             for future in concurrent.futures.as_completed(futures):
#                 media.update(future.result())

#         return media

#     def _extract_images(self, soup: BeautifulSoup, base_url: str) -> Dict:
#         """Extract image content with responsive handling."""
#         images = []
#         for img in soup.find_all('img'):
#             src = img.get('src')
#             if src:
#                 image_data = {
#                     'url': urljoin(base_url, src),
#                     'alt': img.get('alt', ''),
#                     'title': img.get('title', ''),
#                     'loading': img.get('loading', 'eager'),
#                     'srcset': []
#                 }

#                 # Handle srcset
#                 srcset = img.get('srcset', '')
#                 if srcset:
#                     image_data['srcset'] = [
#                         {'url': urljoin(base_url, s.strip().split()[0]),
#                          'size': s.strip().split()[1] if len(s.strip().split()) > 1 else None}
#                         for s in srcset.split(',')
#                         if s.strip()
#                     ]

#                 # Handle picture element
#                 picture = img.find_parent('picture')
#                 if picture:
#                     image_data['sources'] = []
#                     for source in picture.find_all('source'):
#                         source_data = {
#                             'media': source.get('media', ''),
#                             'type': source.get('type', ''),
#                             'srcset': []
#                         }
#                         if source.get('srcset'):
#                             source_data['srcset'] = [
#                                 {'url': urljoin(base_url, s.strip().split()[0]),
#                                  'size': s.strip().split()[1] if len(s.strip().split()) > 1 else None}
#                                 for s in source['srcset'].split(',')
#                                 if s.strip()
#                             ]
#                         image_data['sources'].append(source_data)

#                 images.append(image_data)

#         return {'images': images}

#     def _extract_videos(self, soup: BeautifulSoup, base_url: str) -> Dict:
#         """Extract video content with enhanced metadata."""
#         videos = []
#         for video in soup.find_all(['video', 'iframe[src*="youtube"], iframe[src*="vimeo"]']):
#             if video.name == 'video':
#                 video_data = {
#                     'type': 'html5',
#                     'controls': video.get('controls', False),
#                     'autoplay': video.get('autoplay', False),
#                     'loop': video.get('loop', False),
#                     'muted': video.get('muted', False),
#                     'poster': urljoin(base_url, video.get('poster', '')),
#                     'sources': []
#                 }
                
#                 for source in video.find_all('source'):
#                     video_data['sources'].append({
#                         'url': urljoin(base_url, source.get('src', '')),
#                         'type': source.get('type', '')
#                     })
                
#                 videos.append(video_data)
#             else:  # iframe
#                 src = video.get('src', '')
#                 if 'youtube' in src or 'vimeo' in src:
#                     videos.append({
#                         'type': 'youtube' if 'youtube' in src else 'vimeo',
#                         'url': src,
#                         'width': video.get('width', ''),
#                         'height': video.get('height', ''),
#                         'title': video.get('title', '')
#                     })

#         return {'videos': videos}

#     def _extract_audio(self, soup: BeautifulSoup, base_url: str) -> Dict:
#         """Extract audio content with metadata."""
#         audio_files = []
#         for audio in soup.find_all('audio'):
#             audio_data = {
#                 'controls': audio.get('controls', False),
#                 'autoplay': audio.get('autoplay', False),
#                 'loop': audio.get('loop', False),
#                 'muted': audio.get('muted', False),
#                 'sources': []
#             }
            
#             for source in audio.find_all('source'):
#                 audio_data['sources'].append({
#                     'url': urljoin(base_url, source.get('src', '')),
#                     'type': source.get('type', '')
#                 })
            
#             audio_files.append(audio_data)

#         return {'audio': audio_files}

#     def _extract_documents(self, soup: BeautifulSoup, base_url: str) -> Dict:
#         """Extract document links."""
#         documents = []
#         doc_extensions = ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx']
        
#         for link in soup.find_all('a', href=True):
#             href = link.get('href', '')
#             if any(href.lower().endswith(ext) for ext in doc_extensions):
#                 documents.append({
#                     'url': urljoin(base_url, href),
#                     'text': link.get_text(strip=True),
#                     'type': href.split('.')[-1].lower()
#                 })

#         return {'documents': documents}

#     async def _extract_links(self, html: str, base_url: str) -> List[Dict]:
#         """Extract and analyze links."""
#         soup = BeautifulSoup(html, 'html.parser')
#         links = []
        
#         for a in soup.find_all('a', href=True):
#             href = a.get('href')
#             if href:
#                 absolute_url = urljoin(base_url, href)
#                 link_type = 'internal' if urlparse(base_url).netloc in absolute_url else 'external'
                
#                 link_data = {
#                     'url': absolute_url,
#                     'text': a.get_text(strip=True),
#                     'type': link_type,
#                     'title': a.get('title', ''),
#                     'rel': a.get('rel', []),
#                     'target': a.get('target', '_self')
#                 }
                
#                 # Check if link points to a document
#                 if any(absolute_url.lower().endswith(ext) 
#                       for ext in ['.pdf', '.doc', '.docx', '.xls', '.xlsx']):
#                     link_data['is_document'] = True
#                     link_data['document_type'] = absolute_url.split('.')[-1].lower()
                
#                 links.append(link_data)

#         # Extract iframe sources
#         for iframe in soup.find_all('iframe', src=True):
#             src = iframe.get('src')
#             if src:
#                 links.append({
#                     'url': urljoin(base_url, src),
#                     'type': 'iframe',
#                     'title': iframe.get('title', '')
#                 })

#         return links

# async def main():
#     """Asynchronous main execution function."""
#     crawler = WebCrawler()
#     await crawler.setup(use_browser=True, headless=True)

#     try:
#         url = input("Enter URL to crawl: ")
#         result = await crawler.crawl(url, depth=2)

#         if result:
#             timestamp = time.strftime("%Y%m%d_%H%M%S")
#             os.makedirs("scraped_output", exist_ok=True)

#             # Save full data as JSON
#             json_file = f"scraped_output/data_{timestamp}.json"
#             with open(json_file, 'w', encoding='utf-8') as f:
#                 json.dump(result, f, indent=2, ensure_ascii=False)

#             print(f"\n✅ Content saved to:")
#             print(f"  📊 Full data: {json_file}")
#         else:
#             print("❌ Failed to crawl URL")

#     finally:
#         await crawler.close()

# if __name__ == "__main__":
#     asyncio.run(main())
