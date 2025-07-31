"""Sidebar component."""
import streamlit as st
from datetime import datetime

def render_sidebar():
    with st.sidebar:
        st.title("🎛️ Panel de Control")
        current_time = datetime.now().strftime("%H:%M:%S")
        st.text(f"🕐 {current_time}")
        
        st.markdown("---")
        st.subheader("⚙️ Configuración")
        auto_refresh = st.checkbox("Auto-refresh", value=True)
        theme = st.selectbox("Tema", ["Light", "Dark"], index=0)
        
        st.markdown("---")
        st.subheader("🧭 Navegación")
        
        # Navigation buttons
        if st.button("🏠 Inicio", use_container_width=True):
            st.session_state['current_page'] = 'home'
            st.rerun()
        
        if st.button("📊 Análisis", use_container_width=True):
            st.session_state['current_page'] = 'analysis'
            st.rerun()
        
        if st.button("💼 Trading", use_container_width=True):
            st.session_state['current_page'] = 'trading'
            st.rerun()
        
        if st.button("📈 Monitor", use_container_width=True):
            st.session_state['current_page'] = 'monitor'
            st.rerun()
        
        if st.button("🤖 Backtesting", use_container_width=True):
            st.session_state['current_page'] = 'backtesting'
            st.rerun()
        
        st.markdown("---")
        st.subheader("📊 Estado del Mercado")
        market_open = datetime.now().hour >= 9 and datetime.now().hour < 16
        if market_open:
            st.success("🟢 Mercado Abierto")
        else:
            st.error("🔴 Mercado Cerrado")
        
        st.metric("S&P 500", "4,500.00", "1.2%")
        st.metric("NASDAQ", "14,000.00", "0.8%")
        st.metric("VIX", "18.50", "-2.1%")
