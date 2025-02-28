import asyncio

ascii_art = """                                                                            
███████╗ ██████╗ ███╗   ███╗██████╗ ██╗████████╗██╗  ██╗ ██████╗ ██╗  ██╗
╚══███╔╝██╔═══██╗████╗ ████║██╔══██╗██║╚══██╔══╝╚██╗██╔╝██╔════╝ ██║  ██║
  ███╔╝ ██║   ██║██╔████╔██║██████╔╝██║   ██║    ╚███╔╝ ███████╗ ███████║
 ███╔╝  ██║   ██║██║╚██╔╝██║██╔══██╗██║   ██║    ██╔██╗ ██╔═══██╗╚════██║
███████╗╚██████╔╝██║ ╚═╝ ██║██████╔╝██║   ██║   ██╔╝ ██╗╚██████╔╝     ██║
╚══════╝ ╚═════╝ ╚═╝     ╚═╝╚═════╝ ╚═╝   ╚═╝   ╚═╝  ╚═╝ ╚═════╝      ╚═╝
    """

from web_crawler import WebCrawler
from data_exporter import DataExporter
from argparse import ArgumentParser
from rate_limiter import RateLimiter
from content_extractor import ContentExtractor
from proxy_manager import ProxyManager
from urllib.parse import urlparse
import logging
import time
import os

async def main():
    parser = ArgumentParser(description='Advanced Web Crawler')
    parser.add_argument('--url', help='URL to crawl', required=False)
    parser.add_argument('--depth', type=int, default=2, help='Crawl depth')
    parser.add_argument('--browser', action='store_true', help='Use browser for rendering')
    parser.add_argument('--output-format', choices=['json', 'csv', 'both'], default='json', help='Output format')
    parser.add_argument('--rate-limit', type=float, default=1.0, help='Requests per second')
    parser.add_argument('--proxies', help='File with proxy list (one per line)')
    parser.add_argument('--user-agents', help='File with user agents (one per line)')
    parser.add_argument('--respect-robots', action='store_true', help='Respect robots.txt')
    parser.add_argument('--max-pages', type=int, default=10, help='Maximum pages to crawl with pagination')
    args = parser.parse_args()
    
    print(ascii_art)

    crawler = WebCrawler()
    rate_limiter = RateLimiter(requests_per_second=args.rate_limit)
    content_extractor = ContentExtractor()
    data_exporter = DataExporter()

    proxy_manager = None
    if args.proxies:
        proxy_manager = ProxyManager()
        await proxy_manager.load_from_file(args.proxies)

    user_agents = []
    if args.user_agents:
        try:
            with open(args.user_agents, 'r') as f:
                user_agents = [line.strip() for line in f if line.strip()]
        except Exception as e:
            logging.error(f"Failed to load user agents: {e}")

    crawler.rate_limiter = rate_limiter
    crawler.content_extractor = content_extractor
    crawler.proxy_manager = proxy_manager
    crawler.user_agents = user_agents
    crawler.respect_robots = args.respect_robots

    await crawler.setup(use_browser=args.browser, headless=True)

    try:
        url = args.url or input("Enter URL to crawl: ")
        print(f"🕷️ Starting crawler on {url} with depth {args.depth}")
        print(f"⚙️ Configuration: Browser: {args.browser}, Rate limit: {args.rate_limit} req/sec, Robots.txt: {args.respect_robots}")

        if '?' in url and ('page=' in url or 'p=' in url):
            print("📄 Pagination detected. Using paginated crawl...")
            page_param = 'page' if 'page=' in url else 'p'
            result = await crawler.crawl_with_pagination(url, depth=args.depth, page_param=page_param, max_pages=args.max_pages)
        else:
            result = await crawler.crawl(url, depth=args.depth)

        if result:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            os.makedirs("scraped_output", exist_ok=True)
            base_filename = f"scraped_output/{urlparse(url).netloc.replace('.', '_')}_{timestamp}"

            if args.output_format in ('json', 'both'):
                json_file = await data_exporter.export_to_json(result, f"{base_filename}.json")
                print(f"  📊 JSON data: {json_file}")

            if args.output_format in ('csv', 'both'):
                csv_file = await data_exporter.export_to_csv(result, f"{base_filename}.csv")
                print(f"  📈 CSV data: {csv_file}")

            print("\n📊 Summary Statistics:")
            if isinstance(result, list):
                total_pages = len(result)
                total_links = sum(len(page.get('links', [])) for page in result)
                print(f"  📄 Pages crawled: {total_pages}")
                print(f"  🔗 Links found: {total_links}")
            else:
                print(f"  🔗 Links found: {len(result.get('links', []))}")
                print(f"  🖼️ Images found: {len(result.get('media', {}).get('images', []))}")
                print(f"  📹 Videos found: {len(result.get('media', {}).get('videos', []))}")
        else:
            print("❌ Failed to crawl URL")

    finally:
        await crawler.close()

if __name__ == "__main__":
    asyncio.run(main())
