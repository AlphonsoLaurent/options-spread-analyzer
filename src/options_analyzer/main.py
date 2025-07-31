"""
Options Spread Strategy Analyzer - Main Application
ALTERNATIVA ROBUSTA: Navegación manual más estable
"""

import streamlit as st
import sys
from pathlib import Path

# Add src to path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir.parent))

# Imports
from options_analyzer.ui.pages import strategy_analyzer, paper_trading, position_monitor, backtesting
from options_analyzer.ui.components.sidebar import render_sidebar


def configure_app():
    """Configure Streamlit app."""
    st.set_page_config(
        page_title="Options Strategy Analyzer",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Custom CSS
    st.markdown("""
    <style>
    /* Eliminar márgenes y padding globales de Streamlit */
    .main .block-container {
        padding-top: 1rem !important;
        padding-bottom: 1rem !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
    }
    
    /* Reducir espacio del header principal */
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem !important;
        margin-top: 0 !important;
        padding-top: 0 !important;
    }
    
    /* Eliminar márgenes de elementos de Streamlit */
    .stMarkdown {
        margin-top: 0 !important;
        margin-bottom: 0.5rem !important;
    }
    
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
        margin-top: 0 !important;
        margin-bottom: 0.5rem !important;
    }
    
    .metric-container {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .nav-button {
        width: 100%;
        margin: 0.2rem 0;
    }
    
    /* Estilo para pestañas de navegación elegantes */
    .nav-tabs {
        display: flex;
        background: #f1f5f9;
        border-radius: 12px;
        padding: 4px;
        margin: 8px 0 !important;
    }
    
    .nav-tab {
        flex: 1;
        padding: 12px 16px;
        border-radius: 8px;
        border: none;
        background: transparent;
        font-weight: 600;
        font-size: 14px;
        transition: all 0.2s ease;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 8px;
    }
    
    .nav-tab.active {
        background: white;
        color: #1a202c;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    }
    
    .nav-tab:not(.active) {
        color: #64748b;
    }
    
    .nav-tab:hover:not(.active) {
        background: rgba(255, 255, 255, 0.5);
        color: #1a202c;
    }
    
    /* Estilo para botones de navegación */
    [data-testid="stButton"] {
        border-radius: 8px !important;
        font-weight: 600 !important;
        transition: all 0.2s ease !important;
    }
    
    [data-testid="stButton"]:hover {
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15) !important;
    }
    </style>
    """, unsafe_allow_html=True)


def initialize_session_state():
    """Initialize session state."""
    defaults = {
        'current_page': 'analysis',  # Cambiar a 'analysis' por defecto
        'portfolio': None,
        'market_data_cache': {},
        'analysis_results': {},
        'user_preferences': {'theme': 'light', 'auto_refresh': True}
    }

    for key, default_value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default_value


def render_navigation():
    """Render navigation buttons with elegant tab style."""
    st.markdown("### 🧭 Navegación")
    
    # Determinar pestaña activa
    current_page = st.session_state.get('current_page', 'analysis')
    
    # Renderizar pestañas con estilo elegante usando botones nativos
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("📊 Análisis", key="nav_analysis", use_container_width=True, 
                    type="primary" if current_page == 'analysis' else "secondary"):
            st.session_state['current_page'] = 'analysis'
            st.rerun()
    
    with col2:
        if st.button("💼 Trading", key="nav_trading", use_container_width=True,
                    type="primary" if current_page == 'trading' else "secondary"):
            st.session_state['current_page'] = 'trading'
            st.rerun()
    
    with col3:
        if st.button("📈 Monitoreo", key="nav_monitor", use_container_width=True,
                    type="primary" if current_page == 'monitor' else "secondary"):
            st.session_state['current_page'] = 'monitor'
            st.rerun()


def render_current_page():
    """Render the currently selected page."""
    current_page = st.session_state.get('current_page', 'analysis')

    try:
        if current_page == 'analysis':
            strategy_analyzer.render()
        elif current_page == 'trading':
            paper_trading.render()
        elif current_page == 'monitor':
            position_monitor.render()
        elif current_page == 'backtesting':
            backtesting.render()
        else:
            # Default to analysis
            st.session_state['current_page'] = 'analysis'
            strategy_analyzer.render()
    except Exception as e:
        st.error(f"Error renderizando página '{current_page}': {str(e)}")
        st.exception(e)
        # Fallback to analysis page
        st.session_state['current_page'] = 'analysis'
        try:
            strategy_analyzer.render()
        except Exception as fallback_error:
            st.error(f"Error crítico: {str(fallback_error)}")


def main():
    """Main function."""
    try:
        configure_app()
        initialize_session_state()
        render_sidebar()
        st.markdown('<h1 class="main-header">📊 Options Spread Strategy Analyzer</h1>', unsafe_allow_html=True)
        st.markdown("### Análisis Paso a Paso de Estrategias de Opciones")
        render_navigation()
        render_current_page()

    except Exception as e:
        st.error(f"Error crítico en la aplicación: {str(e)}")
        st.exception(e)

        # Emergency fallback
        st.markdown("## 🚨 Modo de Emergencia")
        st.markdown("La aplicación tuvo un error crítico. Mostrando interfaz básica:")

        if st.button("🔄 Reiniciar Aplicación"):
            # Clear session state
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()


if __name__ == "__main__":
    main()
