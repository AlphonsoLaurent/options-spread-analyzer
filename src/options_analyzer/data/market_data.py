"""Market data provider."""
import yfinance as yf
import pandas as pd
from typing import Dict, Optional, Any
from datetime import datetime, timedelta

class MarketDataProvider:
    def __init__(self):
        self.cache = {}
        self.cache_timeout = 30  # segundos
    
    def get_market_data(self, symbol: str) -> Optional[Dict[str, Any]]:
        # Verificar caché
        cache_key = f"{symbol}_data"
        if cache_key in self.cache:
            cached_data, cache_time = self.cache[cache_key]
            time_since_cache = (datetime.now() - cache_time).total_seconds()
            
            if time_since_cache < self.cache_timeout:
                print(f"📋 Usando datos en caché para {symbol} (hace {int(time_since_cache)}s)")
                return cached_data
        
        try:
            print(f"🔍 Obteniendo datos para {symbol}...")
            ticker = yf.Ticker(symbol)
            
            # Obtener información básica
            info = ticker.info
            print(f"📊 Info obtenida para {symbol}")
            
            # Obtener historial de precios
            end_date = datetime.now()
            start_date = end_date - timedelta(days=30)
            hist = ticker.history(start=start_date, end=end_date)
            
            print(f"📈 Historial obtenido: {len(hist)} días")
            
            if hist.empty:
                print(f"❌ No hay datos históricos para {symbol}")
                return None
            
            current_price = hist['Close'].iloc[-1]
            prev_close = hist['Close'].iloc[-2] if len(hist) > 1 else current_price
            change = current_price - prev_close
            change_percent = (change / prev_close) * 100 if prev_close != 0 else 0
            
            result = {
                'symbol': symbol,
                'current_price': float(current_price),
                'previous_close': float(prev_close),
                'change': float(change),
                'change_percent': float(change_percent),
                'volume': int(info.get('volume', 0)),
                'price_history': hist,
                'last_updated': datetime.now().isoformat()
            }
            
            # Guardar en caché
            self.cache[cache_key] = (result, datetime.now())
            
            print(f"✅ Datos obtenidos para {symbol}: ${current_price:.2f}")
            return result
            
        except Exception as e:
            print(f"❌ Error obteniendo datos para {symbol}: {e}")
            return None

market_provider = MarketDataProvider()

def get_market_data(symbol: str) -> Optional[Dict[str, Any]]:
    return market_provider.get_market_data(symbol)
