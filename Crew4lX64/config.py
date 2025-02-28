import json
import logging
import os

def load_config(config_file='crawler_config.json'):
    defaults = {
        'user_agent': 'PythonWebCrawler/1.0',
        'rate_limit': 1.0,
        'respect_robots': True,
        'max_depth': 2,
        'timeout': 30,
        'allow_cookies': False,
        'follow_redirects': True,
        'max_redirects': 5,
        'max_retries': 3,
        'headers': {
            'Accept': 'text/html,application/xhtml+xml,application/xml',
            'Accept-Language': 'en-US,en;q=0.9',
            'DNT': '1'
        }
    }

    try:
        if os.path.exists(config_file):
            with open(config_file, 'r') as f:
                config = json.load(f)
                for key, value in defaults.items():
                    if key not in config:
                        config[key] = value
                return config
    except Exception as e:
        logging.warning(f"Failed to load config: {e}")

    return defaults
