"""Preset configurations for common web crawling scenarios."""
from typing import Dict, Any

PRESET_BASIC: Dict[str, Any] = {
    'max_depth': 1,
    'rate_limit': 1.0,
    'timeout': 30,
    'respect_robots': True,
    'use_proxies': False,
    'follow_redirects': True,
    'save_errors': True
}

PRESET_AGGRESSIVE: Dict[str, Any] = {
    'max_depth': 3,
    'rate_limit': 0.5,
    'burst_size': 5,
    'timeout': 60,
    'respect_robots': True,
    'use_proxies': True,
    'follow_redirects': True,
    'max_retries': 3,
    'adaptive_rate_limiting': True
}

PRESET_STEALTH: Dict[str, Any] = {
    'max_depth': 2,
    'rate_limit': 2.0,
    'timeout': 45,
    'respect_robots': True,
    'use_proxies': True,
    'do_not_track': True,
    'anonymize_data': True,
    'clear_cookies_after': True,
    'adaptive_rate_limiting': True,
    'backoff_factor': 2.0
}

PRESET_API: Dict[str, Any] = {
    'max_depth': 1,
    'rate_limit': 1.0,
    'timeout': 30,
    'respect_robots': False,
    'use_proxies': False,
    'follow_redirects': True,
    'retry_delay': 2,
    'max_retries': 3
}

PRESET_ARCHIVE: Dict[str, Any] = {
    'max_depth': 5,
    'rate_limit': 1.5,
    'timeout': 60,
    'respect_robots': True,
    'use_proxies': False,
    'follow_redirects': True,
    'save_errors': True,
    'max_file_size': 50 * 1024 * 1024  # 50MB
}

def get_preset_config(preset_name: str) -> Dict[str, Any]:
    """Get a preset configuration by name.
    
    Args:
        preset_name: Name of the preset configuration.
                    Valid options: basic, aggressive, stealth, api, archive
                    
    Returns:
        Dictionary containing the preset configuration.
        
    Raises:
        ValueError: If preset_name is not valid.
    """
    presets = {
        'basic': PRESET_BASIC,
        'aggressive': PRESET_AGGRESSIVE, 
        'stealth': PRESET_STEALTH,
        'api': PRESET_API,
        'archive': PRESET_ARCHIVE
    }
    
    preset_name = preset_name.lower()
    if preset_name not in presets:
        raise ValueError(
            f"Invalid preset name. Valid options are: {', '.join(presets.keys())}"
        )
    
    return presets[preset_name]
