"""
Results Renderer Module - Functions for rendering strategy analysis results
"""

import streamlit as st
from typing import Dict, Any

def render_results(results, strategy_name: str, symbol: str, current_price: float, market_analysis: dict | None = None):
    """Render strategy results in a clean format."""
    
    st.markdown("---")
    st.subheader("📊 Resultados del Análisis")
    
    # Métricas principales
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("💰 Ganancia Máxima", f"${results.max_profit:.2f}")
    with col2:
        st.metric("💸 Pérdida Máxima", f"${abs(results.max_loss):.2f}")
    with col3:
        # Calcular ROI máximo
        total_investment = abs(results.max_loss)
        max_roi = (results.max_profit / total_investment) * 100 if total_investment > 0 else 0
        st.metric("📈 ROI Máximo", f"{max_roi:.1f}%")
    with col4:
        if results.breakeven_points:
            breakeven_str = f"${results.breakeven_points[0]:.2f}"
            if len(results.breakeven_points) > 1:
                breakeven_str += f", ${results.breakeven_points[1]:.2f}"
            st.metric("⚖️ Breakeven", breakeven_str)
        else:
            st.metric("⚖️ Breakeven", "N/A")
    
    # Métricas adicionales
    col5, col6, col7, col8 = st.columns(4)
    with col5:
        st.metric("🎯 Probabilidad", f"{results.profit_probability:.1%}")
    with col6:
        # Calcular ROI esperado basado en probabilidad
        expected_roi = max_roi * (results.profit_probability / 100)
        st.metric("🎲 ROI Esperado", f"{expected_roi:.1f}%")
    with col7:
        # Ratio riesgo/recompensa
        risk_reward_ratio = results.max_profit / abs(results.max_loss) if results.max_loss != 0 else 0
        st.metric("⚖️ R/R Ratio", f"{risk_reward_ratio:.2f}")
    with col8:
        # Días hasta expiración (si está disponible)
        if hasattr(results, 'days_to_expiration'):
            st.metric("📅 DTE", f"{results.days_to_expiration}")
        else:
            st.metric("📅 DTE", "N/A")
    
    # Resumen de la estrategia
    st.markdown("### 📋 Resumen de Estrategia")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.info(f"**Estrategia:** {strategy_name}")
    with col2:
        st.info(f"**Símbolo:** {symbol}")
    with col3:
        st.info(f"**Precio Actual:** ${current_price:.2f}")
    with col4:
        if market_analysis:
            trend = market_analysis.get('trend', 'Neutral')
            st.info(f"**Tendencia:** {trend}")
    
    # Instrucciones de ejecución
    with st.expander("📝 Instrucciones de Ejecución"):
        st.markdown(f"""
        ### 🎯 Instrucciones para {strategy_name}
        
        **1. Análisis de Resultados:**
        - Ganancia Máxima: ${results.max_profit:.2f}
        - Pérdida Máxima: ${abs(results.max_loss):.2f}
        - Probabilidad de Ganancia: {results.profit_probability:.1%}
        
        **2. Puntos de Breakeven:**
        - Niveles: {', '.join([f'${level:.2f}' for level in results.breakeven_points]) if results.breakeven_points else 'N/A'}
        
        **3. Gestión de Riesgo Recomendada:**
        - Stop Loss: ${abs(results.max_loss) * 0.5:.2f} (50% de pérdida máxima)
        - Take Profit: ${results.max_profit * 0.75:.2f} (75% de ganancia máxima)
        
        **4. Configuración de Estrategia:**
        - Tipo: {strategy_name}
        - Símbolo: {symbol}
        - Precio Actual: ${current_price:.2f}
        """) 