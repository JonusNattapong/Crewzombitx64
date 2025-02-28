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


class ContentExtractor:
    def __init__(self):
        self.boilerplate_selectors = [
            'header', 'footer', 'nav', '.sidebar', '#sidebar',
            '.navigation', '.menu', '.ad', '.advertisement',
            '.cookie-banner', '.popup', '#cookie-consent'
        ]
        self.vectorizer = TfidfVectorizer()
        self.schema_generator = SchemaGenerator()

    def extract_main_content(self, html):
        soup = BeautifulSoup(html, 'html.parser')

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

    def _extract_clean_text(self, element):
        texts = []
        for text in element.stripped_strings:
            if text:
                texts.append(text)

        text = ' '.join(texts)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    async def extract_all(self, html: str, data_type: str = None) -> Dict:
        schema = await self.schema_generator.generate_schema(html, data_type) if data_type else {}

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
        result = {}
        soup = BeautifulSoup(html, 'html.parser')
        tree = html.fromstring(html.encode())

        if 'selectors' in schema:
            for key, selector in schema['selectors'].items():
                elements = soup.select(selector)
                result[key] = [e.get_text(strip=True) for e in elements]
                if len(result[key]) == 1:
                    result[key] = result[key][0]

        if 'xpath' in schema:
            for key, xpath in schema['xpath'].items():
                elements = tree.xpath(xpath)
                result[key] = [e.text_content().strip() for e in elements if e.text_content()]
                if len(result[key]) == 1:
                    result[key] = result[key][0]

        return {'structured': result}

    def _extract_json_ld(self, html: str) -> Dict:
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
        soup = BeautifulSoup(html, 'html.parser')
        microdata = {}

        for element in soup.find_all(attrs={"itemscope": True}):
            item_type = element.get("itemtype", "")
            if not item_type:
                continue

            properties = {}
            for prop in element.find_all(attrs={"itemprop": True}):
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

            if properties:
                if item_type in microdata:
                    if isinstance(microdata[item_type], list):
                        microdata[item_type].append(properties)
                    else:
                        microdata[item_type] = [microdata[item_type], properties]
                else:
                    microdata[item_type] = properties

        return {'microdata': microdata}
