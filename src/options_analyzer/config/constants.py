"""Application constants."""
from enum import Enum
from typing import Dict, List

class OptionType(Enum):
    CALL = "call"
    PUT = "put"

class StrategyType(Enum):
    BULL_CALL_SPREAD = "bull_call_spread"
    BEAR_PUT_SPREAD = "bear_put_spread"
    IRON_CONDOR = "iron_condor"
    BUTTERFLY_SPREAD = "butterfly_spread"

POPULAR_SYMBOLS: List[str] = ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA', 'NVDA', 'META', 'NFLX', 'SPY', 'QQQ', 'VST', 'APP', 'PLTR', 'HOOD', 'SCHD', 'VUG', 'AMD']
CHART_COLORS: Dict[str, str] = {'profit': '#00C851', 'loss': '#FF4444', 'breakeven': '#FFA500', 'current_price': '#2196F3'}
GREEKS_CONFIG: Dict[str, float] = {'risk_free_rate': 0.05, 'dividend_yield': 0.0}
