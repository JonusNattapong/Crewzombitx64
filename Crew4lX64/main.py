#!/usr/bin/env python3
import asyncio
import sys
import time
import os
import platform
import queue
import threading
from argparse import ArgumentParser
from urllib.parse import urlparse
import logging
import os
from typing import Dict, Any, List, Optional
import json
import shutil
import traceback

from Crew4lX64.web_crawler import WebCrawler
from Crew4lX64.data_exporter import DataExporter
from Crew4lX64.rate_limiter import RateLimiter
from Crew4lX64.content_extractor import ContentExtractor
from Crew4lX64.proxy_manager import ProxyManager
from Crew4lX64.preset_configs import get_preset_config
from Crew4lX64.cache_manager import CacheManager

# Check for rich module
try:
    from rich.console import Console
    from rich.progress import Progress, TextColumn, BarColumn, TimeElapsedColumn
    from rich.panel import Panel
    from rich.table import Table
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

# Check for GUI modules
try:
    import tkinter as tk
    from tkinter import ttk, filedialog, messagebox
    GUI_AVAILABLE = True
except ImportError:
    GUI_AVAILABLE = False

# ASCII art banner
ascii_art = '''
███████╗ ██████╗ ███╗   ███╗██████╗ ██╗████████╗██╗  ██╗ ██████╗ ██╗  ██╗
╚══███╔╝██╔═══██╗████╗ ████║██╔══██╗██║╚══██╔══╝╚██╗██╔╝██╔════╝ ██║  ██║
  ███╔╝ ██║   ██║██╔████╔██║██████╔╝██║   ██║    ╚███╔╝ ███████╗ ███████║
 ███╔╝  ██║   ██║██║╚██╔╝██║██╔══██╗██║   ██║    ██╔██╗ ██╔═══██╗╚════██║
███████╗╚██████╔╝██║ ╚═╝ ██║██████╔╝██║   ██║   ██╔╝ ██╗╚██████╔╝     ██║
╚══════╝ ╚═════╝ ╚═╝     ╚═╝╚═════╝ ╚═╝   ╚═╝   ╚═╝  ╚═╝ ╚═════╝      ╚═╝
'''

# Set up console for rich output
console = Console() if RICH_AVAILABLE else None

class ProgressTracker:
    """Progress tracking with rich output support"""
    def __init__(self, use_rich=False):
        self.use_rich = use_rich and RICH_AVAILABLE
        self.spinners = ['⣾', '⣽', '⣻', '⢿', '⡿', '⣟', '⣯', '⣷']
        self.i = 0
        self.is_running = True
        self.status = "Initializing..."
        self.progress = None
        self.task_id = None

    def setup(self):
        """Initialize the progress display"""
        if self.use_rich:
            self.progress = Progress(
                TextColumn("[bold blue]{task.description}"),
                BarColumn(),
                TimeElapsedColumn(),
                console=console
            )
            self.progress.start()
            self.task_id = self.progress.add_task(self.status, total=None)

    def update_status(self, status):
        """Update the progress status"""
        self.status = status
        try:
            if self.use_rich and self.progress and self.task_id is not None:
                self.progress.update(self.task_id, description=status)
        except Exception:
            pass

    def spin(self):
        """Show spinner animation in non-rich mode"""
        while self.is_running:
            try:
                if not self.use_rich:
                    sys.stdout.write(f"\r{self.spinners[self.i]} {self.status}")
                    sys.stdout.flush()
                    self.i = (self.i + 1) % len(self.spinners)
                time.sleep(0.1)
            except Exception:
                break

    def stop(self):
        """Stop the progress display"""
        self.is_running = False
        try:
            if self.use_rich and self.progress:
                self.progress.stop()
            else:
                sys.stdout.write("\r" + " " * 80 + "\r")
                sys.stdout.flush()
        except Exception:
            pass

class QueueHandler(logging.Handler):
    """Custom logging handler for GUI mode"""
    def __init__(self, handler_function):
        super().__init__()
        self.handler_function = handler_function

    def emit(self, record):
        try:
            msg = self.format(record)
            self.handler_function(msg)
        except Exception:
            self.handleError(record)

def setup_argument_parser():
    """Create and configure the argument parser"""
    parser = ArgumentParser(description='Crew4lX64 Advanced Web Crawler')
    
    # Basic Options
    basic_group = parser.add_argument_group('Basic Options')
    basic_group.add_argument('--url', help='URL to crawl')
    basic_group.add_argument('--interactive', action='store_true', help='Interactive mode')
    basic_group.add_argument('--gui', action='store_true', help='Launch GUI mode')
    basic_group.add_argument('--preset', choices=['basic', 'aggressive', 'stealth', 'api', 'archive'])
    basic_group.add_argument('--depth', type=int, default=2)
    basic_group.add_argument('--output-format', choices=['json', 'csv', 'md', 'html', 'all'], 
                           default='json')
    basic_group.add_argument('--output-dir', default='scraped_output')

    # Advanced Options
    advanced_group = parser.add_argument_group('Advanced Options')
    advanced_group.add_argument('--browser', action='store_true')
    advanced_group.add_argument('--headless', action='store_true')
    advanced_group.add_argument('--wait-time', type=float, default=2.0)
    advanced_group.add_argument('--scroll', action='store_true')
    advanced_group.add_argument('--rate-limit', type=float, default=1.0)
    advanced_group.add_argument('--retry-count', type=int, default=3)
    advanced_group.add_argument('--retry-delay', type=float, default=1.0)
    advanced_group.add_argument('--proxies', help='Proxy list file')
    advanced_group.add_argument('--respect-robots', action='store_true')

    # Display Options
    display_group = parser.add_argument_group('Display Options')
    display_group.add_argument('--quiet', action='store_true')
    display_group.add_argument('--rich', action='store_true')

    return parser

def show_summary(config: Dict[str, Any], url: str):
    """Display crawl configuration summary"""
    if RICH_AVAILABLE and not config.get('no_color', False):
        table = Table(title="📋 Crawl Configuration")
        table.add_column("Setting", style="cyan")
        table.add_column("Value", style="green")
        
        table.add_row("URL", url)
        table.add_row("Mode", config.get('preset', 'Custom'))
        table.add_row("Depth", str(config.get('depth', 2)))
        table.add_row("Browser", "✅" if config.get('browser', False) else "❌")
        table.add_row("Output format", config.get('output_format', 'json'))
        
        console.print(table)
    else:
        print("\n📋 Configuration Summary")
        print("========================")
        print(f"URL: {url}")
        print(f"Mode: {config.get('preset', 'Custom')}")
        print(f"Depth: {config.get('depth', 2)}")
        print(f"Browser: {'Yes' if config.get('browser', False) else 'No'}")
        print(f"Output format: {config.get('output_format', 'json')}")

async def cleanup_tasks(loop):
    """Clean up any pending tasks in the event loop"""
    tasks = [t for t in asyncio.all_tasks(loop) if t is not asyncio.current_task()]
    for task in tasks:
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass
        except Exception as e:
            logging.error(f"Error cleaning up task: {e}")

def run_crawler_sync(crawler, data_exporter, config):
    """Run crawler operations synchronously"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    async def run_crawler():
        try:
            # Setup crawler
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
                memory_limit=config.get('memory_limit', 0),
                cache_manager=config.get('cache_manager')
            )

            if config.get('url'):
                results = await crawler.crawl(config['url'], depth=config.get('depth', 2))
                await data_exporter.export(results, config)
                return results
            return None
        except Exception as e:
            logging.exception("Error during crawl")
            raise
        finally:
            try:
                # First stop any ongoing crawls
                crawler.terminate_crawl = True
                
                # Wait a moment for tasks to notice termination
                await asyncio.sleep(0.5)
                
                # Clean up tasks first
                await cleanup_tasks(loop)
                
                # Then close the crawler (which handles session cleanup)
                await crawler.close()
                
                # Final cleanup
                await crawler.cleanup()
                
            except Exception as e:
                logging.error(f"Error during cleanup: {e}")
                # Try to force close sessions even if cleanup fails
                if hasattr(crawler, 'session') and crawler.session:
                    try:
                        await crawler.session.close()
                    except Exception:
                        pass

    try:
        return loop.run_until_complete(run_crawler())
    except Exception as e:
        logging.exception("Error during crawl operation")
        raise
    finally:
        try:
            # Handle any remaining tasks
            pending = asyncio.all_tasks(loop)
            if pending:
                loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))
            
            # Close any remaining client sessions
            for task in pending:
                if not task.done():
                    task.cancel()
            
            # Final loop cleanup
            loop.run_until_complete(loop.shutdown_asyncgens())
            loop.run_until_complete(loop.shutdown_default_executor())
            
        except Exception as e:
            logging.error(f"Error during final cleanup: {e}")
        finally:
            loop.close()

def main(config=None, log_function=None):
    """Main entry point for both CLI and GUI modes"""
    parser = setup_argument_parser()
    args = parser.parse_args()

    # Start in GUI mode if specified
    if args.gui and GUI_AVAILABLE:
        from Crew4lX64.gui import launch_gui
        launch_gui()
        return

    # Configure logging
    handlers = [logging.StreamHandler()]
    if log_function:
        queue_handler = QueueHandler(log_function)
        handlers.append(queue_handler)

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=handlers,
        force=True
    )

    # Show ASCII art banner
    if config is None or not config.get('quiet', False):
        print(ascii_art)

    # Initialize progress tracking
    spinner = None
    spinner_thread = None
    if config is None or not config.get('quiet', False):
        spinner = ProgressTracker(use_rich=args.rich if config is None else config.get('rich', False))
        spinner.setup()
        spinner_thread = threading.Thread(target=spinner.spin, daemon=True)
        spinner_thread.start()

    try:
        # Get configuration
        if config is None:
            if args.interactive:
                config = get_preset_config(args.preset or 'basic')
            else:
                config = vars(args)

        # Initialize components
        if spinner:
            spinner.update_status("Initializing crawler...")

        crawler = WebCrawler()
        data_exporter = DataExporter()
        cache_manager = CacheManager() if config.get('use_cache', False) else None
        config['cache_manager'] = cache_manager

        # Show configuration summary
        if spinner:
            spinner.update_status("Setting up crawler...")
        show_summary(config, config.get('url', ''))

        # Run crawler
        if spinner:
            spinner.update_status("Running crawler...")
        run_crawler_sync(crawler, data_exporter, config)

        if spinner:
            spinner.update_status("Crawl completed")

    except KeyboardInterrupt:
        logging.info("Crawl interrupted by user")
    except Exception as e:
        logging.exception("An error occurred during the crawl")
    finally:
        if spinner:
            spinner.stop()
            if spinner_thread and spinner_thread.is_alive():
                spinner_thread.join(timeout=1.0)

if __name__ == "__main__":
    main()
