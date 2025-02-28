import re
import logging
import requests
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser

class SecurityManager:
    def __init__(self):
        self.robot_parsers = {}
        self.banned_patterns = [
            r'\.htaccess',
            r'\.env',
            r'wp-config\.php',
            r'config\.php',
            r'administrator',
            r'wp-admin',
            r'phpmyadmin'
        ]
    def sanitize_url(self, url):
        parsed = urlparse(url)
        hostname = parsed.netloc.lower()
        
        # Block access to internal networks
        if (hostname in ('localhost', '127.0.0.1', '::1') or 
            hostname.startswith(('192.168.', '10.', '172.16.', '169.254.', 'fc00:', 'fe80:'))):
            raise ValueError("Access to local/internal networks not allowed")

        if parsed.scheme not in ('http', 'https'):
            raise ValueError("Only HTTP and HTTPS URLs are supported")

        # Check for restricted patterns
        path = parsed.path.lower()
        for pattern in self.banned_patterns:
            if re.search(pattern, path):
                raise ValueError(f"Access to restricted path pattern: {pattern}")

        # Validate hostname format
        if not re.match(r'^[a-zA-Z0-9-]+(\.[a-zA-Z0-9-]+)*\.[a-zA-Z]{2,}$', hostname):
            raise ValueError("Invalid hostname format")

        return url

    def check_robots_txt(self, url, user_agent):
        parsed = urlparse(url)
        robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
        
        if robots_url not in self.robot_parsers:
            rp = RobotFileParser()
            rp.set_url(robots_url)
            try:
                response = requests.get(robots_url, timeout=5)
                rp.parse(response.text.splitlines())
            except:
                rp.allow_all = True
            self.robot_parsers[robots_url] = rp
        
        return self.robot_parsers[robots_url].can_fetch(user_agent, url)

    def redact_sensitive_data(self, data):
        patterns = {
            'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            'phone': r'\b(\+\d{1,2}\s?)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}\b',
            'ssn': r'\b\d{3}-\d{2}-\d{4}\b',
            'credit_card': r'\b(?:\d{4}[ -]?){3}\d{4}\b',
            'password': r'(?i)password\s*[=:]\s*\S+',
            'api_key': r'(?i)(api[_-]?key|access[_-]?token)[=:]\s*[\w\-]+',
            'private_key': r'-----BEGIN (?:RSA )?PRIVATE KEY-----.*?-----END (?:RSA )?PRIVATE KEY-----',
            'jwt': r'eyJ[A-Za-z0-9-_=]+\.[A-Za-z0-9-_=]+\.?[A-Za-z0-9-_.+/=]*'
        }

        if isinstance(data, dict):
            return {k: SecurityManager.redact_sensitive_data(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [SecurityManager.redact_sensitive_data(item) for item in data]
        elif isinstance(data, str):
            text = data
            for name, pattern in patterns.items():
                text = re.sub(pattern, f"[REDACTED_{name.upper()}]", text)
            return text
        else:
            return data
