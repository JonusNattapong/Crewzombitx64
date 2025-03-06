import json
import logging
import os
import random
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
import yaml
from pathlib import Path
from datetime import datetime

@dataclass
class CrawlerConfig:
    """Strongly typed configuration class for the crawler."""
    # Basic settings
    user_agent: str
    rate_limit: float
    burst_size: int
    respect_robots: bool
    max_depth: int
    timeout: int
    
    # Security settings
    use_proxies: bool
    min_proxy_score: float
    verify_ssl: bool
    allow_cookies: bool
    secure_cookies_only: bool
    sanitize_inputs: bool
    redact_sensitive_data: bool
    blocked_extensions: List[str]
    max_file_size: int
    
    # Privacy settings
    respect_privacy_policies: bool
    do_not_track: bool
    anonymize_data: bool
    clear_cookies_after: bool
    
    # Request settings
    follow_redirects: bool
    max_redirects: int
    max_retries: int
    retry_delay: int
    headers: Dict[str, str]
    
    # Rate limiting
    domain_specific_delays: Dict[str, float]
    adaptive_rate_limiting: bool
    backoff_factor: float
    max_backoff: int
    
    # Legal compliance
    respect_terms_of_service: bool
    check_robots_txt: bool
    honor_nofollow: bool
    max_requests_per_domain: int
    blocked_countries: List[str]
    
    # Error handling
    log_level: str
    save_errors: bool
    error_dir: str
    max_error_rate: float

def _validate_config(config: Dict[str, Any]) -> None:
    """Validate configuration values and types."""
    validation_rules = {
        'rate_limit': (lambda x: 0.1 <= float(x) <= 10.0, "Rate limit must be between 0.1 and 10.0"),
        'max_depth': (lambda x: 1 <= int(x) <= 10, "Max depth must be between 1 and 10"),
        'timeout': (lambda x: 1 <= int(x) <= 60, "Timeout must be between 1 and 60 seconds"),
        'min_proxy_score': (lambda x: 0.0 <= float(x) <= 1.0, "Proxy score must be between 0.0 and 1.0"),
        'max_error_rate': (lambda x: 0.0 <= float(x) <= 1.0, "Error rate must be between 0.0 and 1.0"),
        'burst_size': (lambda x: 1 <= int(x) <= 10, "Burst size must be between 1 and 10"),
        'max_redirects': (lambda x: 0 <= int(x) <= 10, "Max redirects must be between 0 and 10"),
        'max_retries': (lambda x: 0 <= int(x) <= 5, "Max retries must be between 0 and 5")
    }

    for key, (validator, message) in validation_rules.items():
        if key in config:
            try:
                if not validator(config[key]):
                    raise ValueError(f"Invalid {key}: {message}")
            except Exception as e:
                raise ValueError(f"Validation error for {key}: {str(e)}")

def _load_env_config() -> Dict[str, Any]:
    """Load configuration from environment variables."""
    env_prefix = "CRAWLER_"
    env_config = {}
    
    for key in os.environ:
        if key.startswith(env_prefix):
            config_key = key[len(env_prefix):].lower()
            value = os.environ[key]
            
            # Convert boolean strings
            if value.lower() in ('true', 'false'):
                value = value.lower() == 'true'
            # Convert numeric strings
            elif value.replace('.', '').isdigit():
                value = float(value) if '.' in value else int(value)
            # Convert JSON/YAML strings
            elif value.startswith('{') or value.startswith('['):
                try:
                    value = json.loads(value)
                except json.JSONDecodeError:
                    try:
                        value = yaml.safe_load(value)
                    except yaml.YAMLError:
                        logging.warning(f"Failed to parse complex value for {key}")
                        continue
                
            env_config[config_key] = value
    
    return env_config

def get_default_config() -> Dict[str, Any]:
    """Get default configuration values."""
    return {
        # Basic settings
        'user_agent': _get_random_user_agent(),
        'rate_limit': 1.0,
        'burst_size': 3,
        'respect_robots': True,
        'max_depth': 1,
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

def _merge_configs(defaults: Dict[str, Any], user_config: Dict[str, Any]) -> Dict[str, Any]:
    """Merge user config with defaults, validating and sanitizing values."""
    config = defaults.copy()
    
    for key, value in user_config.items():
        if key not in defaults:
            logging.warning(f"Unknown configuration option: {key}")
            continue
            
        if isinstance(value, dict) and isinstance(defaults[key], dict):
            config[key] = _merge_configs(defaults[key], value)
        else:
            config[key] = value
    
    return config

def _get_random_user_agent() -> str:
    """Return a random realistic user agent string."""
    # Load user agents from file if available
    user_agents_file = Path(__file__).parent / 'user_agents.txt'
    try:
        if user_agents_file.exists():
            with open(user_agents_file, 'r') as f:
                user_agents = [line.strip() for line in f if line.strip()]
        else:
            # Fallback to default user agents
            user_agents = [
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15',
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 Edg/91.0.864.59',
                'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            ]
    except Exception as e:
        logging.warning(f"Failed to load user agents file: {e}")
        # Fallback to default Chrome user agent
        user_agents = ['Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36']
    
    return random.choice(user_agents)

def load_config(config_file: str = 'crawler_config.json') -> CrawlerConfig:
    """Load and validate configuration from multiple sources."""
    # Get base configuration
    config = get_default_config()
    
    # Load from config file if it exists
    try:
        if os.path.exists(config_file):
            with open(config_file, 'r') as f:
                if config_file.endswith('.json'):
                    file_config = json.load(f)
                elif config_file.endswith('.yaml') or config_file.endswith('.yml'):
                    file_config = yaml.safe_load(f)
                else:
                    raise ValueError("Unsupported config file format")
                config = _merge_configs(config, file_config)
    except Exception as e:
        logging.warning(f"Failed to load config file: {e}")

    # Override with environment variables
    env_config = _load_env_config()
    if env_config:
        config = _merge_configs(config, env_config)

    # Validate final configuration
    _validate_config(config)
    
    # Convert to CrawlerConfig object
    try:
        return CrawlerConfig(**config)
    except Exception as e:
        logging.error(f"Failed to create CrawlerConfig object: {e}")
        raise
