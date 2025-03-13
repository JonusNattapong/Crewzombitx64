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
import psutil
import sys

# Suppress specific warnings
warnings.filterwarnings('ignore', category=DeprecationWarning)
warnings.filterwarnings('ignore', message='.*XNNPACK.*')

class BrowserManager:
    def __init__(self, headless=True, wait_time=2.0, auto_scroll=False, memory_limit=None):
        self.options = Options()
        self.wait_time = wait_time
        self.auto_scroll = auto_scroll
        self.driver = None
        self.memory_limit = memory_limit  # Memory limit in MB
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
        
        # Improved performance for headless mode
        if headless:
            self.options.add_argument('--headless=new')
            self.options.add_argument('--disable-gpu')
            self.options.add_argument('--window-size=1920,1080')
            
        # Add profile preferences for better performance
        prefs = {
            'profile.managed_default_content_settings.images': 2,  # Don't load images by default
            'profile.default_content_setting_values.notifications': 2,  # Block notifications
            'profile.managed_default_content_settings.plugins': 2,  # Disable plugins
            'profile.managed_default_content_settings.popups': 2,  # Block popups
            'profile.managed_default_content_settings.geolocation': 2,  # Block geolocation
            'profile.managed_default_content_settings.media_stream': 2,  # Block media streaming
            'disk-cache-size': 4096,  # Limit disk cache to 4MB
            'profile.default_content_setting_values.cookies': 1  # Allow cookies
        }
        self.options.add_experimental_option('prefs', prefs)

        # Add performance logging
        self.options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})

    def setup_browser(self):
        """Synchronous setup for compatibility with improved error handling"""
        try:
            if self.driver:
                self.close()

            service = Service()
            self.driver = webdriver.Chrome(options=self.options, service=service)
            self.driver.set_page_load_timeout(30)
            self.driver.set_script_timeout(30)
            logging.info("Browser setup successful")
            return True
        except Exception as e:
            logging.error(f"Failed to setup browser: {str(e)}")
            if "chromedriver" in str(e).lower() and "executable" in str(e).lower():
                logging.error("ChromeDriver not found. Please install ChromeDriver or add it to PATH")
                print("❌ ChromeDriver not found. Please install Chrome or add ChromeDriver to your PATH")
            if self.driver:
                self.driver.quit()
                self.driver = None
            return False

    async def navigate(self, url: str) -> bool:
        """Navigate to URL with retries and improved error handling"""
        if not self.driver:
            logging.error("Browser not initialized")
            return False

        max_retries = 3
        for attempt in range(1, max_retries + 1):
            try:
                await asyncio.to_thread(self.driver.get, url)
                
                # Monitor memory usage and perform cleanup if needed
                if self.memory_limit:
                    process = psutil.Process()
                    memory_usage = process.memory_info().rss / (1024 * 1024)  # Convert to MB
                    if memory_usage > self.memory_limit:
                        logging.warning(f"Memory usage ({memory_usage:.1f}MB) exceeded limit ({self.memory_limit}MB). Cleaning up...")
                        await self._clear_memory()
                
                if self.auto_scroll:
                    await self.scroll_page()
                    
                return True
            except Exception as e:
                if "ERR_TIMED_OUT" in str(e) or "timeout" in str(e).lower():
                    error_msg = f"Page load timeout (attempt {attempt}/{max_retries})"
                elif "ERR_CONNECTION_REFUSED" in str(e):
                    error_msg = f"Connection refused (attempt {attempt}/{max_retries})"
                else:
                    error_msg = f"Navigation error: {str(e)} (attempt {attempt}/{max_retries})"
                
                logging.warning(error_msg)
                
                if attempt < max_retries:
                    wait_time = attempt * 2  # Exponential backoff
                    await asyncio.sleep(wait_time)
                    await self._clear_memory()  # Clear memory before retry
                else:
                    logging.error(f"Failed to navigate to {url} after {max_retries} attempts")
                    return False
        
        return False

    async def scroll_page(self, max_scrolls=10, scroll_pause=0.5):
        """Smooth scrolling with dynamic content loading and enhanced feedback"""
        if not self.driver:
            return

        try:
            last_height = await asyncio.to_thread(
                self.driver.execute_script,
                "return document.documentElement.scrollHeight"
            )

            # Get visible height
            visible_height = await asyncio.to_thread(
                self.driver.execute_script,
                "return window.innerHeight"
            )
            
            # Calculate total scrolls needed to reach bottom
            total_scrolls = min(max_scrolls, (last_height // visible_height) + 1)
            
            for i in range(total_scrolls):
                # Calculate progressive scroll position
                scroll_position = ((i + 1) / total_scrolls) * last_height
                
                # Scroll smoothly to position
                await asyncio.to_thread(
                    self.driver.execute_script,
                    f"""
                    window.scrollTo({{
                        top: {scroll_position},
                        behavior: 'smooth'
                    }});
                    """
                )
                
                # Let content load
                await asyncio.sleep(scroll_pause)

                # Get new height
                new_height = await asyncio.to_thread(
                    self.driver.execute_script,
                    "return document.documentElement.scrollHeight"
                )

                # If height changed, adjust total scrolls
                if new_height > last_height:
                    new_total_scrolls = min(max_scrolls, (new_height // visible_height) + 1)
                    if new_total_scrolls > total_scrolls:
                        total_scrolls = new_total_scrolls
                        
                last_height = new_height

            # Try to load any lazy-loaded images by scrolling back to top
            await asyncio.to_thread(
                self.driver.execute_script,
                "window.scrollTo(0, 0);"
            )

        except Exception as e:
            logging.warning(f"Error during page scrolling: {str(e)}")

    async def wait_for_element(self, selector: str, timeout: int = 10) -> bool:
        """Wait for element with timeout and improved error reporting"""
        if not self.driver:
            return False

        try:
            element = await asyncio.to_thread(
                WebDriverWait(self.driver, timeout).until,
                EC.presence_of_element_located((By.CSS_SELECTOR, selector))
            )
            return bool(element)
        except TimeoutException:
            logging.warning(f"Element not found within {timeout}s: {selector}")
            return False
        except Exception as e:
            logging.error(f"Error waiting for element {selector}: {str(e)}")
            return False

    async def _clear_memory(self):
        """Clear browser memory with improved cleanup"""
        if not self.driver:
            return

        try:
            # Clear local and session storage
            await asyncio.to_thread(
                self.driver.execute_script,
                """
                try {
                    window.localStorage.clear();
                    window.sessionStorage.clear();
                    
                    // Clear cookies
                    let cookies = document.cookie.split(";");
                    for (let i = 0; i < cookies.length; i++) {
                        let cookie = cookies[i];
                        let eqPos = cookie.indexOf("=");
                        let name = eqPos > -1 ? cookie.substr(0, eqPos) : cookie;
                        document.cookie = name + "=;expires=Thu, 01 Jan 1970 00:00:00 GMT";
                    }
                    
                    // Clear cache
                    if ('caches' in window) {
                        caches.keys().then(function(keyList) {
                            return Promise.all(keyList.map(function(key) {
                                return caches.delete(key);
                            }));
                        });
                    }
                    
                    // Force garbage collection if available
                    if (window.gc) window.gc();
                    
                    // Reset unused variables
                    const variables = Object.keys(window);
                    for (let i = 0; i < variables.length; i++) {
                        try {
                            if (typeof window[variables[i]] === 'object' && 
                                window[variables[i]] !== null && 
                                !window[variables[i]]._isSystemObject) {
                                window[variables[i]] = null;
                            }
                        } catch (e) {
                            // Ignore errors for read-only properties
                        }
                    }
                    
                    return true;
                } catch (e) {
                    return false;
                }
                """
            )
            
            # Clear browser console logs
            if hasattr(self.driver, 'get_log'):
                await asyncio.to_thread(lambda: self.driver.get_log('browser'))
                
        except Exception as e:
            logging.warning(f"Error during memory cleanup: {str(e)}")

    def close(self):
        """Close browser and cleanup resources with improved error handling"""
        if self.driver:
            try:
                # Try to clear memory first
                try:
                    self.driver.execute_script(
                        "window.localStorage.clear(); window.sessionStorage.clear(); if(window.gc) window.gc();"
                    )
                except:
                    pass
                    
                # Close and quit the browser
                self.driver.quit()
                logging.info("Browser closed successfully")
            except Exception as e:
                logging.error(f"Error closing browser: {str(e)}")
            finally:
                self.driver = None
