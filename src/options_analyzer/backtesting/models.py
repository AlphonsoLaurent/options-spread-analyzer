"""
Data Models for Backtesting Results
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Any, Optional, List
from enum import Enum

class StrategyStatus(Enum):
    PENDING = "pending"
    ACTIVE = "active"
    COMPLETED = "completed"
    EXPIRED = "expired"

class StrategyResult(Enum):
    PROFIT = "profit"
    LOSS = "loss"
    BREAKEVEN = "breakeven"

@dataclass
class BacktestStrategy:
    """Represents a strategy being backtested"""
    id: str
    symbol: str
    strategy_name: str
    entry_date: datetime
    expiration_date: datetime
    entry_price: float
    lower_strike: float
    upper_strike: float
    lower_premium: float
    upper_premium: float
    contracts: int
    initial_cost: float
    max_profit: float
    max_loss: float
    status: StrategyStatus
    market_analysis: Dict[str, Any]
    created_at: datetime
    
    # Results (filled after completion)
    exit_price: Optional[float] = None
    exit_date: Optional[datetime] = None
    final_pnl: Optional[float] = None
    result: Optional[StrategyResult] = None
    exit_reason: Optional[str] = None
    notes: Optional[str] = None

@dataclass
class PerformanceMetrics:
    """Performance metrics for backtesting results"""
    total_trades: int
    winning_trades: int
    losing_trades: int
    breakeven_trades: int
    win_rate: float
    total_profit: float
    total_loss: float
    net_pnl: float
    average_profit: float
    average_loss: float
    profit_factor: float
    max_drawdown: float
    sharpe_ratio: float
    average_holding_period: float

@dataclass
class BacktestSession:
    """Represents a complete backtesting session"""
    id: str
    name: str
    start_date: datetime
    end_date: datetime
    strategies: List[BacktestStrategy]
    performance: PerformanceMetrics
    settings: Dict[str, Any] 