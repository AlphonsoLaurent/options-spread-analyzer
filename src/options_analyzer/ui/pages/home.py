"""Home page."""
import streamlit as st

def render():
    st.markdown('<h1 class="main-header">📊 Options Spread Strategy Analyzer</h1>', unsafe_allow_html=True)
    st.markdown("Bienvenido al analizador profesional de estrategias de opciones.")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("📊 Nuevo Análisis", type="primary", use_container_width=True):
            st.session_state['current_page'] = 'analysis'
            st.rerun()
    with col2:
        if st.button("💼 Paper Trading", use_container_width=True):
            st.session_state['current_page'] = 'trading'
            st.rerun()
    with col3:
        if st.button("📚 Centro Educativo", use_container_width=True):
            st.info("Próximamente disponible")
    
    st.markdown("---")
    st.subheader("📈 Resumen del Mercado")
    symbols = ['AAPL', 'GOOGL', 'MSFT', 'TSLA']
    for symbol in symbols:
        col_a, col_b, col_c = st.columns([1, 1, 1])
        with col_a:
            st.metric(symbol, "$150.00")
        with col_b:
            st.metric("Cambio", "+2.5%", delta="2.5%")
        with col_c:
            st.metric("Volumen", "1.2M")
