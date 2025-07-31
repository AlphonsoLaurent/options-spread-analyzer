"""
Position Analysis Module - Functions for analyzing and monitoring trading positions
"""

import streamlit as st
from datetime import datetime, timedelta
from typing import Dict, Any

def calculate_real_pnl(strategy_name: str, params: dict, current_price: float, entry_price: float = 0.0) -> float:
    """Calculate real P&L for a strategy position."""
    try:
        # Get strategy parameters
        lower_strike = params.get('lower_strike', 0)
        upper_strike = params.get('upper_strike', 0)
        lower_premium = params.get('lower_premium', 0)
        upper_premium = params.get('upper_premium', 0)
        
        # Calculate theoretical P&L based on strategy type
        if strategy_name in ["Call Debit Spread", "Put Debit Spread"]:
            # Debit spreads: we paid a net premium
            net_premium = abs(lower_premium - upper_premium)
            
            if strategy_name == "Call Debit Spread":
                # For call debit spread, profit increases as price goes up
                if current_price <= lower_strike:
                    pnl = -net_premium  # Maximum loss
                elif current_price >= upper_strike:
                    pnl = (upper_strike - lower_strike) - net_premium  # Maximum profit
                else:
                    # Linear interpolation between strikes
                    pnl = (current_price - lower_strike) - net_premium
            else:  # Put Debit Spread
                # For put debit spread, profit increases as price goes down
                if current_price >= upper_strike:
                    pnl = -net_premium  # Maximum loss
                elif current_price <= lower_strike:
                    pnl = (upper_strike - lower_strike) - net_premium  # Maximum profit
                else:
                    # Linear interpolation between strikes
                    pnl = (upper_strike - current_price) - net_premium
                    
        else:  # Credit spreads
            # Credit spreads: we received a net premium
            net_premium = abs(upper_premium - lower_premium)
            
            if strategy_name == "Call Credit Spread":
                # For call credit spread, profit decreases as price goes up
                if current_price <= lower_strike:
                    pnl = net_premium  # Maximum profit
                elif current_price >= upper_strike:
                    pnl = net_premium - (upper_strike - lower_strike)  # Maximum loss
                else:
                    # Linear interpolation between strikes
                    pnl = net_premium - (current_price - lower_strike)
            else:  # Put Credit Spread
                # For put credit spread, profit decreases as price goes down
                if current_price >= upper_strike:
                    pnl = net_premium  # Maximum profit
                elif current_price <= lower_strike:
                    pnl = net_premium - (upper_strike - lower_strike)  # Maximum loss
                else:
                    # Linear interpolation between strikes
                    pnl = net_premium - (upper_strike - current_price)
        
        return round(pnl, 2)
        
    except Exception as e:
        st.error(f"Error calculating P&L: {str(e)}")
        return 0.0

def render_position_analysis():
    """Render position monitoring and analysis."""
    
    if not st.session_state.get('results'):
        return
    
    results_data = st.session_state['results']
    strategy_name = results_data['strategy_name']
    symbol = results_data['symbol']
    current_price = results_data['current_price']
    params = results_data.get('params', {})
    risk_levels = params.get('risk_levels', {})
    
    st.markdown("---")
    st.subheader("📈 Monitoreo de Posición")
    
    # Calculate current P&L
    current_pnl = calculate_real_pnl(strategy_name, params, current_price)
    
    # Get risk management levels - handle both dict and object
    if hasattr(risk_levels, 'get'):
        # It's a dictionary
        stop_loss = risk_levels.get('stop_loss', 0)
        take_profit = risk_levels.get('take_profit', 0)
        dte_alert = risk_levels.get('dte_alert', 21)
    else:
        # It's an object, try to access attributes directly
        stop_loss = getattr(risk_levels, 'stop_loss', 0)
        take_profit = getattr(risk_levels, 'take_profit', 0)
        dte_alert = getattr(risk_levels, 'dte_alert', 21)
    
    # Calculate days to expiration
    expiration_date = datetime.strptime(results_data['expiration'], "%Y-%m-%d")
    days_to_expiration = (expiration_date - datetime.now()).days
    
    # P&L and Risk Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        # P&L with color coding
        pnl_color = "normal" if current_pnl >= 0 else "inverse"
        st.metric("💰 P&L Actual", f"${current_pnl:.2f}", delta_color=pnl_color)
    
    with col2:
        # P&L percentage
        max_loss = abs(results_data['results'].max_loss)
        pnl_percentage = (current_pnl / max_loss) * 100 if max_loss > 0 else 0
        st.metric("📊 P&L %", f"{pnl_percentage:.1f}%")
    
    with col3:
        # Distance to stop loss
        if stop_loss > 0:
            distance_to_sl = ((current_pnl - stop_loss) / max_loss) * 100 if max_loss > 0 else 0
            st.metric("🛑 Distancia a SL", f"{distance_to_sl:.1f}%")
        else:
            st.metric("🛑 Distancia a SL", "N/A")
    
    with col4:
        # Distance to take profit
        if take_profit > 0:
            distance_to_tp = ((take_profit - current_pnl) / max_loss) * 100 if max_loss > 0 else 0
            st.metric("🎯 Distancia a TP", f"{distance_to_tp:.1f}%")
        else:
            st.metric("🎯 Distancia a TP", "N/A")
    
    # Risk Management Levels
    st.markdown("### 🛡️ Niveles de Gestión de Riesgo")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("🛑 Stop Loss", f"${stop_loss:.2f}")
    
    with col2:
        st.metric("🎯 Take Profit", f"${take_profit:.2f}")
    
    with col3:
        st.metric("📅 DTE", f"{days_to_expiration} días")
    
    with col4:
        st.metric("⚠️ Alerta DTE", f"{dte_alert} días")
    
    # Alert Status
    st.markdown("### 🚨 Estado de Alertas")
    
    # Check for critical alerts
    critical_alerts = []
    
    # Stop Loss alert
    if current_pnl <= stop_loss:
        critical_alerts.append("🛑 **STOP LOSS ACTIVADO** - Considera cerrar la posición")
    
    # Take Profit alert
    if current_pnl >= take_profit:
        critical_alerts.append("🎯 **TAKE PROFIT ACTIVADO** - Considera cerrar la posición")
    
    # DTE alert
    if days_to_expiration <= 3:
        critical_alerts.append("⏰ **DTE CRÍTICO** - Solo quedan 3 días o menos")
    elif days_to_expiration <= dte_alert:
        critical_alerts.append("⚠️ **DTE CERCANO** - Considera gestionar la posición")
    
    # Near levels alerts
    if stop_loss > 0 and current_pnl <= stop_loss * 1.1:
        critical_alerts.append("🟡 **CERCANO A SL** - Monitorea de cerca")
    
    if take_profit > 0 and current_pnl >= take_profit * 0.9:
        critical_alerts.append("🟡 **CERCANO A TP** - Considera tomar ganancias")
    
    # Display alerts
    if critical_alerts:
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%);
            color: white;
            padding: 20px;
            border-radius: 10px;
            margin: 10px 0;
        ">
            <h3 style="margin: 0 0 15px 0;">🚨 ALERTAS CRÍTICAS</h3>
        """, unsafe_allow_html=True)
        
        for alert in critical_alerts:
            st.markdown(f"• {alert}")
        
        st.markdown("""
        <div style="margin-top: 15px;">
            <button style="
                background: #2ecc71;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 5px;
                margin-right: 10px;
                cursor: pointer;
            ">📞 Contactar Broker</button>
            <button style="
                background: #3498db;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 5px;
                margin-right: 10px;
                cursor: pointer;
            ">📊 Ver Detalles</button>
            <button style="
                background: #95a5a6;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 5px;
                cursor: pointer;
            ">🔕 Silenciar 5min</button>
        </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.success("✅ **Sin alertas críticas** - Posición en buen estado")
    
    # Performance Metrics
    st.markdown("### 📊 Métricas de Rendimiento")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        # Time in position - calculated from entry date
        if 'entry_date' in results_data:
            entry_date = datetime.strptime(results_data['entry_date'], "%Y-%m-%d")
            time_in_position = (datetime.now() - entry_date).days
        else:
            time_in_position = 0
        st.metric("⏱️ Tiempo en Posición", f"{time_in_position} días")
    
    with col2:
        # Daily P&L change - calculated from previous day
        if 'previous_pnl' in results_data:
            daily_pnl_change = current_pnl - results_data['previous_pnl']
        else:
            daily_pnl_change = 0.0
        st.metric("📈 Cambio Diario", f"${daily_pnl_change:.2f}")
    
    with col3:
        # Win probability based on current position and market analysis
        market_analysis = results_data.get('market_analysis', {})
        if market_analysis and 'profit_probability' in market_analysis:
            win_probability = market_analysis['profit_probability'] * 100
        else:
            win_probability = 50.0  # Default neutral probability
        st.metric("🎯 Probabilidad de Ganancia", f"{win_probability:.1f}%")
    
    with col4:
        # Risk level
        risk_level = "Alto" if abs(pnl_percentage) > 50 else "Medio" if abs(pnl_percentage) > 25 else "Bajo"
        st.metric("⚠️ Nivel de Riesgo", risk_level)
    
    # Action Buttons
    st.markdown("### 🎯 Acciones Disponibles")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("📊 Actualizar Datos", type="primary", use_container_width=True):
            st.rerun()
    
    with col2:
        if st.button("📈 Ver Gráfico", type="secondary", use_container_width=True):
            st.info("📈 Funcionalidad de gráfico en desarrollo")
    
    with col3:
        if st.button("📝 Registrar Nota", type="secondary", use_container_width=True):
            st.info("📝 Funcionalidad de notas en desarrollo")
    
    with col4:
        if st.button("🔄 Cerrar Posición", type="secondary", use_container_width=True):
            st.warning("🔄 Funcionalidad de cierre en desarrollo") 