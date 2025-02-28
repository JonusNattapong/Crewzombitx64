import asyncio
import sys
import time

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

class ProgressSpinner:
    def __init__(self):
        self.spinners = ['⣾', '⣽', '⣻', '⢿', '⡿', '⣟', '⣯', '⣷']
        self.i = 0
        self.is_running = True
        self.start_time = None
        self.status = "Initializing..."
        
    def update_status(self, status):
        self.status = status
        
    async def spin(self):
        self.start_time = time.time()
        while self.is_running:
            elapsed = time.time() - self.start_time
            sys.stdout.write(f"\r{self.spinners[self.i]} {self.status} (elapsed: {elapsed:.1f}s)")
            sys.stdout.flush()
            await asyncio.sleep(0.1)
            self.i = (self.i + 1) % len(self.spinners)
            
    def stop(self):
        self.is_running = False
        sys.stdout.write("\r")
        sys.stdout.flush()

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

    # Initialize spinner
    spinner = ProgressSpinner()
    spinner_task = asyncio.create_task(spinner.spin())

    try:
        spinner.update_status("Initializing crawler...")
        crawler = WebCrawler()
        rate_limiter = RateLimiter(requests_per_second=args.rate_limit)
        content_extractor = ContentExtractor()
        data_exporter = DataExporter()

        if args.proxies:
            spinner.update_status("Loading proxy list...")
            proxy_manager = ProxyManager()
            await proxy_manager.load_from_file(args.proxies)

        if args.user_agents:
            spinner.update_status("Loading user agents...")
            try:
                with open(args.user_agents, 'r') as f:
                    user_agents = [line.strip() for line in f if line.strip()]
            except Exception as e:
                logging.error(f"Failed to load user agents: {e}")

        spinner.update_status("Setting up crawler configuration...")
        await crawler.setup(
            use_browser=args.browser,
            respect_robots=args.respect_robots,
            rate_limit=args.rate_limit,
            use_proxies=bool(args.proxies),
            headless=True
        )

        url = args.url or input("\nEnter URL to crawl: ")
        print(f"\n📋 Configuration:")
        print(f"  • Depth: {args.depth}")
        print(f"  • Browser mode: {'✅' if args.browser else '❌'}")
        print(f"  • Rate limit: {args.rate_limit} req/sec")
        print(f"  • Robots.txt: {'✅' if args.respect_robots else '❌'}")
        print(f"  • Proxy enabled: {'✅' if args.proxies else '❌'}")

        spinner.update_status(f"Crawling {url}...")
        start_time = time.time()

        try:
            if '?' in url and ('page=' in url or 'p=' in url):
                print("\n📄 Pagination detected. Using paginated crawl...")
                page_param = 'page' if 'page=' in url else 'p'
                result = await crawler.crawl_with_pagination(url, depth=args.depth, page_param=page_param, max_pages=args.max_pages)
            else:
                result = await crawler.crawl(url, depth=args.depth)

            spinner.stop()
            elapsed = time.time() - start_time
            print(f"\r✅ Crawling completed in {elapsed:.1f} seconds!")

        except Exception as e:
            spinner.stop()
            print(f"\r❌ Crawling failed: {str(e)}")
            logging.error(f"Error crawling {url}: {e}")
            return

        if result:
            spinner.update_status("Saving results...")
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            os.makedirs("scraped_output", exist_ok=True)
            base_filename = f"scraped_output/{urlparse(url).netloc.replace('.', '_')}_{timestamp}"

            if args.output_format in ('json', 'both'):
                json_file = await data_exporter.export_to_json(result, f"{base_filename}.json")
                print(f"  📊 JSON data saved: {json_file}")

            if args.output_format in ('csv', 'both'):
                csv_file = await data_exporter.export_to_csv(result, f"{base_filename}.csv")
                print(f"  📈 CSV data saved: {csv_file}")

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
                if 'documents' in result.get('media', {}):
                    print(f"  📄 Documents found: {len(result.get('media', {}).get('documents', []))}")
        else:
            print("\n❌ Failed to crawl URL")

    except Exception as e:
        print(f"\n❌ An error occurred: {str(e)}")
    finally:
        spinner.stop()
        spinner_task.cancel()
        try:
            await spinner_task
        except asyncio.CancelledError:
            pass
        print("\n🧹 Cleaning up...")
        await crawler.close()
        print("✅ Done!")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Crawler stopped by user")
    except Exception as e:
        print(f"\n❌ An error occurred: {str(e)}")
