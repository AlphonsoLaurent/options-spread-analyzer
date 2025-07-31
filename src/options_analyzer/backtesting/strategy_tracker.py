"""
Strategy Tracker - Monitors active strategies and updates their status
"""

import time
import threading
from datetime import datetime, timedelta
from typing import List, Optional, Callable
import uuid

from .models import BacktestStrategy, StrategyStatus, StrategyResult
from .results_manager import ResultsManager

class StrategyTracker:
    """Tracks and monitors active strategies"""
    
    def __init__(self, results_manager: ResultsManager):
        self.results_manager = results_manager
        self.active_strategies: List[BacktestStrategy] = []
        self.monitoring = False
        self.monitor_thread = None
        self.callbacks = []
        
    def add_strategy(self, strategy: BacktestStrategy) -> bool:
        """Add a new strategy to track"""
        try:
            # Save to database
            if self.results_manager.save_strategy(strategy):
                # Add to active list
                self.active_strategies.append(strategy)
                return True
            return False
        except Exception as e:
            print(f"Error adding strategy: {e}")
            return False
    
    def remove_strategy(self, strategy_id: str) -> bool:
        """Remove a strategy from tracking"""
        try:
            # Remove from active list
            self.active_strategies = [s for s in self.active_strategies if s.id != strategy_id]
            return True
        except Exception as e:
            print(f"Error removing strategy: {e}")
            return False
    
    def get_active_strategies(self) -> List[BacktestStrategy]:
        """Get all currently active strategies"""
        return self.active_strategies.copy()
    
    def get_expired_strategies(self) -> List[BacktestStrategy]:
        """Get strategies that have expired"""
        now = datetime.now()
        expired = []
        
        for strategy in self.active_strategies:
            if strategy.expiration_date <= now:
                expired.append(strategy)
        
        return expired
    
    def update_strategy_status(self, strategy_id: str, status: StrategyStatus) -> bool:
        """Update strategy status"""
        try:
            # Update in active list
            for strategy in self.active_strategies:
                if strategy.id == strategy_id:
                    strategy.status = status
                    break
            
            # Update in database
            strategy = self.results_manager.get_strategy(strategy_id)
            if strategy:
                strategy.status = status
                return self.results_manager.save_strategy(strategy)
            
            return False
        except Exception as e:
            print(f"Error updating strategy status: {e}")
            return False
    
    def calculate_strategy_result(self, strategy: BacktestStrategy, current_price: float) -> tuple:
        """Calculate the result of a strategy based on current price"""
        try:
            # Calculate P&L based on strategy type
            if strategy.strategy_name == "Call Debit Spread":
                # For call debit spread: profit if price > upper_strike, loss if price < lower_strike
                if current_price >= strategy.upper_strike:
                    # Max profit
                    pnl = strategy.max_profit
                    result = StrategyResult.PROFIT
                    reason = "Price above upper strike - max profit"
                elif current_price <= strategy.lower_strike:
                    # Max loss
                    pnl = -strategy.max_loss
                    result = StrategyResult.LOSS
                    reason = "Price below lower strike - max loss"
                else:
                    # Between strikes - calculate actual P&L
                    intrinsic_value = current_price - strategy.lower_strike
                    pnl = (intrinsic_value - strategy.initial_cost) * strategy.contracts
                    if pnl > 0:
                        result = StrategyResult.PROFIT
                        reason = "Price between strikes - partial profit"
                    elif pnl < 0:
                        result = StrategyResult.LOSS
                        reason = "Price between strikes - partial loss"
                    else:
                        result = StrategyResult.BREAKEVEN
                        reason = "Price at breakeven point"
            
            elif strategy.strategy_name == "Put Debit Spread":
                # For put debit spread: profit if price < lower_strike, loss if price > upper_strike
                if current_price <= strategy.lower_strike:
                    # Max profit
                    pnl = strategy.max_profit
                    result = StrategyResult.PROFIT
                    reason = "Price below lower strike - max profit"
                elif current_price >= strategy.upper_strike:
                    # Max loss
                    pnl = -strategy.max_loss
                    result = StrategyResult.LOSS
                    reason = "Price above upper strike - max loss"
                else:
                    # Between strikes - calculate actual P&L
                    intrinsic_value = strategy.upper_strike - current_price
                    pnl = (intrinsic_value - strategy.initial_cost) * strategy.contracts
                    if pnl > 0:
                        result = StrategyResult.PROFIT
                        reason = "Price between strikes - partial profit"
                    elif pnl < 0:
                        result = StrategyResult.LOSS
                        reason = "Price between strikes - partial loss"
                    else:
                        result = StrategyResult.BREAKEVEN
                        reason = "Price at breakeven point"
            
            else:
                # Unknown strategy type
                pnl = 0
                result = StrategyResult.BREAKEVEN
                reason = "Unknown strategy type"
            
            return pnl, result, reason
            
        except Exception as e:
            print(f"Error calculating strategy result: {e}")
            return 0, StrategyResult.BREAKEVEN, "Calculation error"
    
    def process_expired_strategies(self, get_current_price_func: Callable[[str], float]) -> List[BacktestStrategy]:
        """Process expired strategies and calculate final results"""
        expired_strategies = self.get_expired_strategies()
        processed = []
        
        for strategy in expired_strategies:
            try:
                # Get current price
                current_price = get_current_price_func(strategy.symbol)
                
                # Calculate final result
                final_pnl, result, reason = self.calculate_strategy_result(strategy, current_price)
                
                # Update strategy with results
                strategy.exit_price = current_price
                strategy.exit_date = datetime.now()
                strategy.final_pnl = final_pnl
                strategy.result = result
                strategy.exit_reason = reason
                strategy.status = StrategyStatus.COMPLETED
                
                # Save to database
                if self.results_manager.update_strategy_result(
                    strategy.id, current_price, datetime.now(), 
                    final_pnl, result, reason
                ):
                    processed.append(strategy)
                    # Remove from active list
                    self.remove_strategy(strategy.id)
                
            except Exception as e:
                print(f"Error processing expired strategy {strategy.id}: {e}")
        
        return processed
    
    def start_monitoring(self, check_interval: int = 3600, 
                        get_current_price_func: Callable[[str], float] = None):
        """Start monitoring active strategies"""
        if self.monitoring:
            return
        
        self.monitoring = True
        self.monitor_thread = threading.Thread(
            target=self._monitor_loop,
            args=(check_interval, get_current_price_func),
            daemon=True
        )
        self.monitor_thread.start()
    
    def stop_monitoring(self):
        """Stop monitoring active strategies"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
    
    def _monitor_loop(self, check_interval: int, get_current_price_func: Callable[[str], float]):
        """Main monitoring loop"""
        while self.monitoring:
            try:
                # Process expired strategies
                if get_current_price_func:
                    processed = self.process_expired_strategies(get_current_price_func)
                    
                    # Notify callbacks
                    for callback in self.callbacks:
                        try:
                            callback(processed)
                        except Exception as e:
                            print(f"Error in callback: {e}")
                
                # Sleep for check interval
                time.sleep(check_interval)
                
            except Exception as e:
                print(f"Error in monitoring loop: {e}")
                time.sleep(60)  # Wait 1 minute before retrying
    
    def add_callback(self, callback: Callable[[List[BacktestStrategy]], None]):
        """Add a callback function to be called when strategies are processed"""
        self.callbacks.append(callback)
    
    def remove_callback(self, callback: Callable[[List[BacktestStrategy]], None]):
        """Remove a callback function"""
        if callback in self.callbacks:
            self.callbacks.remove(callback)
    
    def load_active_strategies(self):
        """Load active strategies from database"""
        try:
            active_strategies = self.results_manager.get_active_strategies()
            self.active_strategies = active_strategies
            return len(active_strategies)
        except Exception as e:
            print(f"Error loading active strategies: {e}")
            return 0 