"""
Options Analyzer Package

A comprehensive toolkit for options trading analysis and paper trading.
"""

__version__ = "0.1.0"
__author__ = "Options Analyzer Team"

# Package information
__all__ = [
    "__version__",
    "__author__",
]

# Optional imports - only load when explicitly requested
def get_settings():
    """Lazy load settings to avoid import errors."""
    try:
        #from .config.settings import Settings
        return Settings()
    except ImportError as e:
        print(f"Warning: Could not load settings - {e}")
        return None

def get_core_classes():
    """Lazy load core trading classes."""
    try:
        from .core.paper_trading import Portfolio, Order, PaperTradingEngine
        return Portfolio, Order, PaperTradingEngine
    except ImportError as e:
        print(f"Warning: Could not load core classes - {e}")
        return None, None, None

# Remove automatic imports to prevent dependency issues
# Comment out these lines that were causing the problem:
# from .config.settings import Settings  # This was causing the pydantic error
