import json
import logging
import os
import random

def load_config(config_file='crawler_config.json'):
    defaults = {
        # Basic settings
        'user_agent': _get_random_user_agent(),
        'rate_limit': 1.0,
        'burst_size': 3,
        'respect_robots': True,
        'max_depth': 2,
        'timeout': 30,
        
        # Security settings
        'use_proxies': True,
        'min_proxy_score': 0.7,
        'verify_ssl': True,
        'allow_cookies': False,
        'secure_cookies_only': True,
        'sanitize_inputs': True,
        'redact_sensitive_data': True,
        'blocked_extensions': ['.php', '.asp', '.aspx', '.exe', '.dll', '.bat', '.cmd', '.sh', '.cgi'],
        'max_file_size': 10 * 1024 * 1024,  # 10MB
        
        # Privacy settings
        'respect_privacy_policies': True,
        'do_not_track': True,
        'anonymize_data': True,
        'clear_cookies_after': True,
        
        # Request settings
        'follow_redirects': True,
        'max_redirects': 3,
        'max_retries': 2,
        'retry_delay': 5,
        'headers': {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'DNT': '1',
            'Upgrade-Insecure-Requests': '1'
        },
        
        # Rate limiting
        'domain_specific_delays': {
            'default': 1.0,
            'api_endpoints': 2.0,
            'search_pages': 3.0
        },
        'adaptive_rate_limiting': True,
        'backoff_factor': 1.5,
        'max_backoff': 300,  # 5 minutes
        
        # Legal compliance
        'respect_terms_of_service': True,
        'check_robots_txt': True,
        'honor_nofollow': True,
        'max_requests_per_domain': 1000,
        'blocked_countries': [],  # Add country codes to comply with regional restrictions
        
        # Error handling
        'log_level': 'INFO',
        'save_errors': True,
        'error_dir': 'error_logs',
        'max_error_rate': 0.1  # 10% error threshold
    }

    try:
        if os.path.exists(config_file):
            with open(config_file, 'r') as f:
                config = json.load(f)
                return _merge_configs(defaults, config)
    except Exception as e:
        logging.warning(f"Failed to load config: {e}")

    return defaults

def _merge_configs(defaults, user_config):
    """Merge user config with defaults, validating and sanitizing values."""
    config = defaults.copy()
    
    for key, value in user_config.items():
        if key not in defaults:
            logging.warning(f"Unknown configuration option: {key}")
            continue
            
        if key == 'rate_limit' and value < 0.1:
            logging.warning("Rate limit too aggressive, using minimum of 0.1")
            value = 0.1
        elif key == 'max_depth' and value > 10:
            logging.warning("Max depth too high, capping at 10")
            value = 10
        elif key == 'timeout' and value > 60:
            logging.warning("Timeout too long, capping at 60 seconds")
            value = 60
            
        config[key] = value
    
    return config

def _get_random_user_agent():
    """Return a random realistic user agent string."""
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 Edg/91.0.864.59',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    ]
    return random.choice(user_agents)
