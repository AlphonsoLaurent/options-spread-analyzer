"""
Strategy Inputs Module - Functions for handling strategy input parameters with user-friendly interface
"""

import streamlit as st
from datetime import datetime, timedelta
from typing import Dict, Any
try:
    from core.risk_management import RiskManagementSystem, RiskManagementUI
except ImportError:
    import sys
    from pathlib import Path
    sys.path.append(str(Path(__file__).parent.parent.parent.parent))
    from core.risk_management import RiskManagementSystem, RiskManagementUI

# Initialize risk management system
if 'risk_management_system' not in st.session_state:
    st.session_state['risk_management_system'] = RiskManagementSystem()

if 'risk_management_ui' not in st.session_state:
    st.session_state['risk_management_ui'] = RiskManagementUI(st.session_state['risk_management_system'])

risk_management_ui = st.session_state['risk_management_ui']

def get_next_business_days(start_date: datetime, business_days: int = 5) -> datetime:
    """
    Calculate the date that is N business days from start_date.
    Excludes weekends (Saturday=5, Sunday=6).
    """
    current_date = start_date
    business_days_count = 0
    
    while business_days_count < business_days:
        current_date += timedelta(days=1)
        # Monday=0, Tuesday=1, ..., Sunday=6
        if current_date.weekday() < 5:  # Monday to Friday
            business_days_count += 1
    
    return current_date

def get_strategy_inputs(strategy_name: str, current_price: float, context: str = "main"):
    """Get strategy-specific input parameters with user-friendly interface."""
    
    # Add context prefix to make keys unique
    prefix = f"{context}_"
    
    if strategy_name == "Call Debit Spread":
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### 🟢 CALL que COMPRAS (Apuestas que suba)")
            lower_strike = st.number_input(
                "🎯 Precio de Ejercicio", 
                value=current_price * 0.98, 
                key=f"{prefix}cds_lower",
                help="Precio al que puedes comprar las acciones si ejercitas la opción"
            )
            lower_premium = st.number_input(
                "💰 Costo de la Opción", 
                value=current_price * 0.03, 
                key=f"{prefix}cds_lower_prem",
                help="Lo que pagas por esta opción (compras esta opción, pagas prima)"
            )
        with col2:
            st.markdown("### 🔴 CALL que VENDES (Limitas ganancia)")
            upper_strike = st.number_input(
                "🎯 Precio de Ejercicio", 
                value=current_price * 1.03, 
                key=f"{prefix}cds_upper",
                help="Precio al que puedes comprar las acciones si ejercitas la opción"
            )
            upper_premium = st.number_input(
                "💰 Costo de la Opción", 
                value=current_price * 0.01, 
                key=f"{prefix}cds_upper_prem",
                help="Lo que recibes por vender esta opción (vendes esta opción, recibes prima)"
            )
        
        # Calcular parámetros de la estrategia
        premium_paid = lower_premium - upper_premium
        max_profit = upper_strike - lower_strike - premium_paid
        max_loss = premium_paid
        
        # Mostrar resumen de costos
        st.markdown("### 💰 Resumen de Costos")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("💸 Pagas por CALL comprada", f"${lower_premium:.2f}")
        with col2:
            st.metric("💵 Recibes por CALL vendida", f"${upper_premium:.2f}")
        with col3:
            st.metric("💳 Costo Neto Total", f"${premium_paid:.2f}", delta_color="inverse" if premium_paid > 0 else "normal")
        
        # Configuración de gestión de riesgo
        expiration_date = get_next_business_days(datetime.now(), 3).strftime("%Y-%m-%d")
        risk_levels = risk_management_ui.render_risk_configuration(
            strategy_name, premium_paid, max_profit, max_loss, current_price, expiration_date
        )
        
        return {
            'lower_strike': lower_strike, 'upper_strike': upper_strike,
            'lower_premium': lower_premium, 'upper_premium': upper_premium,
            'risk_levels': risk_levels, 'expiration_date': expiration_date
        }
    

    
    elif strategy_name == "Put Debit Spread":
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### 🟢 PUT que COMPRAS (Apuestas que baje)")
            upper_strike = st.number_input(
                "🎯 Precio de Ejercicio", 
                value=current_price * 1.02, 
                key=f"{prefix}pds_upper",
                help="Precio al que puedes vender las acciones si ejercitas la opción"
            )
            upper_premium = st.number_input(
                "💰 Costo de la Opción", 
                value=current_price * 0.03, 
                key=f"{prefix}pds_upper_prem",
                help="Lo que pagas por esta opción (compras esta opción, pagas prima)"
            )
        with col2:
            st.markdown("### 🔴 PUT que VENDES (Limitas ganancia)")
            lower_strike = st.number_input(
                "🎯 Precio de Ejercicio", 
                value=current_price * 0.97, 
                key=f"{prefix}pds_lower",
                help="Precio al que puedes vender las acciones si ejercitas la opción"
            )
            lower_premium = st.number_input(
                "💰 Costo de la Opción", 
                value=current_price * 0.01, 
                key=f"{prefix}pds_lower_prem",
                help="Lo que recibes por vender esta opción (vendes esta opción, recibes prima)"
            )
        
        # Calcular parámetros de la estrategia
        premium_paid = upper_premium - lower_premium
        max_profit = upper_strike - lower_strike - premium_paid
        max_loss = premium_paid
        
        # Mostrar resumen de costos
        st.markdown("### 💰 Resumen de Costos")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("💸 Pagas por PUT comprada", f"${upper_premium:.2f}")
        with col2:
            st.metric("💵 Recibes por PUT vendida", f"${lower_premium:.2f}")
        with col3:
            st.metric("💳 Costo Neto Total", f"${premium_paid:.2f}", delta_color="inverse" if premium_paid > 0 else "normal")
        
        # Configuración de gestión de riesgo
        expiration_date = get_next_business_days(datetime.now(), 3).strftime("%Y-%m-%d")
        risk_levels = risk_management_ui.render_risk_configuration(
            strategy_name, premium_paid, max_profit, max_loss, current_price, expiration_date
        )
        
        return {
            'upper_strike': upper_strike, 'lower_strike': lower_strike,
            'upper_premium': upper_premium, 'lower_premium': lower_premium,
            'risk_levels': risk_levels, 'expiration_date': expiration_date
        }
    
 