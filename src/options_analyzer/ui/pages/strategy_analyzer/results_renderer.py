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
    
    # Conclusión y recomendación final
    st.markdown("### 🎯 CONCLUSIÓN Y RECOMENDACIÓN FINAL")
    
    # Evaluación del timing
    timing_score = 0
    timing_factors = []
    
    if market_analysis:
        trend = market_analysis.get('trend', 'Neutral')
        rsi = market_analysis.get('rsi', 50)
        volatility = market_analysis.get('volatility', 20)
        
        # Evaluar timing basado en tendencia y estrategia
        if (strategy_name == "Call Debit Spread" and trend == "Uptrend"):
            timing_score += 2
            timing_factors.append("✅ Tendencia alcista favorable para Call Debit Spread")
        elif (strategy_name == "Put Debit Spread" and trend == "Downtrend"):
            timing_score += 2
            timing_factors.append("✅ Tendencia bajista favorable para Put Debit Spread")
        else:
            timing_score -= 1
            timing_factors.append("❌ Tendencia no óptima para la estrategia")
        
        # Evaluar RSI
        if rsi > 70:
            timing_score -= 1
            timing_factors.append("❌ RSI sobrecomprado - posible corrección")
        elif rsi < 30:
            timing_score -= 1
            timing_factors.append("❌ RSI sobrevendido - posible rebote")
        else:
            timing_score += 1
            timing_factors.append("✅ RSI en rango normal")
        
        # Evaluar volatilidad
        if volatility > 30:
            timing_score += 1
            timing_factors.append("✅ Alta volatilidad - bueno para opciones")
        elif volatility < 15:
            timing_score -= 1
            timing_factors.append("❌ Baja volatilidad - primas baratas")
    
    # Riesgos identificados
    risk_score = 0
    risk_factors = []
    
    # Evaluar ratio riesgo/recompensa
    risk_reward_ratio = results.max_profit / abs(results.max_loss) if results.max_loss != 0 else 0
    if risk_reward_ratio >= 2.0:
        risk_score += 2
        risk_factors.append("✅ Excelente ratio R/R (≥2.0)")
    elif risk_reward_ratio >= 1.5:
        risk_score += 1
        risk_factors.append("✅ Buen ratio R/R (≥1.5)")
    elif risk_reward_ratio >= 1.0:
        risk_score += 0
        risk_factors.append("⚠️ Ratio R/R aceptable (≥1.0)")
    else:
        risk_score -= 1
        risk_factors.append("❌ Ratio R/R pobre (<1.0)")
    
    # Evaluar probabilidad de ganancia
    if results.profit_probability >= 60:
        risk_score += 1
        risk_factors.append("✅ Alta probabilidad de ganancia")
    elif results.profit_probability >= 40:
        risk_score += 0
        risk_factors.append("⚠️ Probabilidad moderada")
    else:
        risk_score -= 1
        risk_factors.append("❌ Baja probabilidad de ganancia")
    
    # Evaluar tamaño de la posición
    max_loss_amount = abs(results.max_loss)
    if max_loss_amount <= 100:
        risk_score += 1
        risk_factors.append("✅ Pérdida máxima controlada")
    elif max_loss_amount <= 500:
        risk_score += 0
        risk_factors.append("⚠️ Pérdida máxima moderada")
    else:
        risk_score -= 1
        risk_factors.append("❌ Pérdida máxima alta")
    
    # Recomendación final
    total_score = timing_score + risk_score
    recommendation = ""
    justification = []
    
    if total_score >= 4:
        recommendation = "✅ EJECUTAR"
        justification.append("• Timing favorable y riesgos controlados")
        justification.append("• Ratio riesgo/recompensa atractivo")
        justification.append("• Condiciones de mercado óptimas")
    elif total_score >= 2:
        recommendation = "⚠️ EJECUTAR CON PRECAUCIÓN"
        justification.append("• Algunos factores favorables")
        justification.append("• Considerar ajustar parámetros")
        justification.append("• Monitorear condiciones de mercado")
    elif total_score >= 0:
        recommendation = "⏸️ ESPERAR MEJORES CONDICIONES"
        justification.append("• Timing no óptimo")
        justification.append("• Riesgos moderados")
        justification.append("• Considerar estrategia alternativa")
    else:
        recommendation = "❌ NO EJECUTAR"
        justification.append("• Timing desfavorable")
        justification.append("• Riesgos elevados")
        justification.append("• Condiciones de mercado adversas")
    
    # Mostrar evaluación
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📊 Evaluación del Timing")
        for factor in timing_factors:
            st.write(factor)
        st.metric("Puntuación Timing", f"{timing_score}/3")
    
    with col2:
        st.markdown("#### ⚠️ Riesgos Identificados")
        for factor in risk_factors:
            st.write(factor)
        st.metric("Puntuación Riesgo", f"{risk_score}/5")
    
    # Recomendación final
    st.markdown("#### 🎯 Recomendación Final")
    
    if recommendation.startswith("✅"):
        st.success(f"**{recommendation}**")
    elif recommendation.startswith("⚠️"):
        st.warning(f"**{recommendation}**")
    elif recommendation.startswith("⏸️"):
        st.info(f"**{recommendation}**")
    else:
        st.error(f"**{recommendation}**")
    
    st.markdown("**Justificación:**")
    for point in justification:
        st.write(point)
    
    st.metric("**Puntuación Total**", f"{total_score}/8")
    
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