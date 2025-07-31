"""
Backtest Engine - Main orchestrator for automated strategy testing
"""

import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Callable, List
import threading
import time

from .models import BacktestStrategy, StrategyStatus, StrategyResult, BacktestSession, PerformanceMetrics
from .results_manager import ResultsManager
from .strategy_tracker import StrategyTracker
from .performance_analyzer import PerformanceAnalyzer

class BacktestEngine:
    """Main engine for automated strategy backtesting"""
    
    def __init__(self, results_manager: ResultsManager = None):
        if results_manager is None:
            results_manager = ResultsManager()
        
        self.results_manager = results_manager
        self.strategy_tracker = StrategyTracker(results_manager)
        self.performance_analyzer = PerformanceAnalyzer(results_manager)
        
        # Engine state
        self.is_running = False
        self.monitoring_thread = None
        self.price_function = None
        
        # Callbacks
        self.on_strategy_completed = None
        self.on_session_completed = None
        
    def start_automated_backtesting(self, 
                                  price_function: Callable[[str], float],
                                  check_interval: int = 3600) -> bool:
        """
        Start automated backtesting system
        
        Args:
            price_function: Function that takes symbol and returns current price
            check_interval: How often to check for expired strategies (seconds)
        """
        try:
            self.price_function = price_function
            
            # Load existing active strategies
            self.strategy_tracker.load_active_strategies()
            
            # Start monitoring
            self.strategy_tracker.start_monitoring(
                check_interval=check_interval,
                get_current_price_func=price_function
            )
            
            # Add callback for completed strategies
            self.strategy_tracker.add_callback(self._on_strategies_completed)
            
            self.is_running = True
            print(f"✅ Automated backtesting started. Monitoring {len(self.strategy_tracker.get_active_strategies())} active strategies.")
            return True
            
        except Exception as e:
            print(f"❌ Error starting automated backtesting: {e}")
            return False
    
    def stop_automated_backtesting(self):
        """Stop automated backtesting system"""
        try:
            self.strategy_tracker.stop_monitoring()
            self.is_running = False
            print("🛑 Automated backtesting stopped.")
        except Exception as e:
            print(f"❌ Error stopping automated backtesting: {e}")
    
    def add_strategy_for_backtesting(self, 
                                   symbol: str,
                                   strategy_name: str,
                                   entry_price: float,
                                   lower_strike: float,
                                   upper_strike: float,
                                   lower_premium: float,
                                   upper_premium: float,
                                   contracts: int,
                                   expiration_date: datetime,
                                   market_analysis: Dict[str, Any]) -> Optional[str]:
        """
        Add a strategy to the backtesting system
        
        Returns:
            Strategy ID if successful, None otherwise
        """
        try:
            # Calculate strategy parameters
            if strategy_name == "Call Debit Spread":
                initial_cost = (lower_premium - upper_premium) * contracts
                max_profit = (upper_strike - lower_strike - (lower_premium - upper_premium)) * contracts
                max_loss = (lower_premium - upper_premium) * contracts
            elif strategy_name == "Put Debit Spread":
                initial_cost = (upper_premium - lower_premium) * contracts
                max_profit = (upper_strike - lower_strike - (upper_premium - lower_premium)) * contracts
                max_loss = (upper_premium - lower_premium) * contracts
            else:
                print(f"❌ Unknown strategy type: {strategy_name}")
                return None
            
            # Create strategy object
            strategy = BacktestStrategy(
                id=str(uuid.uuid4()),
                symbol=symbol,
                strategy_name=strategy_name,
                entry_date=datetime.now(),
                expiration_date=expiration_date,
                entry_price=entry_price,
                lower_strike=lower_strike,
                upper_strike=upper_strike,
                lower_premium=lower_premium,
                upper_premium=upper_premium,
                contracts=contracts,
                initial_cost=initial_cost,
                max_profit=max_profit,
                max_loss=max_loss,
                status=StrategyStatus.ACTIVE,
                market_analysis=market_analysis,
                created_at=datetime.now()
            )
            
            # Add to tracking system
            if self.strategy_tracker.add_strategy(strategy):
                print(f"✅ Strategy added to backtesting: {strategy.id}")
                return strategy.id
            else:
                print(f"❌ Failed to add strategy to backtesting")
                return None
                
        except Exception as e:
            print(f"❌ Error adding strategy for backtesting: {e}")
            return None
    
    def get_active_strategies(self) -> List[BacktestStrategy]:
        """Get all currently active strategies"""
        return self.strategy_tracker.get_active_strategies()
    
    def get_completed_strategies(self, limit: int = 100) -> List[BacktestStrategy]:
        """Get completed strategies for analysis"""
        return self.results_manager.get_completed_strategies(limit)
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get overall performance summary"""
        return self.results_manager.get_performance_summary()
    
    def generate_performance_report(self, limit: int = 100) -> Dict[str, Any]:
        """Generate comprehensive performance report"""
        completed_strategies = self.get_completed_strategies(limit)
        return self.performance_analyzer.generate_performance_report(completed_strategies)
    
    def create_backtest_session(self, name: str, settings: Dict[str, Any] = None) -> str:
        """Create a new backtesting session"""
        try:
            session_id = str(uuid.uuid4())
            session = BacktestSession(
                id=session_id,
                name=name,
                start_date=datetime.now(),
                end_date=None,
                strategies=[],
                performance=self.performance_analyzer._empty_metrics(),
                settings=settings or {}
            )
            
            # Save session
            self.results_manager.save_session(session)
            print(f"✅ Backtesting session created: {name} (ID: {session_id})")
            return session_id
            
        except Exception as e:
            print(f"❌ Error creating backtesting session: {e}")
            return None
    
    def complete_session(self, session_id: str) -> bool:
        """Mark a session as completed and calculate final metrics"""
        try:
            # Get completed strategies for this session
            completed_strategies = self.get_completed_strategies(1000)  # Get all for now
            
            # Calculate performance metrics
            performance = self.performance_analyzer.calculate_performance_metrics(completed_strategies)
            
            # Create completed session
            session = BacktestSession(
                id=session_id,
                name=f"Session {session_id[:8]}",
                start_date=datetime.now() - timedelta(days=30),  # Placeholder
                end_date=datetime.now(),
                strategies=completed_strategies,
                performance=performance,
                settings={}
            )
            
            # Save session
            return self.results_manager.save_session(session)
            
        except Exception as e:
            print(f"❌ Error completing session: {e}")
            return False
    
    def set_callbacks(self, 
                     on_strategy_completed: Callable[[BacktestStrategy], None] = None,
                     on_session_completed: Callable[[BacktestSession], None] = None):
        """Set callback functions for events"""
        self.on_strategy_completed = on_strategy_completed
        self.on_session_completed = on_session_completed
    
    def _on_strategies_completed(self, completed_strategies: List[BacktestStrategy]):
        """Callback when strategies are completed"""
        print(f"📊 {len(completed_strategies)} strategies completed")
        
        for strategy in completed_strategies:
            print(f"  • {strategy.symbol} {strategy.strategy_name}: ${strategy.final_pnl:.2f} ({strategy.result.value})")
            
            # Call user callback if set
            if self.on_strategy_completed:
                try:
                    self.on_strategy_completed(strategy)
                except Exception as e:
                    print(f"❌ Error in strategy completion callback: {e}")
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get current system status"""
        active_strategies = self.get_active_strategies()
        completed_strategies = self.get_completed_strategies(100)
        performance_summary = self.get_performance_summary()
        
        return {
            "is_running": self.is_running,
            "active_strategies_count": len(active_strategies),
            "completed_strategies_count": len(completed_strategies),
            "performance_summary": performance_summary,
            "last_check": datetime.now().isoformat()
        }
    
    def manual_check_expired_strategies(self) -> List[BacktestStrategy]:
        """Manually check and process expired strategies"""
        if not self.price_function:
            print("❌ No price function available")
            return []
        
        return self.strategy_tracker.process_expired_strategies(self.price_function) 