import aiohttp
import aiohttp
import logging
import asyncio
import urllib.parse
import xml.etree.ElementTree as ET
from typing import Dict, List, Optional
import re

logger = logging.getLogger(__name__)

class ArxivHandler:
    """Handler for arXiv API interactions"""
    
    def __init__(self):
        self.base_url = "http://export.arxiv.org/api/query"
        self.ns = {
            'atom': 'http://www.w3.org/2005/Atom',
            'arxiv': 'http://arxiv.org/schemas/atom'
        }
        self.session = None
        self.last_request_time = 0
        self.min_request_interval = 3  # Minimum 3 seconds between requests
        self.patterns = [
            r'arxiv.org/abs/(\d+\.\d+)',           # Modern format
            r'arxiv.org/pdf/(\d+\.\d+)',           # PDF links
            r'arxiv.org/abs/[a-zA-Z.-]+/(\d+)',    # Old format
            r'arxiv.org/pdf/[a-zA-Z.-]+/(\d+)'     # Old PDF format
        ]

    async def setup(self):
        """Initialize aiohttp session"""
        if not self.session:
            timeout = aiohttp.ClientTimeout(total=30, connect=10, sock_read=10)
            self.session = aiohttp.ClientSession(
                timeout=timeout,
                headers={
                    'User-Agent': 'CrewZombitX64/1.0 (Scholarly Paper Analysis Tool; Contact: your@email.com)'
                }
            )

    async def close(self):
        """Close the aiohttp session"""
        if self.session:
            await self.session.close()

    async def _enforce_rate_limit(self):
        """Enforce arXiv's rate limiting requirements"""
        current_time = asyncio.get_event_loop().time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.min_request_interval:
            await asyncio.sleep(self.min_request_interval - time_since_last)
        self.last_request_time = asyncio.get_event_loop().time()

    async def get_paper_metadata(self, arxiv_url: str) -> Optional[Dict]:
        """Extract paper ID from URL and fetch metadata"""
        paper_id = self._extract_arxiv_id(arxiv_url)
        if not paper_id:
            logger.error(f"Could not extract arXiv ID from URL: {arxiv_url}")
            return None

        try:
            await self.setup()  # Ensure session is initialized
            await self._enforce_rate_limit()
            async with self.session.get(
                self.base_url,
                params={'id_list': paper_id, 'max_results': 1}
            ) as response:
                if response.status != 200:
                    logger.error(f"arXiv API error: {response.status} - {await response.text()}")
                    return None

                content = await response.text()
                return self._parse_arxiv_response(content)

        except Exception as e:
            logger.error(f"Error fetching arXiv metadata: {str(e)}")
            return None

    def _extract_arxiv_id(self, url: str) -> Optional[str]:
        """Extract arXiv ID from various URL formats with improved error handling"""
        try:
            parsed = urllib.parse.urlparse(url)
            path = parsed.path

            for pattern in self.patterns:
                match = re.search(pattern, url)
                if match:
                    return match.group(1)

            logger.warning(f"No matching arXiv ID pattern found for URL: {url}")
            return None
        except Exception as e:
            logger.error(f"Error extracting arXiv ID from URL {url}: {str(e)}")
            return None

    def _parse_arxiv_response(self, content: str) -> Dict:
        """Parse arXiv API XML response"""
        try:
            root = ET.fromstring(content)
            entry = root.find('atom:entry', self.ns)
            
            if entry is None:
                logger.error("No entry found in arXiv response")
                return None

            # Extract basic metadata
            metadata = {
                'title': self._get_text(entry, 'atom:title'),
                'summary': self._get_text(entry, 'atom:summary'),
                'published': self._get_text(entry, 'atom:published'),
                'updated': self._get_text(entry, 'atom:updated'),
                'authors': [],
                'categories': [],
                'links': {},
                'journal_ref': self._get_text(entry, 'arxiv:journal_ref'),
                'doi': self._get_text(entry, 'arxiv:doi'),
                'primary_category': entry.find('arxiv:primary_category', self.ns).get('term') if entry.find('arxiv:primary_category', self.ns) is not None else None
            }

            # Extract authors
            for author in entry.findall('atom:author', self.ns):
                name = self._get_text(author, 'atom:name')
                affiliation = self._get_text(author, 'arxiv:affiliation')
                metadata['authors'].append({
                    'name': name,
                    'affiliation': affiliation
                })

            # Extract categories
            for category in entry.findall('atom:category', self.ns):
                metadata['categories'].append(category.get('term'))

            # Extract links
            for link in entry.findall('atom:link', self.ns):
                rel = link.get('rel', 'alternate')
                href = link.get('href', '')
                title = link.get('title', '')
                metadata['links'][rel] = {
                    'href': href,
                    'title': title
                }

            return metadata

        except Exception as e:
            logger.error(f"Error parsing arXiv response: {str(e)}")
            return None

    def _get_text(self, element: ET.Element, xpath: str) -> Optional[str]:
        """Safely extract text from XML element"""
        try:
            found = element.find(xpath, self.ns)
            return found.text.strip() if found is not None and found.text else None
        except Exception:
            return None
