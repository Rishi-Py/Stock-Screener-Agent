"""
Tests for validators.
"""

import pytest
from src.utils.validators import validate_symbol, validate_screening_config


def test_validate_symbol_valid():
    """Test validation of valid symbols."""
    assert validate_symbol("AAPL")
    assert validate_symbol("MSFT")
    assert validate_symbol("GOOGL")
    assert validate_symbol("A")
    assert validate_symbol("AMZN")


def test_validate_symbol_invalid():
    """Test validation of invalid symbols."""
    assert not validate_symbol("")
    assert not validate_symbol("123")
    assert not validate_symbol("WAYTOOLONGSY")  # More than 10 chars
    assert not validate_symbol("abc")
    assert not validate_symbol(None)
    assert not validate_symbol("AA-PL")


def test_validate_screening_config_valid():
    """Test validation of valid configs."""
    config = {
        "min_market_cap": 1000000000,
        "max_pe_ratio": 30,
        "min_revenue_growth": 0.15,
        "min_earnings_growth": 0.10
    }
    assert validate_screening_config(config)


def test_validate_screening_config_partial():
    """Test validation with partial config."""
    config = {"min_market_cap": 1000000000}
    assert validate_screening_config(config)


def test_validate_screening_config_empty():
    """Test validation with empty config."""
    assert validate_screening_config({})


def test_validate_screening_config_invalid_type():
    """Test validation with invalid type."""
    with pytest.raises(ValueError, match="must be a dictionary"):
        validate_screening_config("not a dict")


def test_validate_screening_config_invalid_value():
    """Test validation with invalid numeric value."""
    config = {"min_market_cap": -1}
    with pytest.raises(ValueError):
        validate_screening_config(config)
    
    config = {"max_pe_ratio": 2000}
    with pytest.raises(ValueError):
        validate_screening_config(config)


def test_validate_screening_config_non_numeric():
    """Test validation with non-numeric value."""
    config = {"min_market_cap": "not a number"}
    with pytest.raises(ValueError, match="must be a number"):
        validate_screening_config(config)
