"""
Strategy Calculations Module - Functions for calculating options metrics and validations
"""

import streamlit as st
from typing import Dict, Tuple, List

def calculate_moneyness(current_price: float, strike_price: float) -> tuple:
    """Calcula el moneyness de una opción y retorna el tipo y porcentaje."""
    moneyness_percent = ((strike_price - current_price) / current_price) * 100
    
    if moneyness_percent < -5:
        return "ITM", moneyness_percent
    elif moneyness_percent > 5:
        return "OTM", moneyness_percent
    else:
        return "ATM", moneyness_percent

def validate_strike_coherence(strategy_name: str, lower_strike: float, upper_strike: float, current_price: float) -> dict:
    """Valida la coherencia de los strikes para una estrategia."""
    validation = {
        'is_valid': True,
        'warnings': [],
        'errors': []
    }
    
    # Validaciones básicas
    if lower_strike >= upper_strike:
        validation['is_valid'] = False
        validation['errors'].append("Strike inferior debe ser menor al superior")
    
    if lower_strike <= 0 or upper_strike <= 0:
        validation['is_valid'] = False
        validation['errors'].append("Strikes deben ser positivos")
    
    # Validaciones específicas por estrategia
    if strategy_name in ["Call Debit Spread", "Call Credit Spread"]:
        if lower_strike >= current_price * 1.5:
            validation['warnings'].append("Strike inferior muy alejado del precio actual")
        if upper_strike <= current_price * 0.5:
            validation['warnings'].append("Strike superior muy por debajo del precio actual")
    
    elif strategy_name in ["Put Debit Spread", "Put Credit Spread"]:
        if upper_strike <= current_price * 0.5:
            validation['warnings'].append("Strike superior muy alejado del precio actual")
        if lower_strike >= current_price * 1.5:
            validation['warnings'].append("Strike inferior muy por encima del precio actual")
    
    return validation

def calculate_basic_greeks(strategy_name: str, current_price: float, lower_strike: float, upper_strike: float, days_to_expiration: int, volatility: float = 0.3) -> dict:
    """Calcula Greeks básicos para la estrategia."""
    try:
        # Cálculos simplificados de Greeks
        # Delta aproximado
        if strategy_name in ["Call Debit Spread", "Call Credit Spread"]:
            lower_delta = max(0, min(1, (current_price - lower_strike) / (current_price * 0.1)))
            upper_delta = max(0, min(1, (current_price - upper_strike) / (current_price * 0.1)))
            
            if strategy_name == "Call Debit Spread":
                net_delta = lower_delta - upper_delta
            else:  # Call Credit Spread
                net_delta = upper_delta - lower_delta
        else:  # Put spreads
            lower_delta = max(-1, min(0, (lower_strike - current_price) / (current_price * 0.1)))
            upper_delta = max(-1, min(0, (upper_strike - current_price) / (current_price * 0.1)))
            
            if strategy_name == "Put Debit Spread":
                net_delta = upper_delta - lower_delta
            else:  # Put Credit Spread
                net_delta = lower_delta - upper_delta
        
        # Gamma aproximado (máximo cerca de ATM)
        lower_gamma = 1 / (current_price * volatility * (days_to_expiration ** 0.5))
        upper_gamma = 1 / (current_price * volatility * (days_to_expiration ** 0.5))
        net_gamma = abs(lower_gamma - upper_gamma)
        
        # Theta aproximado (decay temporal)
        net_theta = -volatility * current_price / (365 * (days_to_expiration ** 0.5))
        
        # Vega aproximado
        net_vega = current_price * (days_to_expiration ** 0.5) / 100
        
        return {
            'delta': round(net_delta, 3),
            'gamma': round(net_gamma, 4),
            'theta': round(net_theta, 3),
            'vega': round(net_vega, 2)
        }
    except:
        return {
            'delta': 0.0,
            'gamma': 0.0,
            'theta': 0.0,
            'vega': 0.0
        }

def calculate_itm_probability(current_price: float, strike_price: float, days_to_expiration: int, volatility: float = 0.3) -> float:
    """Calcula la probabilidad aproximada de ITM basada en Black-Scholes simplificado."""
    try:
        # Cálculo simplificado de probabilidad ITM
        moneyness = (strike_price - current_price) / current_price
        time_factor = (days_to_expiration / 365) ** 0.5
        
        # Aproximación usando distribución normal
        if moneyness > 0:  # OTM
            prob = max(0, 0.5 - (moneyness / (volatility * time_factor)) * 0.4)
        else:  # ITM
            prob = min(1, 0.5 + (abs(moneyness) / (volatility * time_factor)) * 0.4)
        
        return round(prob * 100, 1)
    except:
        return 50.0

def get_technical_levels_distance(current_price: float, support_levels: list, resistance_levels: list) -> dict:
    """Calcula la distancia a niveles técnicos clave."""
    try:
        nearest_support = min(support_levels, key=lambda x: abs(x - current_price))
        nearest_resistance = min(resistance_levels, key=lambda x: abs(x - current_price))
        
        support_distance = ((current_price - nearest_support) / current_price) * 100
        resistance_distance = ((nearest_resistance - current_price) / current_price) * 100
        
        return {
            'nearest_support': round(nearest_support, 2),
            'nearest_resistance': round(nearest_resistance, 2),
            'support_distance': round(support_distance, 1),
            'resistance_distance': round(resistance_distance, 1)
        }
    except:
        return {
            'nearest_support': current_price * 0.95,
            'nearest_resistance': current_price * 1.05,
            'support_distance': 5.0,
            'resistance_distance': 5.0
        } 