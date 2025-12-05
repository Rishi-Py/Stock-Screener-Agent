"""
Validators for input data.
"""

import re
from typing import Dict, Any


def validate_symbol(symbol: str) -> bool:
    """
    Validate stock ticker symbol.
    
    Args:
        symbol: Stock ticker symbol
        
    Returns:
        True if valid, False otherwise
    """
    if not symbol or not isinstance(symbol, str):
        return False
    
    # Basic validation: 1-5 uppercase letters only
    # Lowercase is considered invalid to enforce proper formatting
    pattern = r'^[A-Z]{1,5}$'
    return bool(re.match(pattern, symbol))


def validate_screening_config(config: Dict[str, Any]) -> bool:
    """
    Validate screening configuration.
    
    Args:
        config: Configuration dictionary
        
    Returns:
        True if valid, raises ValueError otherwise
    """
    if not isinstance(config, dict):
        raise ValueError("Config must be a dictionary")
    
    # Validate numeric parameters
    numeric_params = {
        'min_market_cap': (0, float('inf')),
        'max_pe_ratio': (0, 1000),
        'min_revenue_growth': (-1, 10),
        'min_earnings_growth': (-1, 10)
    }
    
    for param, (min_val, max_val) in numeric_params.items():
        if param in config:
            value = config[param]
            if not isinstance(value, (int, float)):
                raise ValueError(f"{param} must be a number")
            if not min_val <= value <= max_val:
                raise ValueError(
                    f"{param} must be between {min_val} and {max_val}"
                )
    
    return True
