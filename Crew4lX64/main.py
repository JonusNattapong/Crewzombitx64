import asyncio
import sys
import time
from argparse import ArgumentParser
from urllib.parse import urlparse
import logging
import os

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
from rate_limiter import RateLimiter
from content_extractor import ContentExtractor
from proxy_manager import ProxyManager

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

def setup_argument_parser():
    parser = ArgumentParser(description='Advanced Web Crawler')
    
    # Basic Options
    basic_group = parser.add_argument_group('Basic Options')
    basic_group.add_argument('--url', help='URL to crawl')
    basic_group.add_argument('--depth', type=int, default=2, help='Crawl depth (default: 2)')
    basic_group.add_argument('--output-format', choices=['json', 'csv', 'md', 'all'], default='json',
                          help='Output format: json, csv, md, or all (default: json)')
    basic_group.add_argument('--output-dir', default='scraped_output',
                          help='Output directory (default: scraped_output)')

    # Browser Options
    browser_group = parser.add_argument_group('Browser Options')
    browser_group.add_argument('--browser', action='store_true', help='Use browser for rendering')
    browser_group.add_argument('--headless', action='store_true', help='Run browser in headless mode')
    browser_group.add_argument('--wait-time', type=float, default=2.0,
                             help='Wait time for dynamic content (default: 2.0s)')
    browser_group.add_argument('--scroll', action='store_true', 
                             help='Enable auto-scrolling for dynamic loading')

    # Rate Limiting Options
    rate_group = parser.add_argument_group('Rate Limiting Options')
    rate_group.add_argument('--rate-limit', type=float, default=1.0,
                          help='Requests per second (default: 1.0)')
    rate_group.add_argument('--retry-count', type=int, default=3,
                          help='Number of retries for failed requests (default: 3)')
    rate_group.add_argument('--retry-delay', type=float, default=1.0,
                          help='Delay between retries in seconds (default: 1.0)')

    # Proxy Options
    proxy_group = parser.add_argument_group('Proxy Options')
    proxy_group.add_argument('--proxies', help='File with proxy list (one per line)')
    proxy_group.add_argument('--proxy-type', choices=['http', 'socks5'], default='http',
                          help='Proxy type (default: http)')
    proxy_group.add_argument('--proxy-timeout', type=float, default=10.0,
                          help='Proxy timeout in seconds (default: 10.0)')

    # Authentication Options
    auth_group = parser.add_argument_group('Authentication Options')
    auth_group.add_argument('--user-agents', help='File with user agents (one per line)')
    auth_group.add_argument('--cookies', help='File with cookies in JSON format')
    auth_group.add_argument('--headers', help='File with custom headers in JSON format')

    # Crawling Options
    crawl_group = parser.add_argument_group('Crawling Options')
    crawl_group.add_argument('--respect-robots', action='store_true',
                          help='Respect robots.txt rules')
    crawl_group.add_argument('--max-pages', type=int, default=10,
                          help='Maximum pages to crawl with pagination (default: 10)')
    crawl_group.add_argument('--include-pattern', 
                          help='Only crawl URLs matching this pattern (regex)')
    crawl_group.add_argument('--exclude-pattern',
                          help='Skip URLs matching this pattern (regex)')
    crawl_group.add_argument('--allow-subdomains', action='store_true',
                          help='Allow crawling subdomains')

    # Export Options
    export_group = parser.add_argument_group('Export Options')
    export_group.add_argument('--compress', action='store_true',
                           help='Compress output files')
    export_group.add_argument('--pretty', action='store_true',
                           help='Pretty print JSON output')
    export_group.add_argument('--timestamp', action='store_true',
                           help='Add timestamp to output filenames')
    export_group.add_argument('--export-links', action='store_true',
                           help='Export links to separate file')
    
    return parser

async def main():
    parser = setup_argument_parser()
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
            headless=args.headless,
            wait_time=args.wait_time,
            auto_scroll=args.scroll,
            retry_count=args.retry_count,
            retry_delay=args.retry_delay,
            proxy_timeout=args.proxy_timeout,
            include_pattern=args.include_pattern,
            exclude_pattern=args.exclude_pattern,
            allow_subdomains=args.allow_subdomains
        )

        url = args.url or input("\nEnter URL to crawl: ")
        print(f"\n📋 Configuration:")
        print(f"  • Depth: {args.depth}")
        print(f"  • Browser mode: {'✅' if args.browser else '❌'}")
        print(f"  • Rate limit: {args.rate_limit} req/sec")
        print(f"  • Robots.txt: {'✅' if args.respect_robots else '❌'}")
        print(f"  • Proxy enabled: {'✅' if args.proxies else '❌'}")
        print(f"  • Output format: {args.output_format}")
        if args.browser:
            print(f"  • Headless mode: {'✅' if args.headless else '❌'}")
            print(f"  • Wait time: {args.wait_time}s")
            print(f"  • Auto-scroll: {'✅' if args.scroll else '❌'}")
        if args.proxies:
            print(f"  • Proxy type: {args.proxy_type}")
            print(f"  • Proxy timeout: {args.proxy_timeout}s")

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
            timestamp = time.strftime("%Y%m%d_%H%M%S") if args.timestamp else ""
            os.makedirs(args.output_dir, exist_ok=True)
            base_filename = f"{args.output_dir}/{urlparse(url).netloc.replace('.', '_')}{f'_{timestamp}' if timestamp else ''}"

            if args.output_format in ('json', 'all'):
                json_file = await data_exporter.export_to_json(result, f"{base_filename}.json")
                print(f"  📊 JSON data saved: {json_file}")

            if args.output_format in ('csv', 'all'):
                csv_file = await data_exporter.export_to_csv(result, f"{base_filename}.csv")
                print(f"  📈 CSV data saved: {csv_file}")

            if args.output_format in ('md', 'all'):
                md_file = await data_exporter.export_to_markdown(result, f"{base_filename}.md")
                print(f"  📝 Markdown data saved: {md_file}")

            if args.export_links:
                links_file = f"{base_filename}_links.txt"
                with open(links_file, 'w', encoding='utf-8') as f:
                    for link in result.get('links', []):
                        f.write(f"{link.get('url')}\n")
                print(f"  🔗 Links exported: {links_file}")

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
