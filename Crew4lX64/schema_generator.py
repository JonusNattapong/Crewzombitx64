import json
import logging
import re
import asyncio
from typing import Dict
from functools import lru_cache
from bs4 import BeautifulSoup

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

class SchemaGenerator:
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
        response = await asyncio.to_thread(
            self.client.generate,
            model=self.model,
            prompt=prompt
        )
        return response['response']

    async def _get_openai_response(self, prompt: str) -> str:
        response = await self.openai_client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content

    def _parse_schema_response(self, response: str) -> Dict:
        try:
            json_match = re.search(r'\{[\s\S]*\}', response)
            if json_match:
                schema = json.loads(json_match.group(0))
                return self._validate_schema(schema)
        except json.JSONDecodeError as e:
            logging.error(f"Invalid schema format: {str(e)}")
        return {}

    def _validate_schema(self, schema: Dict) -> Dict:
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
        soup = BeautifulSoup(html_sample, 'html.parser')
        schema = {
            'selectors': {},
            'xpath': {},
            'jsonpath': {},
            'metadata': {}
        }

        for meta in soup.find_all('meta', attrs={'name': True, 'content': True}):
            name = meta['name']
            schema['selectors'][f"meta_{name}"] = f"meta[name='{name}']"

        for tag in ['main', 'article', 'div[class*="content"]']:
            if soup.select(tag):
                schema['selectors']['main_content'] = tag
                break

        return schema
