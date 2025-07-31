"""
Asset Selector Component - Advanced financial asset selection with real-time data
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import yfinance as yf
import sys
from pathlib import Path

# Add config directory to path
sys.path.append(str(Path(__file__).parent.parent.parent / "config"))
from asset_config import ASSET_CATEGORIES, ASSETS_DATABASE, SECTORS, get_asset_info, get_category_assets, get_sector_assets

# Use the complete asset database
POPULAR_ASSETS = ASSETS_DATABASE

class AssetSelector:
    def __init__(self):
        self.cache = {}
        self.cache_timeout = 30  # seconds
        
    def get_asset_data(self, symbol: str) -> Optional[Dict]:
        """Get real-time asset data with caching."""
        cache_key = f"asset_{symbol}"
        current_time = datetime.now()
        
        # Check cache
        if cache_key in self.cache:
            cached_data, cache_time = self.cache[cache_key]
            if (current_time - cache_time).total_seconds() < self.cache_timeout:
                return cached_data
        
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            # Get current price and change
            hist = ticker.history(period="2d")
            if len(hist) >= 2:
                current_price = hist['Close'].iloc[-1]
                prev_price = hist['Close'].iloc[-2]
                price_change = current_price - prev_price
                price_change_pct = (price_change / prev_price) * 100
            else:
                current_price = info.get('currentPrice', 0)
                price_change = 0
                price_change_pct = 0
            
            # Determine trend
            if price_change_pct > 1:
                trend = "↗️"
                trend_color = "#4CAF50"
            elif price_change_pct < -1:
                trend = "↘️"
                trend_color = "#F44336"
            else:
                trend = "➡️"
                trend_color = "#FF9800"
            
            asset_data = {
                'symbol': symbol,
                'name': info.get('longName', POPULAR_ASSETS.get(symbol, {}).get('name', symbol)),
                'current_price': current_price,
                'price_change': price_change,
                'price_change_pct': price_change_pct,
                'trend': trend,
                'trend_color': trend_color,
                'volume': info.get('volume', 0),
                'market_cap': info.get('marketCap', 0),
                'pe_ratio': info.get('trailingPE', 0),
                'fifty_two_week_high': info.get('fiftyTwoWeekHigh', 0),
                'fifty_two_week_low': info.get('fiftyTwoWeekLow', 0),
                'category': POPULAR_ASSETS.get(symbol, {}).get('category', 'stocks'),
                'sector': POPULAR_ASSETS.get(symbol, {}).get('sector', 'Unknown')
            }
            
            # Cache the data
            self.cache[cache_key] = (asset_data, current_time)
            return asset_data
            
        except Exception as e:
            st.error(f"Error getting data for {symbol}: {str(e)}")
            return None
    
    def render_search_bar(self) -> str:
        """Render search bar with filters."""
        col1, col2, col3 = st.columns([3, 2, 1])
        
        with col1:
            search_term = st.text_input(
                "🔍 Buscar activo",
                placeholder="Ej: AAPL, TSLA, SPY...",
                help="Busca por símbolo o nombre de empresa"
            )
        
        with col2:
            category_filter = st.selectbox(
                "📂 Categoría",
                ["Todos", "Stocks", "ETFs", "Indices", "Crypto"],
                help="Filtrar por tipo de activo"
            )
        
        with col3:
            sort_by = st.selectbox(
                "📊 Ordenar",
                ["Alfabético", "Precio", "Variación", "Volumen"],
                help="Ordenar resultados"
            )
        
        return search_term, category_filter, sort_by
    
    def render_asset_card(self, asset_data: Dict, is_selected: bool = False, is_favorite: bool = False):
        """Render individual asset card with rich information."""
        category_info = ASSET_CATEGORIES.get(asset_data['category'], ASSET_CATEGORIES['stocks'])
        
        # Card styling based on selection state
        if is_selected:
            border_color = "#1f77b4"
            background_color = "#f0f8ff"
        else:
            border_color = "#e0e0e0"
            background_color = "white"
        
        # Format price and change
        price_str = f"${asset_data['current_price']:.2f}" if asset_data['current_price'] else "N/A"
        change_str = f"{asset_data['price_change_pct']:+.2f}%" if asset_data['price_change_pct'] else "0.00%"
        change_color = asset_data['trend_color']
        
        # Format volume/market cap
        if asset_data['market_cap']:
            volume_str = f"${asset_data['market_cap']/1e9:.1f}B"
        elif asset_data['volume']:
            volume_str = f"{asset_data['volume']/1e6:.1f}M"
        else:
            volume_str = "N/A"
        
        # Render card with custom HTML
        st.markdown(f"""
        <div style="
            background-color: {background_color};
            border: 2px solid {border_color};
            border-radius: 12px;
            padding: 16px;
            margin: 8px 0;
            transition: all 0.3s ease;
            cursor: pointer;
            position: relative;
        " onmouseover="this.style.transform='translateY(-2px)'; this.style.boxShadow='0 4px 12px rgba(0,0,0,0.15)'"
           onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='none'">
            
            <!-- Header with symbol and favorite -->
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                <div style="display: flex; align-items: center; gap: 8px;">
                    <span style="font-size: 18px;">{category_info['icon']}</span>
                    <span style="font-weight: bold; font-size: 16px; color: #333;">{asset_data['symbol']}</span>
                </div>
                <span style="font-size: 18px; color: {'#FFD700' if is_favorite else '#ccc'}; cursor: pointer;">{'★' if is_favorite else '☆'}</span>
            </div>
            
            <!-- Company name -->
            <div style="font-size: 12px; color: #666; margin-bottom: 12px; line-height: 1.2;">
                {asset_data['name']}
            </div>
            
            <!-- Price and change -->
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                <span style="font-weight: bold; font-size: 18px;">{price_str}</span>
                <div style="display: flex; align-items: center; gap: 4px;">
                    <span style="font-size: 16px;">{asset_data['trend']}</span>
                    <span style="color: {change_color}; font-weight: bold;">{change_str}</span>
                </div>
            </div>
            
            <!-- Additional info -->
            <div style="display: flex; justify-content: space-between; font-size: 11px; color: #888;">
                <span>Vol: {volume_str}</span>
                <span>{asset_data['sector']}</span>
            </div>
            
            <!-- Selection indicator -->
            {f'<div style="position: absolute; top: 8px; right: 8px; width: 12px; height: 12px; background-color: #1f77b4; border-radius: 50%;"></div>' if is_selected else ''}
        </div>
        """, unsafe_allow_html=True)
    
    def render_asset_grid(self, assets: List[str], selected_symbol: Optional[str] = None):
        """Render responsive asset grid."""
        # Get asset data for all symbols
        asset_data_list = []
        for symbol in assets:
            data = self.get_asset_data(symbol)
            if data:
                asset_data_list.append(data)
        
        # Sort assets
        asset_data_list.sort(key=lambda x: x['symbol'])
        
        # Render grid
        cols = st.columns(4)
        for i, asset_data in enumerate(asset_data_list):
            with cols[i % 4]:
                is_selected = selected_symbol == asset_data['symbol']
                is_favorite = st.session_state.get('favorites', {}).get(asset_data['symbol'], False)
                
                # Create clickable card
                if st.button(
                    f"Select {asset_data['symbol']}",
                    key=f"select_{asset_data['symbol']}",
                    use_container_width=True,
                    type="primary" if is_selected else "secondary"
                ):
                    st.session_state['main_symbol'] = asset_data['symbol']
                    st.session_state['current_step'] = 2
                    st.rerun()
                
                # Render the actual card
                self.render_asset_card(asset_data, is_selected, is_favorite)
    
    def render_favorites_section(self):
        """Render favorites section."""
        favorites = st.session_state.get('favorites', {})
        if favorites:
            st.markdown("### ⭐ Favoritos")
            favorite_symbols = [symbol for symbol, is_fav in favorites.items() if is_fav]
            if favorite_symbols:
                self.render_asset_grid(favorite_symbols[:8])
    
    def render_recent_section(self):
        """Render recently used assets."""
        recent = st.session_state.get('recent_assets', [])
        if recent:
            st.markdown("### 🕒 Recientes")
            self.render_asset_grid(recent[:8])
    
    def render_category_section(self, category: str, assets: List[str]):
        """Render assets by category."""
        category_info = ASSET_CATEGORIES.get(category, ASSET_CATEGORIES['stocks'])
        st.markdown(f"### {category_info['icon']} {category_info['name']}")
        self.render_asset_grid(assets)
    
    def render(self) -> Optional[str]:
        """Main render function for asset selector."""
        st.markdown("### 🎯 PASO 1: SELECCIONAR ACTIVO FINANCIERO")
        
        # Search and filters
        search_term, category_filter, sort_by = self.render_search_bar()
        
        # Initialize session state
        if 'favorites' not in st.session_state:
            st.session_state['favorites'] = {}
        if 'recent_assets' not in st.session_state:
            st.session_state['recent_assets'] = []
        
        # Filter assets based on search and category
        filtered_assets = []
        for symbol, metadata in POPULAR_ASSETS.items():
            # Search filter
            if search_term:
                if search_term.upper() not in symbol.upper() and search_term.upper() not in metadata['name'].upper():
                    continue
            
            # Category filter
            if category_filter != "Todos":
                category_map = {"Stocks": "stocks", "ETFs": "etfs", "Indices": "indices", "Crypto": "crypto"}
                if metadata['category'] != category_map.get(category_filter, "stocks"):
                    continue
            
            filtered_assets.append(symbol)
        
        # Sort assets
        if sort_by == "Alfabético":
            filtered_assets.sort()
        elif sort_by == "Precio":
            filtered_assets.sort(key=lambda x: self.get_asset_data(x)['current_price'] if self.get_asset_data(x) else 0, reverse=True)
        elif sort_by == "Variación":
            filtered_assets.sort(key=lambda x: self.get_asset_data(x)['price_change_pct'] if self.get_asset_data(x) else 0, reverse=True)
        elif sort_by == "Volumen":
            filtered_assets.sort(key=lambda x: self.get_asset_data(x)['volume'] if self.get_asset_data(x) else 0, reverse=True)
        
        # Render sections
        if not search_term and category_filter == "Todos":
            # Show organized sections
            self.render_favorites_section()
            self.render_recent_section()
            
            # Show by category
            stocks = [s for s in filtered_assets if POPULAR_ASSETS[s]['category'] == 'stocks']
            etfs = [s for s in filtered_assets if POPULAR_ASSETS[s]['category'] == 'etfs']
            indices = [s for s in filtered_assets if POPULAR_ASSETS[s]['category'] == 'indices']
            crypto = [s for s in filtered_assets if POPULAR_ASSETS[s]['category'] == 'crypto']
            
            if stocks:
                self.render_category_section('stocks', stocks)
            if etfs:
                self.render_category_section('etfs', etfs)
            if indices:
                self.render_category_section('indices', indices)
            if crypto:
                self.render_category_section('crypto', crypto)
        else:
            # Show filtered results
            st.markdown("### 🔍 Resultados de Búsqueda")
            if filtered_assets:
                self.render_asset_grid(filtered_assets, st.session_state.get('main_symbol'))
            else:
                st.info("No se encontraron activos que coincidan con tu búsqueda.")
        
        # Quick actions
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 Actualizar Datos", use_container_width=True):
                self.cache.clear()
                st.rerun()
        
        with col2:
            if st.button("📊 Ver Todos los Activos", use_container_width=True):
                st.session_state['show_all_assets'] = True
                st.rerun()
        
        return st.session_state.get('main_symbol')

# Global instance
asset_selector = AssetSelector() 