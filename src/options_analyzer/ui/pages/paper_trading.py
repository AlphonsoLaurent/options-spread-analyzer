"""Paper trading page."""
import streamlit as st
from datetime import datetime
import sys
from pathlib import Path

# Add core directory to sys.path for imports
current_file = Path(__file__)
core_dir = current_file.parent.parent.parent / "core"
sys.path.insert(0, str(core_dir))

from paper_trading import PaperTradingEngine, Portfolio, Order

# Lista de estrategias de spreads verticales
AVAILABLE_STRATEGIES = [
    "Call Debit Spread",
    "Put Debit Spread"
]

def initialize_trading_components():
    """Initialize trading components with proper error handling."""
    try:
        # Step 1: Ensure Portfolio exists and is valid
        if 'portfolio' not in st.session_state or st.session_state['portfolio'] is None:
            st.session_state['portfolio'] = Portfolio(
                name="Default Portfolio",
                initial_cash=100000.0,
                current_cash=100000.0
            )

        # Step 2: Validate portfolio object
        portfolio = st.session_state['portfolio']
        if not hasattr(portfolio, 'current_cash') or portfolio.current_cash is None:
            st.error("Error: Portfolio inválido - recreando...")
            st.session_state['portfolio'] = Portfolio(
                name="Default Portfolio",
                initial_cash=100000.0,
                current_cash=100000.0
            )
            portfolio = st.session_state['portfolio']

        # Step 3: Ensure TradingEngine exists and is valid
        if ('trading_engine' not in st.session_state or
                st.session_state['trading_engine'] is None or
                getattr(st.session_state.get('trading_engine'), 'portfolio', None) is None):

            st.session_state['trading_engine'] = PaperTradingEngine(portfolio)

        # Step 4: Final validation
        engine = st.session_state['trading_engine']
        if not hasattr(engine, 'portfolio') or engine.portfolio is None:
            st.error("Error crítico: Engine sin portfolio válido")
            return False

        # Step 5: Ensure engine portfolio has required attributes
        if not hasattr(engine.portfolio, 'current_cash'):
            st.error("Error crítico: Portfolio sin current_cash")
            return False

        return True

    except Exception as e:
        st.error(f"Error inicializando componentes de trading: {str(e)}")
        return False


def render():
    st.title("💼 Paper Trading")

    # Initialize components with error handling
    if not initialize_trading_components():
        st.stop()

    # Verify components are properly initialized
    engine = st.session_state.get('trading_engine')
    portfolio = st.session_state.get('portfolio')

    if engine is None or portfolio is None:
        st.error("Error: Componentes de trading no inicializados correctamente")
        if st.button("🔄 Reinicializar Componentes"):
            if 'portfolio' in st.session_state:
                del st.session_state['portfolio']
            if 'trading_engine' in st.session_state:
                del st.session_state['trading_engine']
            st.rerun()
        st.stop()

    col1, col2 = st.columns([1, 2])

    with col1:
        st.subheader("📊 Resumen del Portafolio")

        try:
            if hasattr(engine, 'get_performance_metrics'):
                metrics = engine.get_performance_metrics()
            else:
                metrics = {
                    'total_value': getattr(portfolio, 'current_cash', 100000),
                    'available_cash': getattr(portfolio, 'current_cash', 100000),
                    'total_return': 0.0,
                    'trades_count': len(getattr(engine, 'trade_history', []))
                }

            st.metric("Valor Total", f"${metrics['total_value']:,.2f}")
            st.metric("Efectivo", f"${metrics['available_cash']:,.2f}")
            st.metric("Retorno", f"{metrics['total_return']:.2f}%")
            st.metric("Trades", f"{metrics['trades_count']}")

        except Exception as e:
            st.error(f"Error obteniendo métricas: {str(e)}")
            st.metric("Valor Total", "$100,000.00")
            st.metric("Efectivo", "$100,000.00")
            st.metric("Retorno", "0.00%")
            st.metric("Trades", "0")

        st.subheader("📝 Nueva Orden")
        with st.form("new_order_form"):
            symbol = st.text_input("Símbolo", value="AAPL").upper()
            strategy_type = st.selectbox("Estrategia", AVAILABLE_STRATEGIES)
            quantity = st.number_input("Cantidad", min_value=1, value=1)
            price = st.number_input("Precio", min_value=0.01, value=100.0)

            if st.form_submit_button("🚀 Ejecutar Orden", type="primary"):
                try:
                    order = Order(symbol=symbol, strategy_type=strategy_type, quantity=quantity, price=price * quantity)

                    if hasattr(engine, 'place_order'):
                        result = engine.place_order(order)

                        if "Insufficient" in str(result):
                            st.error(f"❌ {result}")
                        else:
                            st.success(f"✅ Orden ejecutada! ID: {str(result)[:8]}")
                            st.rerun()
                    else:
                        st.error("Error: Engine no tiene método place_order")

                except Exception as e:
                    st.error(f"Error ejecutando orden: {str(e)}")

    with col2:
        st.subheader("📋 Posiciones Actuales")

        try:
            if hasattr(portfolio, 'positions') and portfolio.positions:
                st.dataframe(portfolio.positions, use_container_width=True)
            else:
                st.info("No hay posiciones abiertas")
        except Exception as e:
            st.error(f"Error mostrando posiciones: {str(e)}")
            st.info("No hay posiciones abiertas")

        st.subheader("📜 Historial de Trades")
        try:
            if hasattr(engine, 'trade_history') and engine.trade_history:
                history_data = []
                for trade in engine.trade_history[-10:]:
                    history_data.append({
                        'Fecha': trade.get('timestamp', datetime.now()).strftime('%Y-%m-%d %H:%M'),
                        'Símbolo': trade.get('symbol', 'N/A'),
                        'Precio': f"${trade.get('price', 0):.2f}",
                        'ID': str(trade.get('order_id', 'N/A'))[:8]
                    })
                st.dataframe(history_data, use_container_width=True)
            else:
                st.info("No hay historial de trades")
        except Exception as e:
            st.error(f"Error mostrando historial: {str(e)}")
            st.info("No hay historial de trades")
