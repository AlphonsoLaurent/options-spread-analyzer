"""
Performance Analyzer - Calculates performance metrics and generates reports
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

from .models import BacktestStrategy, PerformanceMetrics, StrategyResult
from .results_manager import ResultsManager

class PerformanceAnalyzer:
    """Analyzes backtesting performance and generates reports"""
    
    def __init__(self, results_manager: ResultsManager):
        self.results_manager = results_manager
    
    def calculate_performance_metrics(self, strategies: List[BacktestStrategy]) -> PerformanceMetrics:
        """Calculate comprehensive performance metrics"""
        if not strategies:
            return self._empty_metrics()
        
        # Basic counts
        total_trades = len(strategies)
        winning_trades = len([s for s in strategies if s.result == StrategyResult.PROFIT])
        losing_trades = len([s for s in strategies if s.result == StrategyResult.LOSS])
        breakeven_trades = len([s for s in strategies if s.result == StrategyResult.BREAKEVEN])
        
        # Win rate
        win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
        
        # P&L calculations
        profits = [s.final_pnl for s in strategies if s.final_pnl and s.final_pnl > 0]
        losses = [s.final_pnl for s in strategies if s.final_pnl and s.final_pnl < 0]
        
        total_profit = sum(profits) if profits else 0
        total_loss = abs(sum(losses)) if losses else 0
        net_pnl = total_profit - total_loss
        
        average_profit = np.mean(profits) if profits else 0
        average_loss = np.mean(losses) if losses else 0
        
        # Profit factor
        profit_factor = total_profit / total_loss if total_loss > 0 else float('inf')
        
        # Maximum drawdown
        cumulative_pnl = self._calculate_cumulative_pnl(strategies)
        max_drawdown = self._calculate_max_drawdown(cumulative_pnl)
        
        # Sharpe ratio (simplified)
        returns = [s.final_pnl for s in strategies if s.final_pnl is not None]
        sharpe_ratio = self._calculate_sharpe_ratio(returns)
        
        # Average holding period
        holding_periods = []
        for strategy in strategies:
            if strategy.entry_date and strategy.exit_date:
                holding_period = (strategy.exit_date - strategy.entry_date).days
                holding_periods.append(holding_period)
        
        average_holding_period = np.mean(holding_periods) if holding_periods else 0
        
        return PerformanceMetrics(
            total_trades=total_trades,
            winning_trades=winning_trades,
            losing_trades=losing_trades,
            breakeven_trades=breakeven_trades,
            win_rate=round(win_rate, 2),
            total_profit=round(total_profit, 2),
            total_loss=round(total_loss, 2),
            net_pnl=round(net_pnl, 2),
            average_profit=round(average_profit, 2),
            average_loss=round(average_loss, 2),
            profit_factor=round(profit_factor, 2),
            max_drawdown=round(max_drawdown, 2),
            sharpe_ratio=round(sharpe_ratio, 2),
            average_holding_period=round(average_holding_period, 1)
        )
    
    def generate_performance_report(self, strategies: List[BacktestStrategy]) -> Dict[str, Any]:
        """Generate a comprehensive performance report"""
        if not strategies:
            return {"error": "No strategies to analyze"}
        
        # Calculate metrics
        metrics = self.calculate_performance_metrics(strategies)
        
        # Strategy breakdown
        strategy_breakdown = self._analyze_strategy_breakdown(strategies)
        
        # Time analysis
        time_analysis = self._analyze_time_performance(strategies)
        
        # Risk analysis
        risk_analysis = self._analyze_risk_metrics(strategies)
        
        return {
            "summary": {
                "total_trades": metrics.total_trades,
                "win_rate": f"{metrics.win_rate}%",
                "net_pnl": f"${metrics.net_pnl:,.2f}",
                "profit_factor": metrics.profit_factor,
                "max_drawdown": f"{metrics.max_drawdown}%",
                "sharpe_ratio": metrics.sharpe_ratio
            },
            "detailed_metrics": {
                "winning_trades": metrics.winning_trades,
                "losing_trades": metrics.losing_trades,
                "breakeven_trades": metrics.breakeven_trades,
                "total_profit": f"${metrics.total_profit:,.2f}",
                "total_loss": f"${metrics.total_loss:,.2f}",
                "average_profit": f"${metrics.average_profit:,.2f}",
                "average_loss": f"${metrics.average_loss:,.2f}",
                "average_holding_period": f"{metrics.average_holding_period} days"
            },
            "strategy_breakdown": strategy_breakdown,
            "time_analysis": time_analysis,
            "risk_analysis": risk_analysis
        }
    
    def _analyze_strategy_breakdown(self, strategies: List[BacktestStrategy]) -> Dict[str, Any]:
        """Analyze performance by strategy type"""
        breakdown = {}
        
        for strategy in strategies:
            strategy_name = strategy.strategy_name
            if strategy_name not in breakdown:
                breakdown[strategy_name] = {
                    "total": 0,
                    "wins": 0,
                    "losses": 0,
                    "breakeven": 0,
                    "total_pnl": 0,
                    "avg_pnl": 0
                }
            
            breakdown[strategy_name]["total"] += 1
            breakdown[strategy_name]["total_pnl"] += strategy.final_pnl or 0
            
            if strategy.result == StrategyResult.PROFIT:
                breakdown[strategy_name]["wins"] += 1
            elif strategy.result == StrategyResult.LOSS:
                breakdown[strategy_name]["losses"] += 1
            else:
                breakdown[strategy_name]["breakeven"] += 1
        
        # Calculate averages and percentages
        for strategy_name, data in breakdown.items():
            total = data["total"]
            data["win_rate"] = round((data["wins"] / total * 100), 2) if total > 0 else 0
            data["avg_pnl"] = round(data["total_pnl"] / total, 2) if total > 0 else 0
            data["total_pnl"] = round(data["total_pnl"], 2)
        
        return breakdown
    
    def _analyze_time_performance(self, strategies: List[BacktestStrategy]) -> Dict[str, Any]:
        """Analyze performance over time"""
        if not strategies:
            return {}
        
        # Group by month
        monthly_data = {}
        for strategy in strategies:
            if strategy.entry_date:
                month_key = strategy.entry_date.strftime("%Y-%m")
                if month_key not in monthly_data:
                    monthly_data[month_key] = {
                        "trades": 0,
                        "pnl": 0,
                        "wins": 0,
                        "losses": 0
                    }
                
                monthly_data[month_key]["trades"] += 1
                monthly_data[month_key]["pnl"] += strategy.final_pnl or 0
                
                if strategy.result == StrategyResult.PROFIT:
                    monthly_data[month_key]["wins"] += 1
                elif strategy.result == StrategyResult.LOSS:
                    monthly_data[month_key]["losses"] += 1
        
        # Calculate monthly win rates
        for month, data in monthly_data.items():
            data["win_rate"] = round((data["wins"] / data["trades"] * 100), 2) if data["trades"] > 0 else 0
            data["pnl"] = round(data["pnl"], 2)
        
        return monthly_data
    
    def _analyze_risk_metrics(self, strategies: List[BacktestStrategy]) -> Dict[str, Any]:
        """Analyze risk metrics"""
        if not strategies:
            return {}
        
        # Calculate various risk metrics
        pnls = [s.final_pnl for s in strategies if s.final_pnl is not None]
        
        if not pnls:
            return {}
        
        # Volatility
        volatility = np.std(pnls)
        
        # Value at Risk (95% confidence)
        var_95 = np.percentile(pnls, 5)
        
        # Maximum consecutive losses
        consecutive_losses = self._calculate_max_consecutive_losses(strategies)
        
        # Largest win and loss
        largest_win = max(pnls) if pnls else 0
        largest_loss = min(pnls) if pnls else 0
        
        return {
            "volatility": round(volatility, 2),
            "var_95": round(var_95, 2),
            "max_consecutive_losses": consecutive_losses,
            "largest_win": round(largest_win, 2),
            "largest_loss": round(largest_loss, 2),
            "avg_trade": round(np.mean(pnls), 2)
        }
    
    def _calculate_cumulative_pnl(self, strategies: List[BacktestStrategy]) -> List[float]:
        """Calculate cumulative P&L over time"""
        if not strategies:
            return []
        
        # Sort by entry date
        sorted_strategies = sorted(strategies, key=lambda x: x.entry_date)
        
        cumulative = 0
        cumulative_pnl = []
        
        for strategy in sorted_strategies:
            cumulative += strategy.final_pnl or 0
            cumulative_pnl.append(cumulative)
        
        return cumulative_pnl
    
    def _calculate_max_drawdown(self, cumulative_pnl: List[float]) -> float:
        """Calculate maximum drawdown"""
        if not cumulative_pnl:
            return 0
        
        peak = cumulative_pnl[0]
        max_dd = 0
        
        for value in cumulative_pnl:
            if value > peak:
                peak = value
            drawdown = (peak - value) / peak * 100 if peak > 0 else 0
            max_dd = max(max_dd, drawdown)
        
        return max_dd
    
    def _calculate_sharpe_ratio(self, returns: List[float]) -> float:
        """Calculate Sharpe ratio (simplified)"""
        if not returns or len(returns) < 2:
            return 0
        
        mean_return = np.mean(returns)
        std_return = np.std(returns)
        
        if std_return == 0:
            return 0
        
        # Assuming risk-free rate of 0 for simplicity
        sharpe = mean_return / std_return
        return sharpe
    
    def _calculate_max_consecutive_losses(self, strategies: List[BacktestStrategy]) -> int:
        """Calculate maximum consecutive losses"""
        if not strategies:
            return 0
        
        # Sort by entry date
        sorted_strategies = sorted(strategies, key=lambda x: x.entry_date)
        
        max_consecutive = 0
        current_consecutive = 0
        
        for strategy in sorted_strategies:
            if strategy.result == StrategyResult.LOSS:
                current_consecutive += 1
                max_consecutive = max(max_consecutive, current_consecutive)
            else:
                current_consecutive = 0
        
        return max_consecutive
    
    def _empty_metrics(self) -> PerformanceMetrics:
        """Return empty performance metrics"""
        return PerformanceMetrics(
            total_trades=0,
            winning_trades=0,
            losing_trades=0,
            breakeven_trades=0,
            win_rate=0,
            total_profit=0,
            total_loss=0,
            net_pnl=0,
            average_profit=0,
            average_loss=0,
            profit_factor=0,
            max_drawdown=0,
            sharpe_ratio=0,
            average_holding_period=0
        ) 