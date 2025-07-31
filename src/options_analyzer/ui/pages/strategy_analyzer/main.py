"""
Main Strategy Analyzer Module - Orchestrates all strategy analysis functionality
"""

import streamlit as st
from datetime import datetime, timedelta
from typing import Dict, Any

from .market_analysis import analyze_market_conditions, analyze_advanced_context
from .strategy_inputs import get_strategy_inputs
from .strategy_calculations import (
    calculate_moneyness, validate_strike_coherence, calculate_basic_greeks,
    calculate_itm_probability, get_technical_levels_distance
)
from .results_renderer import render_results
from .position_analysis import render_position_analysis

# Import strategy classes
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))
from core.options_strategies import (
    CallDebitSpread, CallCreditSpread, PutDebitSpread, PutCreditSpread
)
from data.market_data import get_market_data

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

# Strategy definitions
STRATEGIES = {
    "Call Debit Spread": {
        "type": "Bullish",
        "description": "Compras calls y vendes calls más caras para reducir costo",
        "color": "green"
    },
    "Put Debit Spread": {
        "type": "Bearish", 
        "description": "Compras puts y vendes puts más baratas para reducir costo",
        "color": "red"
    }
}

def create_strategy(strategy_name: str, current_price: float, params: dict, expiration: str):
    """Create strategy instance."""
    if strategy_name == "Call Debit Spread":
        strategy = CallDebitSpread(current_price)
        strategy.add_legs(params['lower_strike'], params['upper_strike'], 
                         params['lower_premium'], params['upper_premium'], expiration)
    
    elif strategy_name == "Put Debit Spread":
        strategy = PutDebitSpread(current_price)
        strategy.add_legs(params['upper_strike'], params['lower_strike'], 
                         params['upper_premium'], params['lower_premium'], expiration)
    
    return strategy

def render():
    """Main render function for strategy analyzer page."""
    
    # No custom CSS - completely native design
    
    # Initialize session state
    if 'current_step' not in st.session_state:
        st.session_state['current_step'] = 1
    if 'main_symbol' not in st.session_state:
        st.session_state['main_symbol'] = None
    if 'market_analysis' not in st.session_state:
        st.session_state['market_analysis'] = None
    if 'results' not in st.session_state:
        st.session_state['results'] = None
    
    # Auto-refresh system
    if 'auto_refresh' not in st.session_state:
        st.session_state['auto_refresh'] = True
    if 'last_update' not in st.session_state:
        st.session_state['last_update'] = datetime.now()
    if 'last_data_update' not in st.session_state:
        st.session_state['last_data_update'] = datetime.now()
    
    # Auto-refresh toggle
    col1, col2 = st.columns([3, 1])
    with col1:
        auto_refresh = st.toggle(
            "🔄 Auto-Refresh (30s)", 
            value=st.session_state['auto_refresh'],
            help="Actualización automática de datos cada 30 segundos"
        )
    with col2:
        if st.button("🔄 Actualizar Ahora", type="secondary"):
            st.session_state['last_data_update'] = datetime.now()
            st.session_state['last_update'] = datetime.now()
            st.rerun()
    
    # Update auto-refresh state
    st.session_state['auto_refresh'] = auto_refresh
    
    # Auto-refresh logic - only update data, not the entire page
    if auto_refresh:
        time_since_data_update = (datetime.now() - st.session_state['last_data_update']).total_seconds()
        if time_since_data_update >= 30:
            st.session_state['last_data_update'] = datetime.now()
            # Don't rerun here - let the data fetching functions handle caching
    
    # Show last update time
    time_since_update = (datetime.now() - st.session_state['last_update']).total_seconds()
    if time_since_update < 60:
        update_color = "🟢"
        update_text = f"Última actualización: hace {int(time_since_update)}s"
    elif time_since_update < 300:
        update_color = "🟡"
        update_text = f"Última actualización: hace {int(time_since_update/60)}m"
    else:
        update_color = "🔴"
        update_text = f"Última actualización: hace {int(time_since_update/60)}m"
    
    st.caption(f"{update_color} {update_text}")
    
    # === PASO 1: SELECCIONAR ACTIVO FINANCIERO ===
    if st.session_state['current_step'] >= 1:
        st.subheader("🎯 PASO 1: SELECCIONAR ACTIVO FINANCIERO")
        
        # Search input
        symbol_input = st.text_input(
            "🔍 Buscar activo",
            value=st.session_state.get('main_symbol', ''),
            placeholder="Ej: AAPL, TSLA, SPY...",
            help="Ingresa el símbolo del activo que quieres analizar"
        )
        
        # Initialize session state for tabs and recent assets
        if 'selected_tab' not in st.session_state:
            st.session_state['selected_tab'] = 'populares'
        if 'recent_assets' not in st.session_state:
            st.session_state['recent_assets'] = []
        
        # Tabs for Populares and Recientes
        tab1, tab2 = st.tabs(["⭐ Populares", "🕒 Recientes"])
        
        with tab1:
            # Popular assets - Grid de 20 elementos (5x4)
            popular_symbols = [
                ("AAPL", "Apple Inc.", "STOCK"),
                ("GOOGL", "Alphabet Inc.", "STOCK"),
                ("TSLA", "Tesla Inc.", "STOCK"),
                ("SPY", "SPDR S&P 500 ETF", "ETF"),
                ("QQQ", "Invesco QQQ Trust", "ETF"),
                ("NVDA", "NVIDIA Corp.", "STOCK"),
                ("MSFT", "Microsoft Corp.", "STOCK"),
                ("AMZN", "Amazon.com Inc.", "STOCK"),
                ("META", "Meta Platforms", "STOCK"),
                ("NFLX", "Netflix Inc.", "STOCK"),
                ("AMD", "Advanced Micro Devices", "STOCK"),
                ("VST", "Vistra Corp.", "STOCK"),
                ("APP", "Applovin Corp.", "STOCK"),
                ("PLTR", "Palantir Technologies", "STOCK"),
                ("HOOD", "Robinhood Markets", "STOCK"),
                ("SCHD", "Schwab US Dividend Equity ETF", "ETF"),
                ("VUG", "Vanguard Growth ETF", "ETF"),
                ("DIA", "SPDR Dow Jones ETF", "ETF"),
                ("IWM", "iShares Russell 2000 ETF", "ETF"),
                ("GLD", "SPDR Gold Shares ETF", "ETF"),
                ("TLT", "iShares 20+ Year ETF", "ETF")
            ]
            
            # Grid de 20 elementos en 5 filas x 4 columnas
            for row in range(5):
                cols = st.columns(4)
                for col in range(4):
                    idx = row * 4 + col
                    if idx < len(popular_symbols):
                        symbol, name, asset_type = popular_symbols[idx]
                        with cols[col]:
                            is_selected = st.session_state.get('main_symbol') == symbol
                            button_text = f"{symbol} {asset_type}"
                            
                            if st.button(button_text, key=f"symbol_{symbol}", 
                                       use_container_width=True,
                                       type="primary" if is_selected else "secondary"):
                                st.session_state['main_symbol'] = symbol
                                st.session_state['current_step'] = 2
                                
                                # Add to recent assets
                                if symbol not in st.session_state['recent_assets']:
                                    st.session_state['recent_assets'].insert(0, symbol)
                                    st.session_state['recent_assets'] = st.session_state['recent_assets'][:10]
                                
                                st.rerun()
        
        with tab2:
            # Recent assets
            recent_assets = st.session_state.get('recent_assets', [])
            if recent_assets:
                # Show recent assets in a grid
                for row in range(0, len(recent_assets), 4):
                    cols = st.columns(4)
                    for col in range(4):
                        if row + col < len(recent_assets):
                            symbol = recent_assets[row + col]
                            with cols[col]:
                                is_selected = st.session_state.get('main_symbol') == symbol
                                if st.button(symbol, key=f"recent_{symbol}", 
                                           use_container_width=True,
                                           type="primary" if is_selected else "secondary"):
                                    st.session_state['main_symbol'] = symbol
                                    st.session_state['current_step'] = 2
                                    st.rerun()
            else:
                st.info("No hay símbolos recientes. Selecciona algunos símbolos populares para que aparezcan aquí.")
        
        # Analyze button
        if st.button("🚀 ANÁLISIS RÁPIDO", type="primary", use_container_width=True):
            if symbol_input:
                st.session_state['main_symbol'] = symbol_input.upper()
                st.session_state['current_step'] = 2
                
                # Add to recent assets
                if symbol_input.upper() not in st.session_state['recent_assets']:
                    st.session_state['recent_assets'].insert(0, symbol_input.upper())
                    st.session_state['recent_assets'] = st.session_state['recent_assets'][:10]
                
                st.rerun()
            else:
                st.error("❌ Ingresa un símbolo válido")
    
    # === PASO 2: ANÁLISIS DE MERCADO ===
    if st.session_state['current_step'] >= 2 and st.session_state['main_symbol']:
        st.subheader("📊 PASO 2: ANÁLISIS DE MERCADO")
        
        symbol = st.session_state['main_symbol']
        
        # Get market data
        market_data = get_market_data(symbol)
        if market_data:
            current_price = market_data['current_price']
            
            # Perform market analysis
            with st.spinner(f"📊 Analizando {symbol}..."):
                market_analysis = analyze_market_conditions(symbol, current_price)
                market_analysis = analyze_advanced_context(symbol, current_price, market_analysis)
                st.session_state['market_analysis'] = market_analysis
            
            # Display analysis results
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                trend_color = "🟢" if market_analysis['trend'] == "Uptrend" else "🔴" if market_analysis['trend'] == "Downtrend" else "🟡"
                st.metric("📈 Tendencia", f"{trend_color} {market_analysis['trend']}")
            
            with col2:
                rsi_value = market_analysis['rsi']
                rsi_color = "🟢" if rsi_value < 70 else "🔴" if rsi_value > 30 else "🟡"
                st.metric("📊 RSI", f"{rsi_color} {rsi_value}")
            
            with col3:
                st.metric("📉 MACD", market_analysis['macd'])
            
            with col4:
                st.metric("📊 Volatilidad", f"{market_analysis['volatility']}%")
            
            # Strategy recommendation
            st.success(f"🎯 **Estrategia Recomendada**: {market_analysis['best_strategy']}")
            
            # Debug information (temporary)
            if 'debug_info' in market_analysis:
                debug = market_analysis['debug_info']
                st.caption(f"🔍 Debug: Uptrend={debug['uptrend_score']}, Downtrend={debug['downtrend_score']}, 5d={debug['momentum_5d']}%, 10d={debug['momentum_10d']}%")
            
            # Continue button
            if st.button("➡️ CONTINUAR A CONFIGURACIÓN", type="primary", use_container_width=True):
                st.session_state['current_step'] = 3
                st.rerun()
        else:
            st.error(f"❌ No se pudieron obtener datos para {symbol}")
    
    # === PASO 3: CONFIGURAR ESTRATEGIA ===
    if st.session_state['current_step'] >= 2:
        st.subheader("⚙️ PASO 3: CONFIGURAR ESTRATEGIA")
        
        # Obtener estrategia recomendada del análisis de mercado
        market_analysis = st.session_state.get('market_analysis', {})
        recommended_strategy = market_analysis.get('best_strategy', "Call Debit Spread") if market_analysis else "Call Debit Spread"
        
        # Selección de estrategia
        strategy_options = list(STRATEGIES.keys())
        default_index = strategy_options.index(recommended_strategy) if recommended_strategy in strategy_options else 0
        
        strategy_name = st.selectbox(
            "⚙️ Estrategia:",
            strategy_options,
            index=default_index,
            help="La estrategia recomendada está seleccionada automáticamente",
            key="strategy_selectbox"
        )
        
        # Información de la estrategia
        strategy_info = STRATEGIES[strategy_name]
        
        # Parámetros básicos
        col1, col2 = st.columns(2)
        with col1:
            # Calcular fecha de vencimiento: 3 días hábiles desde hoy (para llegar al viernes)
            default_expiration = get_next_business_days(datetime.now(), 3).date()
            expiration = st.date_input("📅 Vencimiento", 
                                     value=default_expiration,
                                     key="strategy_expiration")
        with col2:
            contracts = st.number_input("📋 Contratos", value=1, min_value=1, key="contracts_input")
        
        # VALIDACIÓN UNIVERSAL DE STRIKES Y MÉTRICAS TÉCNICAS
        if st.session_state['main_symbol']:
            market_data = get_market_data(st.session_state['main_symbol'])
            current_price = market_data['current_price'] if market_data else 150.0
            params = get_strategy_inputs(strategy_name, current_price, "main")
            
            # Obtener strikes de los parámetros
            lower_strike = params.get('lower_strike', current_price * 0.95)
            upper_strike = params.get('upper_strike', current_price * 1.05)
            
            # Calcular días hasta expiración
            days_to_expiration = (expiration - datetime.now().date()).days
            
            # VALIDACIÓN DE STRIKES
            validation = validate_strike_coherence(strategy_name, lower_strike, upper_strike, current_price)
            
            # Mostrar validaciones
            if validation['errors']:
                for error in validation['errors']:
                    st.error(f"❌ {error}")
            
            if validation['warnings']:
                for warning in validation['warnings']:
                    st.warning(f"⚠️ {warning}")
            
            # MÉTRICAS TÉCNICAS EN TIEMPO REAL
            st.markdown("### 📊 Análisis Técnico de Strikes")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                # Moneyness del strike inferior
                lower_moneyness_type, lower_moneyness_pct = calculate_moneyness(current_price, lower_strike)
                lower_moneyness_color = "🟢" if lower_moneyness_type == "ITM" else "🟡" if lower_moneyness_type == "ATM" else "🔴"
                st.metric(
                    f"Strike Inferior ({lower_moneyness_color})",
                    f"${lower_strike:.2f}",
                    f"{lower_moneyness_pct:.1f}% ({lower_moneyness_type})"
                )
            
            with col2:
                # Moneyness del strike superior
                upper_moneyness_type, upper_moneyness_pct = calculate_moneyness(current_price, upper_strike)
                upper_moneyness_color = "🟢" if upper_moneyness_type == "ITM" else "🟡" if upper_moneyness_type == "ATM" else "🔴"
                st.metric(
                    f"Strike Superior ({upper_moneyness_color})",
                    f"${upper_strike:.2f}",
                    f"{upper_moneyness_pct:.1f}% ({upper_moneyness_type})"
                )
            
            with col3:
                # Probabilidad ITM
                lower_itm_prob = calculate_itm_probability(current_price, lower_strike, days_to_expiration)
                upper_itm_prob = calculate_itm_probability(current_price, upper_strike, days_to_expiration)
                st.metric(
                    "Probabilidad ITM",
                    f"{lower_itm_prob:.1f}% / {upper_itm_prob:.1f}%",
                    "Inferior / Superior"
                )
            
            with col4:
                # Distancia a niveles técnicos
                support_levels = market_analysis.get('support_levels', [current_price * 0.95, current_price * 0.98])
                resistance_levels = market_analysis.get('resistance_levels', [current_price * 1.05, current_price * 1.02])
                tech_levels = get_technical_levels_distance(current_price, support_levels, resistance_levels)
                
                st.metric(
                    "Distancia a Niveles",
                    f"{tech_levels['support_distance']:.1f}% / {tech_levels['resistance_distance']:.1f}%",
                    "Soporte / Resistencia"
                )
            
            # GREEKS BÁSICOS
            st.markdown("### 🎯 Greeks de la Estrategia")
            
            # Obtener volatilidad del análisis de mercado
            volatility = market_analysis.get('implied_volatility', 0.3) / 100 if market_analysis.get('implied_volatility') else 0.3
            
            greeks = calculate_basic_greeks(strategy_name, current_price, lower_strike, upper_strike, days_to_expiration, volatility)
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                delta_color = "normal" if greeks['delta'] > 0 else "inverse"
                st.metric("Delta", f"{greeks['delta']:.3f}", delta_color=delta_color)
            
            with col2:
                st.metric("Gamma", f"{greeks['gamma']:.4f}")
            
            with col3:
                theta_color = "inverse" if greeks['theta'] < 0 else "normal"
                st.metric("Theta", f"{greeks['theta']:.3f}", delta_color=theta_color)
            
            with col4:
                st.metric("Vega", f"{greeks['vega']:.2f}")
        
        # Botón para analizar estrategia
        if st.button("🚀 ANALIZAR ESTRATEGIA", type="primary", use_container_width=True, key="analyze_strategy_btn"):
            try:
                if st.session_state['main_symbol'] and st.session_state.get('market_analysis'):
                    # Validar strikes antes de analizar
                    if not validation['is_valid']:
                        st.error("❌ Corrige los errores en la configuración de strikes antes de continuar")
                        return
                    
                    with st.spinner("🚀 Analizando estrategia..."):
                        market_data = get_market_data(st.session_state['main_symbol'])
                        current_price = market_data['current_price'] if market_data else 150.0
                        
                        # Crear y analizar estrategia
                        strategy = create_strategy(strategy_name, current_price, params, expiration.strftime("%Y-%m-%d"))
                        results = strategy.analyze()
                        
                        # Guardar resultados
                        st.session_state['results'] = {
                            'strategy_name': strategy_name,
                            'symbol': st.session_state['main_symbol'],
                            'current_price': current_price,
                            'results': results,
                            'params': params,
                            'expiration': expiration.strftime("%Y-%m-%d"),
                            'market_analysis': st.session_state['market_analysis']
                        }
                        
                        st.session_state['current_step'] = 4
                        st.success("✅ Análisis completado - Ve a PASO 4 para ver resultados")
                        st.rerun()
                else:
                    st.error("❌ Primero selecciona un símbolo")
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
    
    # === PASO 4: VER RESULTADOS ===
    if st.session_state['current_step'] >= 3:
        st.subheader("📈 PASO 4: VER RESULTADOS")
        
        # Mostrar resultados si existen
        if st.session_state.get('results'):
            results_data = st.session_state['results']
            results = results_data['results']
            symbol = results_data['symbol']
            current_price = results_data['current_price']
            params = results_data.get('params', {})
            risk_levels = params.get('risk_levels')
            
            # Render results
            render_results(results, results_data['strategy_name'], symbol, current_price, results_data.get('market_analysis'))
            
            # Botón para hacer backtesting de esta estrategia
            st.markdown("---")
            st.markdown("### 🤖 ¿Quieres probar esta estrategia?")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🚀 HACER BACKTESTING", type="primary", use_container_width=True):
                    try:
                        # Importar el motor de backtesting
                        from options_analyzer.backtesting import BacktestEngine
                        
                        # Inicializar el motor
                        if 'backtest_engine' not in st.session_state:
                            st.session_state['backtest_engine'] = BacktestEngine()
                        
                        engine = st.session_state['backtest_engine']
                        
                        # Obtener datos de la estrategia actual
                        strategy_name = results_data['strategy_name']
                        symbol = results_data['symbol']
                        current_price = results_data['current_price']
                        expiration_date = datetime.strptime(results_data['expiration'], "%Y-%m-%d")
                        market_analysis = results_data.get('market_analysis', {})
                        
                        # Extraer parámetros de la estrategia
                        params = results_data.get('params', {})
                        lower_strike = params.get('lower_strike', current_price * 0.95)
                        upper_strike = params.get('upper_strike', current_price * 1.05)
                        lower_premium = params.get('lower_premium', current_price * 0.03)
                        upper_premium = params.get('upper_premium', current_price * 0.01)
                        contracts = params.get('contracts', 1)
                        
                        # Agregar estrategia al backtesting
                        strategy_id = engine.add_strategy_for_backtesting(
                            symbol=symbol,
                            strategy_name=strategy_name,
                            entry_price=current_price,
                            lower_strike=lower_strike,
                            upper_strike=upper_strike,
                            lower_premium=lower_premium,
                            upper_premium=upper_premium,
                            contracts=contracts,
                            expiration_date=expiration_date,
                            market_analysis=market_analysis
                        )
                        
                        if strategy_id:
                            st.success(f"✅ Estrategia agregada al backtesting! ID: {strategy_id[:8]}")
                            st.info("🔍 Ve a la página '🤖 Backtesting' para monitorear los resultados")
                        else:
                            st.error("❌ Error al agregar estrategia al backtesting")
                            
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
            
            with col2:
                if st.button("📊 Ver Backtesting", use_container_width=True):
                    st.session_state['current_page'] = 'backtesting'
                    st.rerun()
        else:
            st.info("📊 Ejecuta el análisis en el PASO 3 para ver los resultados")
    
    # === POSITION MONITORING ===
    if st.session_state.get('results'):
        render_position_analysis() 