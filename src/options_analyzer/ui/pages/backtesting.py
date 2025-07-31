"""
Backtesting Page - UI for automated strategy testing
"""

import streamlit as st
from datetime import datetime, timedelta
import sys
from pathlib import Path

# Add core directory to sys.path for imports
current_file = Path(__file__)
core_dir = current_file.parent.parent.parent.parent
sys.path.insert(0, str(core_dir))

from options_analyzer.backtesting import BacktestEngine, ResultsManager
from options_analyzer.data.market_data import get_market_data

def get_current_price(symbol: str) -> float:
    """Get current price for a symbol"""
    try:
        market_data = get_market_data(symbol)
        return market_data['current_price'] if market_data else 0.0
    except:
        return 0.0

def initialize_backtest_engine():
    """Initialize the backtesting engine"""
    if 'backtest_engine' not in st.session_state:
        st.session_state['backtest_engine'] = BacktestEngine()
    
    return st.session_state['backtest_engine']

def render():
    """Render the backtesting page"""
    st.markdown('<h1 class="main-header">🤖 Automated Strategy Backtesting</h1>', unsafe_allow_html=True)
    
    # Initialize engine
    engine = initialize_backtest_engine()
    
    # Main tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Dashboard", 
        "➕ Add Strategy", 
        "📈 Performance", 
        "⚙️ Settings"
    ])
    
    with tab1:
        render_dashboard(engine)
    
    with tab2:
        render_add_strategy(engine)
    
    with tab3:
        render_performance(engine)
    
    with tab4:
        render_settings(engine)

def render_dashboard(engine: BacktestEngine):
    """Render the main dashboard"""
    st.subheader("📊 Backtesting Dashboard")
    
    # System status
    status = engine.get_system_status()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        status_color = "🟢" if status['is_running'] else "🔴"
        st.metric(
            "System Status",
            f"{status_color} {'Running' if status['is_running'] else 'Stopped'}"
        )
    
    with col2:
        st.metric(
            "Active Strategies",
            status['active_strategies_count']
        )
    
    with col3:
        st.metric(
            "Completed Strategies",
            status['completed_strategies_count']
        )
    
    with col4:
        performance = status['performance_summary']
        win_rate = performance.get('win_rate', 0)
        st.metric(
            "Win Rate",
            f"{win_rate}%"
        )
    
    # Control buttons
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🚀 Start Backtesting", type="primary", use_container_width=True):
            if engine.start_automated_backtesting(get_current_price, check_interval=3600):
                st.success("✅ Backtesting started successfully!")
                st.rerun()
            else:
                st.error("❌ Failed to start backtesting")
    
    with col2:
        if st.button("🛑 Stop Backtesting", use_container_width=True):
            engine.stop_automated_backtesting()
            st.success("✅ Backtesting stopped")
            st.rerun()
    
    with col3:
        if st.button("🔄 Check Expired", use_container_width=True):
            completed = engine.manual_check_expired_strategies()
            if completed:
                st.success(f"✅ Processed {len(completed)} expired strategies")
            else:
                st.info("ℹ️ No expired strategies found")
    
    # Active strategies table
    st.markdown("---")
    st.subheader("📋 Active Strategies")
    
    active_strategies = engine.get_active_strategies()
    
    if active_strategies:
        # Create table data
        table_data = []
        for strategy in active_strategies:
            days_to_expiry = (strategy.expiration_date - datetime.now()).days
            
            table_data.append({
                "Symbol": strategy.symbol,
                "Strategy": strategy.strategy_name,
                "Entry Date": strategy.entry_date.strftime("%Y-%m-%d"),
                "Expiry": strategy.expiration_date.strftime("%Y-%m-%d"),
                "Days Left": days_to_expiry,
                "Contracts": strategy.contracts,
                "Max Profit": f"${strategy.max_profit:.2f}",
                "Max Loss": f"${strategy.max_loss:.2f}"
            })
        
        st.dataframe(table_data, use_container_width=True)
    else:
        st.info("ℹ️ No active strategies found")

def render_add_strategy(engine: BacktestEngine):
    """Render the add strategy form"""
    st.subheader("➕ Add Strategy for Backtesting")
    
    with st.form("add_strategy_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            symbol = st.text_input("Symbol", value="AAPL").upper()
            strategy_name = st.selectbox(
                "Strategy Type",
                ["Call Debit Spread", "Put Debit Spread"]
            )
            contracts = st.number_input("Contracts", min_value=1, value=1)
        
        with col2:
            entry_price = st.number_input("Entry Price", min_value=0.01, value=150.0)
            expiration_days = st.number_input("Days to Expiry", min_value=1, value=3)
        
        # Strategy-specific inputs
        st.markdown("### Strategy Parameters")
        
        if strategy_name == "Call Debit Spread":
            col1, col2 = st.columns(2)
            with col1:
                lower_strike = st.number_input("Lower Strike (Buy)", value=entry_price * 0.98)
                lower_premium = st.number_input("Lower Premium (Buy)", value=entry_price * 0.03)
            with col2:
                upper_strike = st.number_input("Upper Strike (Sell)", value=entry_price * 1.03)
                upper_premium = st.number_input("Upper Premium (Sell)", value=entry_price * 0.01)
        
        elif strategy_name == "Put Debit Spread":
            col1, col2 = st.columns(2)
            with col1:
                upper_strike = st.number_input("Upper Strike (Buy)", value=entry_price * 1.02)
                upper_premium = st.number_input("Upper Premium (Buy)", value=entry_price * 0.03)
            with col2:
                lower_strike = st.number_input("Lower Strike (Sell)", value=entry_price * 0.97)
                lower_premium = st.number_input("Lower Premium (Sell)", value=entry_price * 0.01)
        
        # Market analysis (simplified)
        st.markdown("### Market Analysis")
        market_analysis = {
            "trend": st.selectbox("Market Trend", ["Uptrend", "Downtrend", "Neutral"]),
            "rsi": st.slider("RSI", 0, 100, 50),
            "macd": st.selectbox("MACD", ["Bullish", "Bearish", "Neutral"]),
            "implied_volatility": st.slider("Implied Volatility", 10, 100, 30)
        }
        
        # Calculate expiration date
        expiration_date = datetime.now() + timedelta(days=expiration_days)
        
        submitted = st.form_submit_button("🚀 Add to Backtesting", type="primary")
        
        if submitted:
            strategy_id = engine.add_strategy_for_backtesting(
                symbol=symbol,
                strategy_name=strategy_name,
                entry_price=entry_price,
                lower_strike=lower_strike,
                upper_strike=upper_strike,
                lower_premium=lower_premium,
                upper_premium=upper_premium,
                contracts=contracts,
                expiration_date=expiration_date,
                market_analysis=market_analysis
            )
            
            if strategy_id:
                st.success(f"✅ Strategy added successfully! ID: {strategy_id[:8]}")
                st.rerun()
            else:
                st.error("❌ Failed to add strategy")

def render_performance(engine: BacktestEngine):
    """Render performance analysis"""
    st.subheader("📈 Performance Analysis")
    
    # Performance summary
    performance_summary = engine.get_performance_summary()
    
    if performance_summary:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Total Trades",
                performance_summary.get('total_trades', 0)
            )
        
        with col2:
            st.metric(
                "Win Rate",
                f"{performance_summary.get('win_rate', 0)}%"
            )
        
        with col3:
            st.metric(
                "Total P&L",
                f"${performance_summary.get('total_pnl', 0):,.2f}"
            )
        
        with col4:
            st.metric(
                "Avg P&L",
                f"${performance_summary.get('average_pnl', 0):,.2f}"
            )
        
        # Detailed report
        st.markdown("---")
        st.subheader("📊 Detailed Performance Report")
        
        if st.button("🔄 Generate Report"):
            with st.spinner("Generating performance report..."):
                report = engine.generate_performance_report()
                
                if "error" not in report:
                    # Summary
                    st.markdown("### Summary")
                    summary = report['summary']
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("Total Trades", summary['total_trades'])
                        st.metric("Win Rate", summary['win_rate'])
                    
                    with col2:
                        st.metric("Net P&L", summary['net_pnl'])
                        st.metric("Profit Factor", summary['profit_factor'])
                    
                    with col3:
                        st.metric("Max Drawdown", summary['max_drawdown'])
                        st.metric("Sharpe Ratio", summary['sharpe_ratio'])
                    
                    # Strategy breakdown
                    st.markdown("### Strategy Breakdown")
                    breakdown = report['strategy_breakdown']
                    if breakdown:
                        breakdown_data = []
                        for strategy, data in breakdown.items():
                            breakdown_data.append({
                                "Strategy": strategy,
                                "Total Trades": data['total'],
                                "Wins": data['wins'],
                                "Losses": data['losses'],
                                "Win Rate": f"{data['win_rate']}%",
                                "Total P&L": f"${data['total_pnl']:.2f}",
                                "Avg P&L": f"${data['avg_pnl']:.2f}"
                            })
                        
                        st.dataframe(breakdown_data, use_container_width=True)
                    
                    # Risk analysis
                    st.markdown("### Risk Analysis")
                    risk = report['risk_analysis']
                    if risk:
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.metric("Volatility", f"${risk['volatility']:.2f}")
                            st.metric("VaR (95%)", f"${risk['var_95']:.2f}")
                        
                        with col2:
                            st.metric("Max Consecutive Losses", risk['max_consecutive_losses'])
                            st.metric("Largest Win", f"${risk['largest_win']:.2f}")
                        
                        with col3:
                            st.metric("Largest Loss", f"${risk['largest_loss']:.2f}")
                            st.metric("Avg Trade", f"${risk['avg_trade']:.2f}")
                else:
                    st.error("❌ No completed strategies to analyze")
    else:
        st.info("ℹ️ No performance data available yet")

def render_settings(engine: BacktestEngine):
    """Render settings page"""
    st.subheader("⚙️ Backtesting Settings")
    
    # Check interval
    st.markdown("### Monitoring Settings")
    check_interval = st.slider(
        "Check Interval (hours)",
        min_value=1,
        max_value=24,
        value=1,
        help="How often to check for expired strategies"
    )
    
    # Database info
    st.markdown("### Database Information")
    st.info(f"Database location: {engine.results_manager.db_path}")
    
    # Export/Import
    st.markdown("### Data Management")
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📤 Export Data"):
            st.info("Export functionality coming soon...")
    
    with col2:
        if st.button("🗑️ Clear All Data"):
            if st.checkbox("I understand this will delete all backtesting data"):
                st.warning("Clear data functionality coming soon...")
    
    # System info
    st.markdown("### System Information")
    status = engine.get_system_status()
    
    st.json({
        "System Status": status,
        "Last Check": status['last_check']
    }) 