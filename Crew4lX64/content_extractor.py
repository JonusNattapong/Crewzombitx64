import re
import json
import logging
import concurrent.futures
from bs4 import BeautifulSoup
from typing import Dict, List
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from lxml import html
from jsonpath_ng import parse as jsonpath_parse
from schema_generator import SchemaGenerator

logger = logging.getLogger(__name__)

class ContentExtractor:
    def __init__(self):
        self.boilerplate_selectors = [
            'header', 'footer', 'nav', '.sidebar', '#sidebar',
            '.navigation', '.menu', '.ad', '.advertisement',
            '.cookie-banner', '.popup', '#cookie-consent'
        ]
        self.github_selectors = {
            'repo_name': '.author.flex-self-stretch a, strong[itemprop="name"] a',
            'repo_desc': '.f4.my-3',
            'repo_about': '#repo-content-pjax-container .Layout-sidebar .BorderGrid-row:first-child .BorderGrid-cell',
            'readme': '#readme article.markdown-body',
            'file_tree': '[role="grid"][aria-labelledby="files"]',
            'issues': '#issues-tab-count',
            'pull_requests': '#pull-requests-tab-count',
            'releases': '#releases-tab-count',
            'last_commit': 'relative-time',
            'branches': '.ml-3.wb-break-word',
            'topics': '[data-ga-click="Topic, repository page"]',
            'language_stats': '.Progress.float-left.bg-gray-dark'
        }
        self.vectorizer = TfidfVectorizer()
        self.schema_generator = SchemaGenerator()

    def extract_main_content(self, html_content, url=None):
        soup = BeautifulSoup(html_content, 'html.parser')

        # Check if it's a GitHub page
        if url and 'github.com' in url:
            return self._extract_github_content(soup, url)

        for element in soup.find_all(['script', 'style', 'noscript']):
            element.decompose()

        for selector in self.boilerplate_selectors:
            for element in soup.select(selector):
                element.decompose()

        candidates = []

        for tag in ['article', 'main', 'section', '[role="main"]']:
            elements = soup.select(tag)
            for element in elements:
                candidates.append({
                    'element': element,
                    'score': self._calculate_content_score(element),
                    'method': 'semantic'
                })

        for div in soup.find_all('div'):
            paragraphs = div.find_all('p')
            if len(paragraphs) >= 3:
                candidates.append({
                    'element': div,
                    'score': self._calculate_content_score(div),
                    'method': 'paragraph_density'
                })

        for element in soup.select('div[class*="content"], div[class*="article"], div[id*="content"], div[id*="article"]'):
            candidates.append({
                'element': element,
                'score': self._calculate_content_score(element) * 1.5,
                'method': 'class_hint'
            })

        candidates.sort(key=lambda x: x['score'], reverse=True)

        if candidates:
            main_content = candidates[0]['element']
            logging.info(f"Content identified via: {candidates[0]['method']} (score: {candidates[0]['score']})")
        else:
            main_content = soup.body
            logging.warning("No clear main content found, using body")

        text = self._extract_clean_text(main_content)

        return {
            'text': text,
            'html': str(main_content),
            'word_count': len(text.split()),
            'title': soup.title.get_text() if soup.title else ""
        }

    def _calculate_content_score(self, element):
        text_length = len(element.get_text(strip=True))
        p_count = len(element.find_all('p'))
        content_tags = len(element.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'ul', 'ol', 'dl', 'table']))
        links = len(element.find_all('a'))
        link_density = links / max(1, text_length) * 1000
        image_count = len(element.find_all('img'))

        score = text_length * 1.0
        score += p_count * 30
        score += content_tags * 25
        score += image_count * 10
        score -= link_density * 50

        direct_p_count = sum(1 for child in element.children if child.name == 'p')
        score += direct_p_count * 20

        return score

    def _extract_github_content(self, soup, url):
        """Extract content specifically from GitHub pages"""
        content = {
            'type': 'github',
            'text': '',
            'html': '',
            'metadata': {}
        }

        # Extract repository information
        for key, selector in self.github_selectors.items():
            elements = soup.select(selector)
            if elements:
                if key == 'language_stats':
                    # Parse language statistics
                    stats = {}
                    for lang_el in elements:
                        lang_name = lang_el.find_previous_sibling('span')
                        if lang_name:
                            percentage = lang_el.get('aria-valuenow', '0')
                            stats[lang_name.text.strip()] = float(percentage)
                    content['metadata']['languages'] = stats
                else:
                    value = [el.get_text(strip=True) for el in elements]
                    content['metadata'][key] = value[0] if len(value) == 1 else value

        # Extract README content
        readme = soup.select_one(self.github_selectors['readme'])
        if readme:
            content['text'] = self._extract_clean_text(readme)
            content['html'] = str(readme)
            content['word_count'] = len(content['text'].split())

        # Extract file tree
        file_tree = soup.select_one(self.github_selectors['file_tree'])
        if file_tree:
            content['metadata']['files'] = self._extract_file_tree(file_tree)

        # Extract repository title
        content['title'] = (
            content['metadata'].get('repo_name', '') or 
            soup.title.get_text() if soup.title else ""
        )

        return content

    def _extract_file_tree(self, file_tree_element):
        """Extract repository file structure"""
        files = []
        for row in file_tree_element.select('[role="row"]'):
            name_element = row.select_one('[role="rowheader"] a')
            if name_element:
                item = {
                    'name': name_element.text.strip(),
                    'path': name_element.get('href', '').strip(),
                    'type': 'file'
                }
                
                # Determine if it's a directory
                if row.select_one('.octicon-file-directory'):
                    item['type'] = 'directory'
                
                # Get last commit message if available
                commit_message = row.select_one('[role="gridcell"] a[aria-label]')
                if commit_message:
                    item['last_commit'] = commit_message.get('aria-label', '').strip()
                
                files.append(item)
        return files

    def _extract_clean_text(self, element):
        texts = []
        for text in element.stripped_strings:
            if text:
                texts.append(text)

        text = ' '.join(texts)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    async def extract_all(self, html_content: str, data_type: str = None) -> Dict:
        schema = await self.schema_generator.generate_schema(html_content, data_type) if data_type else {}

        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = [
                executor.submit(self._extract_structured_data, html_content, schema),
                executor.submit(self._extract_json_ld, html_content),
                executor.submit(self._extract_microdata, html_content)
            ]

            results = {}
            for future in concurrent.futures.as_completed(futures):
                try:
                    results.update(future.result())
                except Exception as e:
                    logging.error(f"Error in extraction task: {str(e)}")
                    continue

        return results

    def _extract_structured_data(self, html_content: str, schema: Dict) -> Dict:
        result = {}
        soup = BeautifulSoup(html_content, 'html.parser')
        
        try:
            tree = html.fromstring(html_content.encode('utf-8'))
        except Exception as e:
            logging.error(f"Failed to parse HTML with lxml: {str(e)}")
            tree = None

        if 'selectors' in schema:
            for key, selector in schema['selectors'].items():
                try:
                    elements = soup.select(selector)
                    result[key] = [e.get_text(strip=True) for e in elements]
                    if len(result[key]) == 1:
                        result[key] = result[key][0]
                except Exception as e:
                    logging.error(f"Error extracting selector {selector}: {str(e)}")

        if tree is not None and 'xpath' in schema:
            for key, xpath in schema['xpath'].items():
                try:
                    elements = tree.xpath(xpath)
                    result[key] = [e.text_content().strip() for e in elements if e.text_content()]
                    if len(result[key]) == 1:
                        result[key] = result[key][0]
                except Exception as e:
                    logging.error(f"Error extracting xpath {xpath}: {str(e)}")

        return {'structured': result}

    def _extract_json_ld(self, html_content: str) -> Dict:
        soup = BeautifulSoup(html_content, 'html.parser')
        json_ld_data = []

        for script in soup.find_all('script', type='application/ld+json'):
            try:
                if script.string:
                    data = json.loads(script.string)
                    json_ld_data.append(data)
            except (json.JSONDecodeError, TypeError) as e:
                logging.error(f"Error parsing JSON-LD: {str(e)}")
                continue

        return {'json_ld': json_ld_data}

    def _extract_microdata(self, html_content: str) -> Dict:
        soup = BeautifulSoup(html_content, 'html.parser')
        microdata = {}

        for element in soup.find_all(attrs={"itemscope": True}):
            item_type = element.get("itemtype", "")
            if not item_type:
                continue

            properties = {}
            for prop in element.find_all(attrs={"itemprop": True}):
                try:
                    prop_name = prop["itemprop"]

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
                except Exception as e:
                    logging.error(f"Error extracting microdata property: {str(e)}")
                    continue

            if properties:
                if item_type in microdata:
                    if isinstance(microdata[item_type], list):
                        microdata[item_type].append(properties)
                    else:
                        microdata[item_type] = [microdata[item_type], properties]
                else:
                    microdata[item_type] = properties

        return {'microdata': microdata}
