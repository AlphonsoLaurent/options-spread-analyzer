"""
Panel de Monitoreo de Posiciones con Gestión de Riesgo
"""

import streamlit as st
from datetime import datetime, timedelta
import sys
from pathlib import Path

# Add core directory to sys.path for imports
current_file = Path(__file__)
core_dir = current_file.parent.parent.parent / "core"
sys.path.insert(0, str(core_dir))

try:
    from ...core.risk_management import risk_management_system, risk_management_ui
except ImportError:
    from core.risk_management import risk_management_system, risk_management_ui


def initialize_session_state():
    """Initialize session state for position monitoring."""
    if 'monitored_positions' not in st.session_state:
        st.session_state['monitored_positions'] = {}
    
    if 'position_counter' not in st.session_state:
        st.session_state['position_counter'] = 0


def create_demo_position():
    """Crea una posición de demostración para mostrar el sistema."""
    position_id = f"DEMO_{st.session_state['position_counter']}"
    st.session_state['position_counter'] += 1
    
    # Datos de ejemplo
    symbol = "AAPL"
    strategy_name = "Call Debit Spread"
    premium_paid = 2.50
    max_profit = 7.50
    max_loss = 2.50
    current_price = 213.76
    expiration_date = (datetime.now() + timedelta(days=14)).strftime("%Y-%m-%d")
    
    # Crear niveles de riesgo
    from ...core.risk_management import RiskLevels
    risk_levels = RiskLevels(
        stop_loss_usd=max_loss * 0.5,  # 50% de pérdida máxima
        take_profit_usd=max_profit * 0.75,  # 75% de ganancia máxima
        stop_loss_percent=50.0,
        take_profit_percent=75.0,
        dte_alert=21,
        max_loss_usd=max_loss,
        max_profit_usd=max_profit
    )
    
    # Agregar posición al sistema
    risk_management_system.add_position(
        position_id=position_id,
        symbol=symbol,
        strategy_name=strategy_name,
        risk_levels=risk_levels,
        entry_date=datetime.now().strftime("%Y-%m-%d"),
        expiration_date=expiration_date,
        initial_premium=premium_paid
    )
    
    # P&L inicial (se actualizará con datos reales)
    current_pnl = 0.0
    risk_management_system.update_position_pnl(position_id, current_pnl)
    
    st.session_state['monitored_positions'][position_id] = {
        'symbol': symbol,
        'strategy_name': strategy_name,
        'current_pnl': current_pnl,
        'entry_date': datetime.now().strftime("%Y-%m-%d"),
        'expiration_date': expiration_date
    }
    
    return position_id


def render_position_summary():
    """Renderiza el resumen general de todas las posiciones."""
    positions = risk_management_system.get_all_positions()
    
    if not positions:
        st.info("📊 No hay posiciones monitoreadas. Crea una posición de demostración para comenzar.")
        if st.button("🎯 Crear Posición Demo", type="primary"):
            create_demo_position()
            st.rerun()
        return
    
    st.markdown("### 📊 Resumen de Posiciones")
    
    # Métricas generales
    total_positions = len(positions)
    total_pnl = sum(pos['current_pnl_usd'] for pos in positions.values())
    profitable_positions = sum(1 for pos in positions.values() if pos['current_pnl_usd'] > 0)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Posiciones Activas", total_positions)
    
    with col2:
        pnl_color = "normal" if total_pnl >= 0 else "inverse"
        st.metric("P&L Total", f"${total_pnl:.2f}", delta_color=pnl_color)
    
    with col3:
        win_rate = (profitable_positions / total_positions * 100) if total_positions > 0 else 0
        st.metric("Win Rate", f"{win_rate:.1f}%")
    
    with col4:
        active_alerts = sum(
            len([alert for alert in pos['status'].alerts if alert['status'].value == 'active'])
            for pos in positions.values()
        )
        st.metric("Alertas Activas", active_alerts, delta_color="inverse" if active_alerts > 0 else "normal")
    
    # Tabla de posiciones
    st.markdown("### 📋 Posiciones Activas")
    
    for position_id, position_data in positions.items():
        with st.expander(f"{position_data['symbol']} - {position_data['strategy_name']} (ID: {position_id})"):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                pnl = position_data['current_pnl_usd']
                pnl_color = "normal" if pnl >= 0 else "inverse"
                st.metric("P&L", f"${pnl:.2f}", delta_color=pnl_color)
            
            with col2:
                dte = position_data['status'].dte_remaining
                st.metric("DTE", dte)
            
            with col3:
                risk_level = position_data['status'].risk_level.value.upper()
                risk_color = "inverse" if risk_level in ["HIGH", "CRITICAL"] else "normal"
                st.metric("Riesgo", risk_level, delta_color=risk_color)
            
            # Botones de acción
            col_a, col_b, col_c = st.columns(3)
            
            with col_a:
                if st.button("📊 Ver Detalles", key=f"details_{position_id}"):
                    st.session_state['selected_position'] = position_id
            
            with col_b:
                if st.button("🔄 Actualizar P&L", key=f"update_{position_id}"):
                    # Actualizar P&L con datos reales (funcionalidad en desarrollo)
                    st.info("🔄 Actualización de P&L en tiempo real en desarrollo")
                    st.rerun()
            
            with col_c:
                if st.button("❌ Cerrar", key=f"close_{position_id}"):
                    risk_management_system.close_position(position_id, "Manual")
                    st.rerun()


def render_position_details(position_id: str):
    """Renderiza los detalles completos de una posición específica."""
    position_data = risk_management_system.get_all_positions().get(position_id)
    
    if not position_data:
        st.error("Posición no encontrada")
        return
    
    st.markdown("---")
    st.markdown(f"### 📊 Detalles de Posición: {position_data['symbol']}")
    
    # Información básica
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.info(f"**Estrategia:** {position_data['strategy_name']}")
        st.info(f"**Fecha de Entrada:** {position_data['entry_date']}")
    
    with col2:
        st.info(f"**Fecha de Expiración:** {position_data['expiration_date']}")
        st.info(f"**Prima Inicial:** ${position_data['initial_premium']:.2f}")
    
    with col3:
        st.info(f"**DTE Restante:** {position_data['status'].dte_remaining}")
        st.info(f"**Última Actualización:** {position_data['status'].last_updated.strftime('%H:%M:%S')}")
    
    # Panel de monitoreo en tiempo real
    risk_management_ui.render_monitoring_panel(position_id)
    
    # Simulador de P&L
    st.markdown("### 🎮 Simulador de P&L")
    st.markdown("Ajusta el P&L para ver cómo cambian las alertas y recomendaciones:")
    
    col1, col2 = st.columns(2)
    
    with col1:
        current_pnl = st.slider(
            "P&L Actual ($)",
            min_value=-position_data['risk_levels'].max_loss_usd,
            max_value=position_data['risk_levels'].max_profit_usd,
            value=position_data['current_pnl_usd'],
            step=0.1,
            key=f"pnl_slider_{position_id}"
        )
    
    with col2:
        if st.button("🔄 Aplicar P&L", key=f"apply_pnl_{position_id}"):
            risk_management_system.update_position_pnl(position_id, current_pnl)
            st.rerun()
    
    # Mostrar niveles de riesgo
    st.markdown("### 🎯 Niveles de Gestión")
    
    risk_levels = position_data['risk_levels']
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Stop Loss",
            f"${risk_levels.stop_loss_usd:.2f}",
            f"{risk_levels.stop_loss_percent:.0f}%",
            delta_color="inverse"
        )
    
    with col2:
        st.metric(
            "Take Profit",
            f"${risk_levels.take_profit_usd:.2f}",
            f"{risk_levels.take_profit_percent:.0f}%",
            delta_color="normal"
        )
    
    with col3:
        st.metric(
            "Pérdida Máx.",
            f"${risk_levels.max_loss_usd:.2f}",
            "100%"
        )
    
    with col4:
        st.metric(
            "Ganancia Máx.",
            f"${risk_levels.max_profit_usd:.2f}",
            "100%"
        )


def render_alert_center():
    """Renderiza el centro de alertas global."""
    st.markdown("---")
    st.markdown("### 🚨 Centro de Alertas")
    
    # Obtener todas las alertas activas
    all_positions = risk_management_system.get_all_positions()
    active_alerts = []
    
    for position_id, position_data in all_positions.items():
        for alert in position_data['status'].alerts:
            if alert['status'].value == 'active':
                alert['position_id'] = position_id
                alert['symbol'] = position_data['symbol']
                active_alerts.append(alert)
    
    if not active_alerts:
        st.success("✅ No hay alertas activas en este momento")
        return
    
    # Mostrar alertas activas
    for alert in active_alerts:
        if alert['type'] == 'stop_loss':
            st.error(f"🚨 **{alert['symbol']}** - {alert['message']}")
        elif alert['type'] == 'take_profit':
            st.success(f"🎯 **{alert['symbol']}** - {alert['message']}")
        elif alert['type'] == 'dte_warning':
            st.warning(f"⏰ **{alert['symbol']}** - {alert['message']}")
        
        st.info(f"💡 **Recomendación:** {alert['recommendation']}")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button(f"Ver Posición {alert['symbol']}", key=f"view_{alert['position_id']}"):
                st.session_state['selected_position'] = alert['position_id']
        with col2:
            if st.button(f"Cerrar Alerta", key=f"close_alert_{alert['position_id']}_{alert['type']}"):
                alert['status'] = 'closed'
                st.rerun()


def render():
    """Renderiza la página principal del panel de monitoreo."""
    st.markdown('<h1 class="main-header">📈 Panel de Monitoreo de Posiciones</h1>', unsafe_allow_html=True)
    st.markdown("### Sistema de Gestión de Riesgo Automático en Tiempo Real")
    
    initialize_session_state()
    
    # Navegación por pestañas
    tab1, tab2, tab3 = st.tabs(["📊 Resumen", "🎯 Posición Detallada", "🚨 Alertas"])
    
    with tab1:
        render_position_summary()
    
    with tab2:
        if 'selected_position' in st.session_state:
            render_position_details(st.session_state['selected_position'])
        else:
            st.info("👆 Selecciona una posición desde el resumen para ver sus detalles")
    
    with tab3:
        render_alert_center()
    
    # Botón para volver al análisis
    if st.button("🔙 Volver al Análisis", type="secondary"):
        st.session_state['current_page'] = 'analysis'
        st.rerun()


if __name__ == "__main__":
    render() 