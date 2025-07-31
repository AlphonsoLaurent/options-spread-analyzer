"""
Results Manager - Handles storage and retrieval of backtesting results
"""

import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any
import pandas as pd

from .models import BacktestStrategy, PerformanceMetrics, BacktestSession, StrategyStatus, StrategyResult

class ResultsManager:
    """Manages storage and retrieval of backtesting results"""
    
    def __init__(self, db_path: str = None):
        if db_path is None:
            db_path = Path(__file__).parent.parent.parent.parent / "data" / "backtesting.db"
        
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_database()
    
    def _init_database(self):
        """Initialize the SQLite database with required tables"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Strategies table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS strategies (
                    id TEXT PRIMARY KEY,
                    symbol TEXT NOT NULL,
                    strategy_name TEXT NOT NULL,
                    entry_date TEXT NOT NULL,
                    expiration_date TEXT NOT NULL,
                    entry_price REAL NOT NULL,
                    lower_strike REAL NOT NULL,
                    upper_strike REAL NOT NULL,
                    lower_premium REAL NOT NULL,
                    upper_premium REAL NOT NULL,
                    contracts INTEGER NOT NULL,
                    initial_cost REAL NOT NULL,
                    max_profit REAL NOT NULL,
                    max_loss REAL NOT NULL,
                    status TEXT NOT NULL,
                    market_analysis TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    exit_price REAL,
                    exit_date TEXT,
                    final_pnl REAL,
                    result TEXT,
                    exit_reason TEXT,
                    notes TEXT
                )
            """)
            
            # Sessions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    start_date TEXT NOT NULL,
                    end_date TEXT,
                    settings TEXT NOT NULL
                )
            """)
            
            # Performance metrics table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS performance_metrics (
                    session_id TEXT PRIMARY KEY,
                    total_trades INTEGER NOT NULL,
                    winning_trades INTEGER NOT NULL,
                    losing_trades INTEGER NOT NULL,
                    breakeven_trades INTEGER NOT NULL,
                    win_rate REAL NOT NULL,
                    total_profit REAL NOT NULL,
                    total_loss REAL NOT NULL,
                    net_pnl REAL NOT NULL,
                    average_profit REAL NOT NULL,
                    average_loss REAL NOT NULL,
                    profit_factor REAL NOT NULL,
                    max_drawdown REAL NOT NULL,
                    sharpe_ratio REAL NOT NULL,
                    average_holding_period REAL NOT NULL,
                    FOREIGN KEY (session_id) REFERENCES sessions (id)
                )
            """)
            
            conn.commit()
    
    def save_strategy(self, strategy: BacktestStrategy) -> bool:
        """Save a strategy to the database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT OR REPLACE INTO strategies VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    strategy.id,
                    strategy.symbol,
                    strategy.strategy_name,
                    strategy.entry_date.isoformat(),
                    strategy.expiration_date.isoformat(),
                    strategy.entry_price,
                    strategy.lower_strike,
                    strategy.upper_strike,
                    strategy.lower_premium,
                    strategy.upper_premium,
                    strategy.contracts,
                    strategy.initial_cost,
                    strategy.max_profit,
                    strategy.max_loss,
                    strategy.status.value,
                    json.dumps(strategy.market_analysis),
                    strategy.created_at.isoformat(),
                    strategy.exit_price,
                    strategy.exit_date.isoformat() if strategy.exit_date else None,
                    strategy.final_pnl,
                    strategy.result.value if strategy.result else None,
                    strategy.exit_reason,
                    strategy.notes
                ))
                
                conn.commit()
                return True
        except Exception as e:
            print(f"Error saving strategy: {e}")
            return False
    
    def get_strategy(self, strategy_id: str) -> Optional[BacktestStrategy]:
        """Retrieve a strategy from the database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("SELECT * FROM strategies WHERE id = ?", (strategy_id,))
                row = cursor.fetchone()
                
                if row:
                    return self._row_to_strategy(row)
                return None
        except Exception as e:
            print(f"Error retrieving strategy: {e}")
            return None
    
    def get_active_strategies(self) -> List[BacktestStrategy]:
        """Get all active strategies"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT * FROM strategies 
                    WHERE status IN (?, ?) 
                    ORDER BY created_at DESC
                """, (StrategyStatus.PENDING.value, StrategyStatus.ACTIVE.value))
                
                rows = cursor.fetchall()
                return [self._row_to_strategy(row) for row in rows]
        except Exception as e:
            print(f"Error retrieving active strategies: {e}")
            return []
    
    def get_completed_strategies(self, limit: int = 100) -> List[BacktestStrategy]:
        """Get completed strategies for analysis"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT * FROM strategies 
                    WHERE status = ? 
                    ORDER BY exit_date DESC 
                    LIMIT ?
                """, (StrategyStatus.COMPLETED.value, limit))
                
                rows = cursor.fetchall()
                return [self._row_to_strategy(row) for row in rows]
        except Exception as e:
            print(f"Error retrieving completed strategies: {e}")
            return []
    
    def update_strategy_result(self, strategy_id: str, exit_price: float, 
                             exit_date: datetime, final_pnl: float, 
                             result: StrategyResult, exit_reason: str = None) -> bool:
        """Update strategy with final results"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    UPDATE strategies 
                    SET exit_price = ?, exit_date = ?, final_pnl = ?, 
                        result = ?, exit_reason = ?, status = ?
                    WHERE id = ?
                """, (
                    exit_price,
                    exit_date.isoformat(),
                    final_pnl,
                    result.value,
                    exit_reason,
                    StrategyStatus.COMPLETED.value,
                    strategy_id
                ))
                
                conn.commit()
                return True
        except Exception as e:
            print(f"Error updating strategy result: {e}")
            return False
    
    def save_session(self, session: BacktestSession) -> bool:
        """Save a complete backtesting session"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Save session
                cursor.execute("""
                    INSERT OR REPLACE INTO sessions VALUES (?, ?, ?, ?, ?)
                """, (
                    session.id,
                    session.name,
                    session.start_date.isoformat(),
                    session.end_date.isoformat() if session.end_date else None,
                    json.dumps(session.settings)
                ))
                
                # Save performance metrics
                cursor.execute("""
                    INSERT OR REPLACE INTO performance_metrics VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    session.id,
                    session.performance.total_trades,
                    session.performance.winning_trades,
                    session.performance.losing_trades,
                    session.performance.breakeven_trades,
                    session.performance.win_rate,
                    session.performance.total_profit,
                    session.performance.total_loss,
                    session.performance.net_pnl,
                    session.performance.average_profit,
                    session.performance.average_loss,
                    session.performance.profit_factor,
                    session.performance.max_drawdown,
                    session.performance.sharpe_ratio,
                    session.performance.average_holding_period
                ))
                
                # Save all strategies in the session
                for strategy in session.strategies:
                    self.save_strategy(strategy)
                
                conn.commit()
                return True
        except Exception as e:
            print(f"Error saving session: {e}")
            return False
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get overall performance summary"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Get basic stats
                cursor.execute("""
                    SELECT 
                        COUNT(*) as total_trades,
                        SUM(CASE WHEN result = 'profit' THEN 1 ELSE 0 END) as winning_trades,
                        SUM(CASE WHEN result = 'loss' THEN 1 ELSE 0 END) as losing_trades,
                        SUM(CASE WHEN result = 'breakeven' THEN 1 ELSE 0 END) as breakeven_trades,
                        SUM(final_pnl) as total_pnl,
                        AVG(final_pnl) as avg_pnl
                    FROM strategies 
                    WHERE status = 'completed'
                """)
                
                row = cursor.fetchone()
                if row:
                    total_trades, winning_trades, losing_trades, breakeven_trades, total_pnl, avg_pnl = row
                    
                    win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
                    
                    return {
                        'total_trades': total_trades or 0,
                        'winning_trades': winning_trades or 0,
                        'losing_trades': losing_trades or 0,
                        'breakeven_trades': breakeven_trades or 0,
                        'win_rate': round(win_rate, 2),
                        'total_pnl': total_pnl or 0,
                        'average_pnl': round(avg_pnl or 0, 2)
                    }
                
                return {
                    'total_trades': 0,
                    'winning_trades': 0,
                    'losing_trades': 0,
                    'breakeven_trades': 0,
                    'win_rate': 0,
                    'total_pnl': 0,
                    'average_pnl': 0
                }
        except Exception as e:
            print(f"Error getting performance summary: {e}")
            return {}
    
    def _row_to_strategy(self, row) -> BacktestStrategy:
        """Convert database row to BacktestStrategy object"""
        return BacktestStrategy(
            id=row[0],
            symbol=row[1],
            strategy_name=row[2],
            entry_date=datetime.fromisoformat(row[3]),
            expiration_date=datetime.fromisoformat(row[4]),
            entry_price=row[5],
            lower_strike=row[6],
            upper_strike=row[7],
            lower_premium=row[8],
            upper_premium=row[9],
            contracts=row[10],
            initial_cost=row[11],
            max_profit=row[12],
            max_loss=row[13],
            status=StrategyStatus(row[14]),
            market_analysis=json.loads(row[15]),
            created_at=datetime.fromisoformat(row[16]),
            exit_price=row[17],
            exit_date=datetime.fromisoformat(row[18]) if row[18] else None,
            final_pnl=row[19],
            result=StrategyResult(row[20]) if row[20] else None,
            exit_reason=row[21],
            notes=row[22]
        ) 