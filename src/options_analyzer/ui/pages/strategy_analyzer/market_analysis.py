"""
Market Analysis Module - Functions for analyzing market conditions and technical indicators
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, Any, List, Tuple
import yfinance as yf

def calculate_real_rsi(historical_data, period=14):
    """Calculate RSI using real historical data."""
    try:
        if len(historical_data) < period:
            return 50.0
        
        delta = historical_data['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        # Get the last values safely
        gain_value = float(gain.iloc[-1]) if not pd.isna(gain.iloc[-1]) else 0.0
        loss_value = float(loss.iloc[-1]) if not pd.isna(loss.iloc[-1]) else 0.0
        
        # Calculate RS and RSI
        if loss_value == 0:
            rs = 1.0
        else:
            rs = gain_value / loss_value
        
        try:
            rsi = 100 - (100 / (1 + rs))
            return float(rsi) if not pd.isna(rsi) else 50.0
        except (ZeroDivisionError, ValueError):
            return 50.0
    except Exception as e:
        return 50.0

def calculate_real_macd(historical_data, fast=12, slow=26, signal=9):
    """Calculate MACD using real historical data."""
    if len(historical_data) < slow:
        return "Neutral"
    
    exp1 = historical_data['Close'].ewm(span=fast).mean()
    exp2 = historical_data['Close'].ewm(span=slow).mean()
    macd_line = exp1 - exp2
    signal_line = macd_line.ewm(span=signal).mean()
    
    current_macd = macd_line.iloc[-1]
    current_signal = signal_line.iloc[-1]
    
    if current_macd > current_signal:
        return "Bullish"
    elif current_macd < current_signal:
        return "Bearish"
    else:
        return "Neutral"

def calculate_real_moving_averages(historical_data):
    """Calculate moving averages using real historical data."""
    if len(historical_data) < 50:
        return {"sma_20": 0, "sma_50": 0, "ema_12": 0, "ema_26": 0}
    
    sma_20 = historical_data['Close'].rolling(window=20).mean().iloc[-1]
    sma_50 = historical_data['Close'].rolling(window=50).mean().iloc[-1]
    ema_12 = historical_data['Close'].ewm(span=12).mean().iloc[-1]
    ema_26 = historical_data['Close'].ewm(span=26).mean().iloc[-1]
    
    return {
        "sma_20": sma_20 if not pd.isna(sma_20) else 0,
        "sma_50": sma_50 if not pd.isna(sma_50) else 0,
        "ema_12": ema_12 if not pd.isna(ema_12) else 0,
        "ema_26": ema_26 if not pd.isna(ema_26) else 0
    }

def calculate_real_volatility(historical_data, period=20):
    """Calculate volatility using real historical data."""
    if len(historical_data) < period:
        return 0.3
    
    returns = historical_data['Close'].pct_change().dropna()
    volatility = returns.rolling(window=period).std().iloc[-1]
    return volatility if not pd.isna(volatility) else 0.3

def calculate_real_support_resistance(historical_data, period=20):
    """Calculate support and resistance levels using real historical data."""
    if len(historical_data) < period:
        return {"support_levels": [], "resistance_levels": []}
    
    # Simple pivot point calculation
    high = historical_data['High'].rolling(window=period).max().iloc[-1]
    low = historical_data['Low'].rolling(window=period).min().iloc[-1]
    close = historical_data['Close'].iloc[-1]
    
    # Calculate pivot points
    pivot = (high + low + close) / 3
    r1 = 2 * pivot - low
    s1 = 2 * pivot - high
    
    support_levels = [s1, low]
    resistance_levels = [r1, high]
    
    return {
        "support_levels": [level for level in support_levels if not pd.isna(level)],
        "resistance_levels": [level for level in resistance_levels if not pd.isna(level)]
    }

def calculate_real_rsi_divergence(historical_data):
    """Calculate RSI divergence patterns."""
    if len(historical_data) < 30:
        return "No divergence detected"
    
    # Calculate RSI
    delta = historical_data['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    
    # Safe division for RS calculation
    try:
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
    except (ZeroDivisionError, ValueError):
        # If division fails, use a simple RSI calculation
        rsi = 50.0
    
    # Get recent data points
    recent_prices = historical_data['Close'].tail(10)
    recent_rsi = rsi.tail(10)
    
    # Check for divergence
    price_trend = recent_prices.iloc[-1] - recent_prices.iloc[0]
    rsi_trend = recent_rsi.iloc[-1] - recent_rsi.iloc[0]
    
    if price_trend > 0 and rsi_trend < -5:
        return "Bearish divergence"
    elif price_trend < 0 and rsi_trend > 5:
        return "Bullish divergence"
    else:
        return "No divergence detected"

# Función eliminada - Solo datos reales

def analyze_market_conditions(symbol: str, current_price: float):
    """Analyze real market conditions using yfinance data."""
    try:
        # Get real market data
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period="1mo")
        
        if len(hist) < 20:
            st.error(f"❌ Datos insuficientes para {symbol}. Se requieren al menos 20 días de datos históricos.")
            return None
        
        # Calculate real indicators
        rsi = calculate_real_rsi(hist)
        macd_signal = calculate_real_macd(hist)
        moving_averages = calculate_real_moving_averages(hist)
        volatility = calculate_real_volatility(hist)
        support_resistance = calculate_real_support_resistance(hist)
        rsi_divergence = calculate_real_rsi_divergence(hist)
        
        # Determine trend with more sophisticated logic
        sma_20 = moving_averages['sma_20']
        sma_50 = moving_averages['sma_50']
        current_price = hist['Close'].iloc[-1]
        
        # Calculate price momentum
        price_5d_ago = hist['Close'].iloc[-6] if len(hist) >= 6 else current_price
        price_10d_ago = hist['Close'].iloc[-11] if len(hist) >= 11 else current_price
        
        momentum_5d = (current_price / price_5d_ago - 1) * 100
        momentum_10d = (current_price / price_10d_ago - 1) * 100
        
        # Calculate moving average slope
        sma_20_slope = (sma_20 / moving_averages['sma_20'] - 1) * 100 if len(hist) >= 25 else 0
        sma_50_slope = (sma_50 / moving_averages['sma_50'] - 1) * 100 if len(hist) >= 55 else 0
        
        # Determine trend with multiple factors
        uptrend_score = 0
        downtrend_score = 0
        
        # Price vs moving averages
        if current_price > sma_20:
            uptrend_score += 1
        else:
            downtrend_score += 1
            
        if current_price > sma_50:
            uptrend_score += 1
        else:
            downtrend_score += 1
            
        # Moving average relationship
        if sma_20 > sma_50:
            uptrend_score += 1
        else:
            downtrend_score += 1
            
        # Momentum analysis
        if momentum_5d > 2:  # 2% gain in 5 days
            uptrend_score += 1
        elif momentum_5d < -2:  # 2% loss in 5 days
            downtrend_score += 1
            
        if momentum_10d > 5:  # 5% gain in 10 days
            uptrend_score += 1
        elif momentum_10d < -5:  # 5% loss in 10 days
            downtrend_score += 1
            
        # RSI consideration
        if rsi > 60:
            uptrend_score += 0.5
        elif rsi < 40:
            downtrend_score += 0.5
            
        # MACD consideration
        if macd_signal == "Bullish":
            uptrend_score += 1
        elif macd_signal == "Bearish":
            downtrend_score += 1
            
        # Determine final trend
        if uptrend_score > downtrend_score + 1:
            trend = "Uptrend"
        elif downtrend_score > uptrend_score + 1:
            trend = "Downtrend"
        else:
            trend = "Sideways"
            
        # Debug information (can be removed later)
        debug_info = {
            'uptrend_score': round(uptrend_score, 1),
            'downtrend_score': round(downtrend_score, 1),
            'momentum_5d': round(momentum_5d, 1),
            'momentum_10d': round(momentum_10d, 1),
            'price_vs_sma20': round((current_price / sma_20 - 1) * 100, 1),
            'price_vs_sma50': round((current_price / sma_50 - 1) * 100, 1)
        }
        
        # Determine best strategy - Solo Call Debit Spread y Put Debit Spread
        if trend == "Uptrend" and rsi < 70:
            best_strategy = "Call Debit Spread"
        elif trend == "Downtrend" and rsi > 30:
            best_strategy = "Put Debit Spread"
        elif trend == "Sideways" and rsi > 50:
            best_strategy = "Call Debit Spread"
        else:
            best_strategy = "Put Debit Spread"
        
        # Get additional market info
        info = ticker.info
        try:
            volume_trend = "Increasing" if hist['Volume'].iloc[-5:].mean() > hist['Volume'].iloc[-10:-5].mean() else "Decreasing"
        except:
            volume_trend = "Stable"
        
        return {
            'symbol': symbol,
            'current_price': current_price,
            'trend': trend,
            'rsi': round(rsi, 1),
            'macd': macd_signal,
            'volatility': round(volatility * 100, 1),
            'sma_20': round(moving_averages['sma_20'], 2),
            'sma_50': round(moving_averages['sma_50'], 2),
            'support_levels': support_resistance['support_levels'],
            'resistance_levels': support_resistance['resistance_levels'],
            'best_strategy': best_strategy,
            'confidence': 0.8,
            'risk_level': "Medium",
            'implied_volatility': round(volatility * 100, 1),
            'volume_trend': volume_trend,
            'market_sentiment': "Neutral",
            'rsi_divergence': rsi_divergence,
            'debug_info': debug_info
        }
        
    except Exception as e:
        st.error(f"❌ Error obteniendo datos reales para {symbol}: {str(e)}")
        return None

def analyze_advanced_context(symbol: str, current_price: float, market_analysis: dict):
    """Perform advanced market context analysis."""
    
    # Get additional market data
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period="3mo")
        
        if len(hist) < 30:
            return market_analysis
        
        # Calculate advanced indicators
        # Bollinger Bands
        sma_20 = hist['Close'].rolling(window=20).mean()
        std_20 = hist['Close'].rolling(window=20).std()
        upper_band = sma_20 + (std_20 * 2)
        lower_band = sma_20 - (std_20 * 2)
        
        try:
            current_upper = float(upper_band.iloc[-1])
            current_lower = float(lower_band.iloc[-1])
        except (IndexError, TypeError, ValueError):
            current_upper = current_price * 1.1
            current_lower = current_price * 0.9
        
        # Price position relative to Bollinger Bands
        bb_range = current_upper - current_lower
        if bb_range > 0:
            bb_position = (current_price - current_lower) / bb_range
        else:
            bb_position = 0.5  # Default to middle if bands are too close
        
        # Volume analysis
        avg_volume = hist['Volume'].mean()
        current_volume = hist['Volume'].iloc[-1]
        volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1.0
        
        # Momentum indicators
        try:
            if len(hist) >= 6:
                momentum_5d = (current_price / float(hist['Close'].iloc[-6])) - 1
            else:
                momentum_5d = 0.0
        except:
            momentum_5d = 0.0
            
        try:
            if len(hist) >= 21:
                momentum_20d = (current_price / float(hist['Close'].iloc[-21])) - 1
            else:
                momentum_20d = 0.0
        except:
            momentum_20d = 0.0
        
        # Market context - with safe division
        try:
            price_vs_sma20 = ((current_price / market_analysis['sma_20']) - 1) * 100 if market_analysis['sma_20'] > 0 else 0.0
        except (KeyError, ZeroDivisionError):
            price_vs_sma20 = 0.0
            
        try:
            price_vs_sma50 = ((current_price / market_analysis['sma_50']) - 1) * 100 if market_analysis['sma_50'] > 0 else 0.0
        except (KeyError, ZeroDivisionError):
            price_vs_sma50 = 0.0
        
        context = {
            'bollinger_position': round(bb_position, 3),
            'volume_ratio': round(volume_ratio, 2),
            'momentum_5d': round(momentum_5d * 100, 2),
            'momentum_20d': round(momentum_20d * 100, 2),
            'price_vs_sma20': round(price_vs_sma20, 2),
            'price_vs_sma50': round(price_vs_sma50, 2)
        }
        
        # Add context to market analysis
        market_analysis.update(context)
        
        return market_analysis
        
    except Exception as e:
        st.warning(f"Error in advanced analysis: {str(e)}")
        return market_analysis 