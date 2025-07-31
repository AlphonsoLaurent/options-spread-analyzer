"""Paper trading system - Core classes."""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional
from enum import Enum
import uuid


class OrderStatus(Enum):
    """Order status enumeration."""
    PENDING = "pending"
    FILLED = "filled"
    CANCELLED = "cancelled"


@dataclass
class Portfolio:
    """Portfolio class for paper trading."""
    name: str = "Default Portfolio"
    initial_cash: float = 100000.0
    current_cash: float = 100000.0
    positions: Dict = field(default_factory=dict)
    orders: Dict = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class Order:
    """Order class for paper trading."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    symbol: str = ""
    strategy_type: str = ""
    quantity: int = 1
    price: float = 0.0
    status: OrderStatus = OrderStatus.PENDING
    created_at: datetime = field(default_factory=datetime.now)


class PaperTradingEngine:
    """Paper trading engine for executing orders and managing portfolio."""

    def __init__(self, portfolio: Portfolio):
        """Initialize the trading engine with a portfolio."""
        if portfolio is None:
            raise ValueError("Portfolio cannot be None")

        self.portfolio = portfolio
        self.trade_history: List[Dict] = []

    def place_order(self, order: Order) -> str:
        """Place an order and update portfolio."""
        if order is None:
            return "Invalid order"

        if order.price > self.portfolio.current_cash:
            order.status = OrderStatus.CANCELLED
            return "Insufficient funds"

        # Execute the order
        order.status = OrderStatus.FILLED
        self.portfolio.current_cash -= order.price
        self.portfolio.orders[order.id] = order

        # Record in trade history
        self.trade_history.append({
            'order_id': order.id,
            'timestamp': order.created_at,
            'symbol': order.symbol,
            'price': order.price,
            'strategy_type': order.strategy_type,
            'quantity': order.quantity
        })

        return order.id

    def get_portfolio_value(self) -> float:
        """Get current portfolio value."""
        if self.portfolio is None:
            return 0.0

        return self.portfolio.current_cash

    def get_performance_metrics(self) -> Dict:
        """Get portfolio performance metrics."""
        if self.portfolio is None:
            return {
                'total_value': 0.0,
                'total_return': 0.0,
                'trades_count': 0,
                'available_cash': 0.0
            }

        try:
            total_value = self.get_portfolio_value()
            total_return = (total_value - self.portfolio.initial_cash) / self.portfolio.initial_cash

            return {
                'total_value': total_value,
                'total_return': total_return * 100,
                'trades_count': len(self.trade_history),
                'available_cash': self.portfolio.current_cash
            }
        except (ZeroDivisionError, AttributeError):
            return {
                'total_value': self.portfolio.current_cash if self.portfolio else 0.0,
                'total_return': 0.0,
                'trades_count': len(self.trade_history),
                'available_cash': self.portfolio.current_cash if self.portfolio else 0.0
            }
