import unittest
import asyncio
import time
from unittest.mock import patch, AsyncMock
from Crew4lX64.arxiv_handler import ArxivHandler
from Crew4lX64.web_crawler import WebCrawler

class TestArxivHandler(unittest.IsolatedAsyncioTestCase):

    async def test_fetch_arxiv_data_success(self):
        handler = ArxivHandler()
        url = "https://arxiv.org/abs/2311.08798"
        data = await handler.fetch_arxiv_data(url)
        self.assertIsNotNone(data)
        self.assertIn('title', data)
        self.assertIn('authors', data)
        self.assertIn('abstract', data)
        self.assertIn('categories', data)
        await handler.close_session()

    async def test_fetch_arxiv_data_invalid_url(self):
        handler = ArxivHandler()
        url = "https://arxiv.org/pdf/2502.19634"
        data = await handler.fetch_arxiv_data(url)
        self.assertIsNone(data)
        await handler.close_session()

    async def test_fetch_arxiv_data_rate_limit(self):
        handler = ArxivHandler()
        url = "https://arxiv.org/abs/2311.08798"
        start_time = time.time()
        await handler.fetch_arxiv_data(url)
        end_time = time.time()
        first_call_duration = end_time - start_time

        start_time = time.time()
        await handler.fetch_arxiv_data(url)
        end_time = time.time()
        second_call_duration = end_time - start_time

        self.assertGreaterEqual(second_call_duration, handler.delay)
        await handler.close_session()

    async def test_parse_arxiv_id(self):
        handler = ArxivHandler()
        url1 = "https://arxiv.org/abs/2311.08798"
        url2 = "http://arxiv.org/pdf/2311.08798.pdf"
        url3 = "arxiv.org/abs/2311.08798v1"

        id1 = handler._parse_arxiv_id(url1)
        id2 = handler._parse_arxiv_id(url2)
        id3 = handler._parse_arxiv_id(url3)

        self.assertEqual(id1, "2311.08798")
        self.assertEqual(id2, "2311.08798")
        self.assertEqual(id3, "2311.08798v1")
        await handler.close_session()

class TestWebCrawlerArxivIntegration(unittest.IsolatedAsyncioTestCase):

    @patch('Crew4lX64.arxiv_handler.ArxivHandler.fetch_arxiv_data')
    async def test_crawler_arxiv_handling(self, mock_fetch_arxiv_data):
        mock_fetch_arxiv_data.return_value = AsyncMock(return_value={
            'title': 'Test Title',
            'authors': ['Author 1', 'Author 2'],
            'abstract': 'Test abstract.',
            'categories': ['cs.AI'],
            'metadata': {}
        })

        crawler = WebCrawler()
        url = "https://arxiv.org/abs/2311.08798"
        result = await crawler.crawl_url(url)

        self.assertIsNotNone(result)
        self.assertIn('Test Title', result['content']['text'])
        self.assertIn('Test abstract', result['content']['text'])
        mock_fetch_arxiv_data.assert_called_once_with(url)
        await crawler.close_session()

    @patch('Crew4lX64.arxiv_handler.ArxivHandler.fetch_arxiv_data')
    async def test_crawler_arxiv_handling_failure(self, mock_fetch_arxiv_data):
        mock_fetch_arxiv_data.return_value = AsyncMock(return_value=None)

        crawler = WebCrawler()
        url = "https://arxiv.org/abs/2311.08798"
        result = await crawler.crawl_url(url)

        self.assertIsNone(result)  # Expecting None when API fails
        mock_fetch_arxiv_data.assert_called_once_with(url)
        await crawler.close_session()

if __name__ == '__main__':
    unittest.main()
