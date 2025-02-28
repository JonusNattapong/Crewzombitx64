import re
import logging
from urllib.parse import urlparse

class SecurityManager:
    @staticmethod
    def sanitize_url(url):
        parsed = urlparse(url)
        hostname = parsed.netloc.lower()
        if hostname in ('localhost', '127.0.0.1', '::1') or hostname.startswith('192.168.') or hostname.startswith('10.'):
            raise ValueError("Access to local/internal networks not allowed")

        if parsed.scheme not in ('http', 'https'):
            raise ValueError("Only HTTP and HTTPS URLs are supported")

        return url

    @staticmethod
    def redact_sensitive_data(data):
        patterns = {
            'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            'phone': r'\b(\+\d{1,2}\s?)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}\b',
            'ssn': r'\b\d{3}-\d{2}-\d{4}\b',
            'credit_card': r'\b(?:\d{4}[ -]?){3}\d{4}\b'
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
