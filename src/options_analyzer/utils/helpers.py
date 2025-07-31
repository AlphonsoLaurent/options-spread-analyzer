"""Helper utilities."""
import re
from typing import Union
from datetime import datetime, date

def format_currency(amount: float, currency: str = "USD") -> str:
    if currency == "USD":
        return f"${amount:,.2f}"
    return f"{amount:,.2f} {currency}"

def format_percentage(value: float, decimals: int = 2) -> str:
    return f"{value * 100:.{decimals}f}%"

def validate_symbol(symbol: str) -> bool:
    if not symbol:
        return False
    return bool(re.match(r'^[A-Z]{1,5}$', symbol.upper()))

def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    return numerator / denominator if denominator != 0 else default
