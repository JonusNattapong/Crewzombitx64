import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'  # Suppress TF logging

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
import asyncio
import logging
import warnings

# Suppress specific warnings
warnings.filterwarnings('ignore', category=DeprecationWarning)
warnings.filterwarnings('ignore', message='.*XNNPACK.*')

class BrowserManager:
    def __init__(self, headless=True, wait_time=2.0, auto_scroll=False):
        self.options = Options()
        self.wait_time = wait_time
        self.auto_scroll = auto_scroll
        self.driver = None
        self._setup_options(headless)

    def _setup_options(self, headless):
        # Browser performance options
        self.options.add_argument('--no-sandbox')
        self.options.add_argument('--disable-dev-shm-usage')
        self.options.add_argument('--disable-gpu')
        self.options.add_argument('--disable-software-rasterizer')
        self.options.add_argument('--disable-web-security')
        self.options.add_argument('--allow-running-insecure-content')
        
        # Memory and performance optimization
        self.options.add_argument('--disable-extensions')
        self.options.add_argument('--disable-blink-features=AutomationControlled')
        self.options.add_argument('--disable-infobars')
        self.options.add_argument('--ignore-certificate-errors')
        self.options.add_argument('--disable-notifications')
        self.options.add_argument('--disable-popup-blocking')
        self.options.add_argument('--disable-logging')
        self.options.add_argument('--disable-blink-features')
        self.options.add_argument('--disable-default-apps')
        self.options.add_argument('--no-default-browser-check')
        
        # Memory limits
        self.options.add_argument('--memory-pressure-off')
        self.options.add_argument('--js-flags=--expose-gc')
        self.options.add_argument('--aggressive-cache-discard')
        self.options.add_argument('--disable-cache')
        self.options.add_argument('--disable-application-cache')
        self.options.add_argument('--disable-offline-load-stale-cache')
        
        if headless:
            self.options.add_argument('--headless=new')
            self.options.add_argument('--disable-gpu')
            self.options.add_argument('--window-size=1920,1080')

        # Performance preferences
        self.options.set_preference = {
            'profile.managed_default_content_settings.images': 2,
            'profile.managed_default_content_settings.javascript': 1,
            'profile.managed_default_content_settings.cookies': 1,
            'profile.managed_default_content_settings.plugins': 2,
            'profile.managed_default_content_settings.popups': 2,
            'profile.managed_default_content_settings.geolocation': 2,
            'profile.managed_default_content_settings.media_stream': 2,
        }

    def setup_browser(self):
        """Synchronous setup for compatibility"""
        try:
            if self.driver:
                self.close()

            service = Service()
            self.driver = webdriver.Chrome(options=self.options, service=service)
            self.driver.set_page_load_timeout(30)
            self.driver.set_script_timeout(30)
            return True
        except Exception as e:
            logging.error(f"Failed to setup browser: {str(e)}")
            if self.driver:
                self.driver.quit()
                self.driver = None
            return False

    async def navigate(self, url: str) -> bool:
        """Navigate to URL with retries and error handling"""
        if not self.driver:
            if not self.setup_browser():
                return False

        max_retries = 3
        for attempt in range(max_retries):
            try:
                await asyncio.to_thread(self.driver.get, url)
                await asyncio.sleep(self.wait_time)

                if self.auto_scroll:
                    await self.scroll_page()

                await self._clear_memory()
                return True

            except Exception as e:
                if attempt == max_retries - 1:
                    logging.error(f"Navigation failed after {max_retries} attempts: {str(e)}")
                    return False
                await asyncio.sleep(1 * (attempt + 1))

        return False

    async def scroll_page(self, max_scrolls=10, scroll_pause=0.5):
        """Smooth scrolling with dynamic content loading"""
        if not self.driver:
            return

        try:
            last_height = await asyncio.to_thread(
                self.driver.execute_script,
                "return document.documentElement.scrollHeight"
            )

            for _ in range(max_scrolls):
                # Scroll smoothly
                await asyncio.to_thread(
                    self.driver.execute_script,
                    """
                    window.scrollTo({
                        top: document.documentElement.scrollHeight,
                        behavior: 'smooth'
                    });
                    """
                )
                
                await asyncio.sleep(scroll_pause)

                new_height = await asyncio.to_thread(
                    self.driver.execute_script,
                    "return document.documentElement.scrollHeight"
                )

                if new_height == last_height:
                    break
                    
                last_height = new_height

        except Exception as e:
            logging.warning(f"Error during page scrolling: {str(e)}")

    async def wait_for_element(self, selector: str, timeout: int = 10) -> bool:
        """Wait for element with timeout"""
        if not self.driver:
            return False

        try:
            element = await asyncio.to_thread(
                WebDriverWait(self.driver, timeout).until,
                EC.presence_of_element_located((By.CSS_SELECTOR, selector))
            )
            return bool(element)
        except TimeoutException:
            logging.warning(f"Element not found: {selector}")
            return False
        except Exception as e:
            logging.error(f"Error waiting for element: {str(e)}")
            return False

    async def _clear_memory(self):
        """Clear browser memory"""
        if not self.driver:
            return

        try:
            await asyncio.to_thread(
                self.driver.execute_script,
                """
                window.localStorage.clear();
                window.sessionStorage.clear();
                let cookies = document.cookie.split(";");
                for (let i = 0; i < cookies.length; i++) {
                    let cookie = cookies[i];
                    let eqPos = cookie.indexOf("=");
                    let name = eqPos > -1 ? cookie.substr(0, eqPos) : cookie;
                    document.cookie = name + "=;expires=Thu, 01 Jan 1970 00:00:00 GMT";
                }
                if (window.gc) window.gc();
                """
            )
        except Exception as e:
            logging.warning(f"Error clearing browser memory: {str(e)}")

    def close(self):
        """Close browser and cleanup resources"""
        if self.driver:
            try:
                self.driver.quit()
            except Exception as e:
                logging.error(f"Error closing browser: {str(e)}")
            finally:
                self.driver = None
