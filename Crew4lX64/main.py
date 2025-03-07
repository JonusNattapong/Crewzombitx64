#!/usr/bin/env python3
import asyncio
import sys
import time
from argparse import ArgumentParser
from urllib.parse import urlparse
import logging
import os
from typing import Dict, Any

from web_crawler import WebCrawler
from data_exporter import DataExporter
from rate_limiter import RateLimiter
from content_extractor import ContentExtractor
from proxy_manager import ProxyManager
from preset_configs import get_preset_config

ascii_art = """                                                                            
███████╗ ██████╗ ███╗   ███╗██████╗ ██╗████████╗██╗  ██╗ ██████╗ ██╗  ██╗
╚══███╔╝██╔═══██╗████╗ ████║██╔══██╗██║╚══██╔══╝╚██╗██╔╝██╔════╝ ██║  ██║
  ███╔╝ ██║   ██║██╔████╔██║██████╔╝██║   ██║    ╚███╔╝ ███████╗ ███████║
 ███╔╝  ██║   ██║██║╚██╔╝██║██╔══██╗██║   ██║    ██╔██╗ ██╔═══██╗╚════██║
███████╗╚██████╔╝██║ ╚═╝ ██║██████╔╝██║   ██║   ██╔╝ ██╗╚██████╔╝     ██║
╚══════╝ ╚═════╝ ╚═╝     ╚═╝╚═════╝ ╚═╝   ╚═╝   ╚═╝  ╚═╝ ╚═════╝      ╚═╝
    """

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
    basic_group.add_argument('--interactive', action='store_true', 
                          help='Enable interactive mode for configuration')
    basic_group.add_argument('--preset', choices=['basic', 'aggressive', 'stealth', 'api', 'archive'],
                          help='Use preset configuration')
    basic_group.add_argument('--depth', type=int, default=2, 
                          help='Crawl depth (default: 2)')
    basic_group.add_argument('--output-format', choices=['json', 'csv', 'md', 'all'], 
                          default='json',
                          help='Output format: json, csv, md, or all (default: json)')
    basic_group.add_argument('--output-dir', default='scraped_output',
                          help='Output directory (default: scraped_output)')

    # Advanced Options (hidden by default in interactive mode)
    advanced_group = parser.add_argument_group('Advanced Options')
    advanced_group.add_argument('--browser', action='store_true', 
                             help='Use browser for rendering')
    advanced_group.add_argument('--headless', action='store_true', 
                             help='Run browser in headless mode')
    advanced_group.add_argument('--wait-time', type=float, default=2.0,
                             help='Wait time for dynamic content (default: 2.0s)')
    advanced_group.add_argument('--scroll', action='store_true', 
                             help='Enable auto-scrolling for dynamic loading')
    advanced_group.add_argument('--rate-limit', type=float, default=1.0,
                             help='Requests per second (default: 1.0)')
    advanced_group.add_argument('--retry-count', type=int, default=3,
                             help='Number of retries for failed requests (default: 3)')
    advanced_group.add_argument('--retry-delay', type=float, default=1.0,
                             help='Delay between retries in seconds (default: 1.0)')
    advanced_group.add_argument('--proxies', help='File with proxy list (one per line)')
    advanced_group.add_argument('--user-agents', help='File with user agents (one per line)')
    advanced_group.add_argument('--respect-robots', action='store_true',
                             help='Respect robots.txt rules')
    
    return parser

def get_interactive_config() -> Dict[str, Any]:
    """Get configuration through interactive prompts."""
    config = {}
    
    print("\n🔧 Interactive Configuration")
    print("---------------------------")
    
    # Purpose selection
    print("\nWhat's the main purpose of your crawl?")
    print("1. Basic website crawling (safe defaults)")
    print("2. Aggressive crawling (faster, higher depth)")
    print("3. Stealth crawling (slower, more cautious)")
    print("4. API endpoints (optimized for REST APIs)")
    print("5. Archive crawling (high depth, large files)")
    
    while True:
        try:
            choice = int(input("\nEnter your choice (1-5): "))
            if 1 <= choice <= 5:
                break
            print("Please enter a number between 1 and 5")
        except ValueError:
            print("Please enter a valid number")
    
    preset_map = {
        1: 'basic',
        2: 'aggressive',
        3: 'stealth',
        4: 'api',
        5: 'archive'
    }
    
    config.update(get_preset_config(preset_map[choice]))
    
    # Output format
    print("\nSelect output format:")
    print("1. JSON (default)")
    print("2. CSV")
    print("3. Markdown")
    print("4. All formats")
    
    while True:
        try:
            format_choice = int(input("\nEnter your choice (1-4): "))
            if 1 <= format_choice <= 4:
                break
            print("Please enter a number between 1 and 4")
        except ValueError:
            print("Please enter a valid number")
    
    format_map = {
        1: 'json',
        2: 'csv',
        3: 'md',
        4: 'all'
    }
    
    config['output_format'] = format_map[format_choice]
    
    # Advanced options
    if input("\nWould you like to configure advanced options? (y/N): ").lower() == 'y':
        config['browser'] = input("Use browser rendering? (y/N): ").lower() == 'y'
        if config['browser']:
            config['headless'] = input("Run in headless mode? (Y/n): ").lower() != 'n'
            config['wait_time'] = float(input("Wait time for dynamic content (seconds, default 2.0): ") or 2.0)
            config['scroll'] = input("Enable auto-scrolling? (y/N): ").lower() == 'y'
        
        config['use_proxies'] = input("Use proxy servers? (y/N): ").lower() == 'y'
        if config['use_proxies']:
            config['proxy_file'] = input("Path to proxy list file: ")
    
    return config

async def main():
    parser = setup_argument_parser()
    args = parser.parse_args()
    
    print(ascii_art)
    
    # Initialize spinner
    spinner = ProgressSpinner()
    spinner_task = asyncio.create_task(spinner.spin())
    
    try:
        # Get configuration
        if args.interactive:
            config = get_interactive_config()
        elif args.preset:
            config = get_preset_config(args.preset)
        else:
            # Use command line arguments
            config = vars(args)
        
        spinner.update_status("Initializing crawler...")
        crawler = WebCrawler()
        rate_limiter = RateLimiter(requests_per_second=config.get('rate_limit', 1.0))
        content_extractor = ContentExtractor()
        data_exporter = DataExporter()

        if config.get('use_proxies'):
            spinner.update_status("Loading proxy list...")
            proxy_manager = ProxyManager()
            if 'proxy_file' in config:
                await proxy_manager.load_from_file(config['proxy_file'])
            elif args.proxies:
                await proxy_manager.load_from_file(args.proxies)

        spinner.update_status("Setting up crawler configuration...")
        await crawler.setup(
            use_browser=config.get('browser', False),
            respect_robots=config.get('respect_robots', True),
            rate_limit=config.get('rate_limit', 1.0),
            use_proxies=config.get('use_proxies', False),
            headless=config.get('headless', True),
            wait_time=config.get('wait_time', 2.0),
            auto_scroll=config.get('scroll', False),
            retry_count=config.get('retry_count', 3),
            retry_delay=config.get('retry_delay', 1.0),
            proxy_timeout=config.get('proxy_timeout', 10.0)
        )

        url = args.url or input("\nEnter URL to crawl: ")
        
        print(f"\n📋 Configuration:")
        print(f"  • Mode: {args.preset or 'Custom'}")
        print(f"  • Depth: {config.get('depth', 2)}")
        print(f"  • Browser mode: {'✅' if config.get('browser') else '❌'}")
        print(f"  • Rate limit: {config.get('rate_limit', 1.0)} req/sec")
        print(f"  • Robots.txt: {'✅' if config.get('respect_robots') else '❌'}")
        print(f"  • Proxy enabled: {'✅' if config.get('use_proxies') else '❌'}")
        print(f"  • Output format: {config.get('output_format', 'json')}")
        
        if config.get('browser'):
            print(f"  • Headless mode: {'✅' if config.get('headless') else '❌'}")
            print(f"  • Wait time: {config.get('wait_time')}s")
            print(f"  • Auto-scroll: {'✅' if config.get('scroll') else '❌'}")

        spinner.update_status(f"Crawling {url}...")
        start_time = time.time()

        try:
            if '?' in url and ('page=' in url or 'p=' in url):
                print("\n📄 Pagination detected. Using paginated crawl...")
                page_param = 'page' if 'page=' in url else 'p'
                result = await crawler.crawl_with_pagination(
                    url, 
                    depth=config.get('depth', 2),
                    page_param=page_param,
                    max_pages=config.get('max_pages', 10)
                )
            else:
                result = await crawler.crawl(url, depth=config.get('depth', 2))

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
            timestamp = time.strftime("%Y%m%d_%H%M%S") if config.get('timestamp', True) else ""
            os.makedirs(config.get('output_dir', 'scraped_output'), exist_ok=True)
            base_filename = f"{config.get('output_dir', 'scraped_output')}/{urlparse(url).netloc.replace('.', '_')}{f'_{timestamp}' if timestamp else ''}"

            output_format = config.get('output_format', 'json')
            if output_format in ('json', 'all'):
                json_file = await data_exporter.export_to_json(result, f"{base_filename}.json")
                print(f"  📊 JSON data saved: {json_file}")

            if output_format in ('csv', 'all'):
                csv_file = await data_exporter.export_to_csv(result, f"{base_filename}.csv")
                print(f"  📈 CSV data saved: {csv_file}")

            if output_format in ('md', 'all'):
                md_file = await data_exporter.export_to_markdown(result, f"{base_filename}.md")
                print(f"  📝 Markdown data saved: {md_file}")

            if config.get('export_links', True):
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
