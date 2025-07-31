"""Options strategies implementation."""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Dict, Optional
from enum import Enum
import numpy as np

class OptionType(Enum):
    CALL = "call"
    PUT = "put"

class StrategyType(Enum):
    CALL_DEBIT_SPREAD = "call_debit_spread"      # Bullish
    CALL_CREDIT_SPREAD = "call_credit_spread"    # Bearish
    PUT_DEBIT_SPREAD = "put_debit_spread"        # Bearish
    PUT_CREDIT_SPREAD = "put_credit_spread"      # Bullish

@dataclass
class OptionLeg:
    option_type: OptionType
    strike: float
    premium: float
    quantity: int
    expiration: str

@dataclass
class StrategyResult:
    breakeven_points: List[float]
    max_profit: float
    max_loss: float
    profit_probability: float
    payoff_at_expiration: Dict[float, float]
    strategy_name: str

class OptionsStrategy(ABC):
    def __init__(self, underlying_price: float, strategy_name: str = ""):
        self.underlying_price = underlying_price
        self.strategy_name = strategy_name
        self.legs: List[OptionLeg] = []
    
    @abstractmethod
    def add_legs(self, **kwargs) -> None:
        pass
    
    @abstractmethod
    def calculate_payoff(self, spot_prices: np.ndarray) -> np.ndarray:
        pass
    
    def analyze(self) -> StrategyResult:
        spot_range = np.linspace(self.underlying_price * 0.7, self.underlying_price * 1.3, 100)
        payoffs = self.calculate_payoff(spot_range)
        
        return StrategyResult(
            breakeven_points=self._find_breakevens(spot_range, payoffs),
            max_profit=np.max(payoffs),
            max_loss=np.min(payoffs),
            profit_probability=self._calc_profit_prob(payoffs),
            payoff_at_expiration=dict(zip(spot_range, payoffs)),
            strategy_name=self.strategy_name
        )
    
    def _find_breakevens(self, prices: np.ndarray, payoffs: np.ndarray) -> List[float]:
        breakevens = []
        for i in range(len(payoffs) - 1):
            if payoffs[i] * payoffs[i + 1] < 0:
                breakeven = prices[i] - payoffs[i] * (prices[i + 1] - prices[i]) / (payoffs[i + 1] - payoffs[i])
                breakevens.append(round(breakeven, 2))
        return breakevens
    
    def _calc_profit_prob(self, payoffs: np.ndarray) -> float:
        return np.sum(payoffs > 0) / len(payoffs) if len(payoffs) > 0 else 0.0

class CallDebitSpread(OptionsStrategy):
    """Call Debit Spread - Bullish strategy (Long Call + Short Call)"""
    def __init__(self, underlying_price: float):
        super().__init__(underlying_price, "Call Debit Spread (Bullish)")
    
    def add_legs(self, lower_strike: float, upper_strike: float,
                 lower_premium: float, upper_premium: float, expiration: str) -> None:
        self.legs = [
            OptionLeg(OptionType.CALL, lower_strike, lower_premium, 1, expiration),  # Long Call
            OptionLeg(OptionType.CALL, upper_strike, upper_premium, -1, expiration)  # Short Call
        ]
    
    def calculate_payoff(self, spot_prices: np.ndarray) -> np.ndarray:
        long_call = self.legs[0]
        short_call = self.legs[1]
        
        long_payoff = np.maximum(spot_prices - long_call.strike, 0)
        short_payoff = -np.maximum(spot_prices - short_call.strike, 0)
        net_debit = long_call.premium - short_call.premium
        
        return long_payoff + short_payoff - net_debit

class CallCreditSpread(OptionsStrategy):
    """Call Credit Spread - Bearish strategy (Short Call + Long Call)"""
    def __init__(self, underlying_price: float):
        super().__init__(underlying_price, "Call Credit Spread (Bearish)")
    
    def add_legs(self, lower_strike: float, upper_strike: float,
                 lower_premium: float, upper_premium: float, expiration: str) -> None:
        self.legs = [
            OptionLeg(OptionType.CALL, lower_strike, lower_premium, -1, expiration),  # Short Call
            OptionLeg(OptionType.CALL, upper_strike, upper_premium, 1, expiration)   # Long Call
        ]
    
    def calculate_payoff(self, spot_prices: np.ndarray) -> np.ndarray:
        short_call = self.legs[0]
        long_call = self.legs[1]
        
        short_payoff = -np.maximum(spot_prices - short_call.strike, 0)
        long_payoff = np.maximum(spot_prices - long_call.strike, 0)
        net_credit = short_call.premium - long_call.premium
        
        return short_payoff + long_payoff + net_credit

class PutDebitSpread(OptionsStrategy):
    """Put Debit Spread - Bearish strategy (Long Put + Short Put)"""
    def __init__(self, underlying_price: float):
        super().__init__(underlying_price, "Put Debit Spread (Bearish)")
    
    def add_legs(self, upper_strike: float, lower_strike: float,
                 upper_premium: float, lower_premium: float, expiration: str) -> None:
        self.legs = [
            OptionLeg(OptionType.PUT, upper_strike, upper_premium, 1, expiration),   # Long Put
            OptionLeg(OptionType.PUT, lower_strike, lower_premium, -1, expiration)   # Short Put
        ]
    
    def calculate_payoff(self, spot_prices: np.ndarray) -> np.ndarray:
        long_put = self.legs[0]
        short_put = self.legs[1]
        
        long_payoff = np.maximum(long_put.strike - spot_prices, 0)
        short_payoff = -np.maximum(short_put.strike - spot_prices, 0)
        net_debit = long_put.premium - short_put.premium
        
        return long_payoff + short_payoff - net_debit

class PutCreditSpread(OptionsStrategy):
    """Put Credit Spread - Bullish strategy (Short Put + Long Put)"""
    def __init__(self, underlying_price: float):
        super().__init__(underlying_price, "Put Credit Spread (Bullish)")
    
    def add_legs(self, upper_strike: float, lower_strike: float,
                 upper_premium: float, lower_premium: float, expiration: str) -> None:
        self.legs = [
            OptionLeg(OptionType.PUT, upper_strike, upper_premium, -1, expiration),  # Short Put
            OptionLeg(OptionType.PUT, lower_strike, lower_premium, 1, expiration)   # Long Put
        ]
    
    def calculate_payoff(self, spot_prices: np.ndarray) -> np.ndarray:
        short_put = self.legs[0]
        long_put = self.legs[1]
        
        short_payoff = -np.maximum(short_put.strike - spot_prices, 0)
        long_payoff = np.maximum(long_put.strike - spot_prices, 0)
        net_credit = short_put.premium - long_put.premium
        
        return short_payoff + long_payoff + net_credit

class StrategyFactory:
    @staticmethod
    def create_strategy(strategy_type: StrategyType, underlying_price: float) -> OptionsStrategy:
        strategies = {
            StrategyType.CALL_DEBIT_SPREAD: CallDebitSpread,
            StrategyType.CALL_CREDIT_SPREAD: CallCreditSpread,
            StrategyType.PUT_DEBIT_SPREAD: PutDebitSpread,
            StrategyType.PUT_CREDIT_SPREAD: PutCreditSpread
        }
        
        strategy_class = strategies.get(strategy_type)
        if not strategy_class:
            raise ValueError(f"Strategy not supported: {strategy_type}")
        
        return strategy_class(underlying_price)
