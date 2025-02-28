from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import asyncio
import os
import logging

class BrowserManager:
    def __init__(self, headless=True):
        self.options = Options()
        if headless:
            self.options.add_argument('--headless')
        self.options.add_argument('--no-sandbox')
        self.options.add_argument('--disable-dev-shm-usage')
        self.driver = None
        self._setup_options()

    def _setup_options(self):
        self.options.add_argument('--disable-gpu')
        self.options.add_argument('--disable-software-rasterizer')
        self.options.add_argument('--disable-dev-shm-usage')
        self.options.add_argument('--disable-web-security')
        self.options.add_argument('--allow-running-insecure-content')

        cert_path = os.getenv('CUSTOM_CERT_PATH')
        if cert_path:
            self.options.add_argument(f'--ignore-certificate-errors-spki-list={cert_path}')

    def setup_browser(self, proxy=None, user_agent=None):
        if proxy:
            if isinstance(proxy, dict):
                auth_proxy = f"{proxy['username']}:{proxy['password']}@{proxy['host']}:{proxy['port']}"
                self.options.add_argument(f'--proxy-server={auth_proxy}')
            else:
                self.options.add_argument(f'--proxy-server={proxy}')

        if user_agent:
            self.options.add_argument(f'--user-agent={user_agent}')

        self.driver = webdriver.Chrome(options=self.options)
        return self.driver

    def adjust_viewport(self):
        if self.driver:
            total_height = self.driver.execute_script("""
                return Math.max(
                    document.body.scrollHeight,
                    document.documentElement.scrollHeight,
                    document.body.offsetHeight,
                    document.documentElement.offsetHeight,
                    document.body.clientHeight,
                    document.documentElement.clientHeight
                );
            """)

            width = self.driver.execute_script("""
                return Math.max(
                    document.body.scrollWidth,
                    document.documentElement.scrollWidth,
                    document.body.offsetWidth,
                    document.documentElement.offsetWidth,
                    document.body.clientWidth,
                    document.documentElement.clientWidth
                );
            """)

            self.driver.set_window_size(width, total_height)

    async def wait_for_element(self, selector: str, timeout: int = 10):
        if not self.driver:
            return None

        try:
            return await asyncio.to_thread(
                WebDriverWait(self.driver, timeout).until,
                EC.presence_of_element_located((By.CSS_SELECTOR, selector))
            )
        except TimeoutException:
            logging.warning(f"Element not found: {selector}")
            return None
        except Exception as e:
            logging.error(f"Error waiting for element: {str(e)}")
            return None
