"""
Sistema de Gestión de Riesgo Automático para Estrategias de Opciones
"""

import streamlit as st
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import numpy as np
from dataclasses import dataclass
from enum import Enum


class AlertStatus(Enum):
    ACTIVE = "active"
    TRIGGERED = "triggered"
    CLOSED = "closed"


class RiskLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class RiskLevels:
    """Niveles de gestión de riesgo para una estrategia."""
    stop_loss_usd: float
    take_profit_usd: float
    stop_loss_percent: float
    take_profit_percent: float
    dte_alert: int
    max_loss_usd: float
    max_profit_usd: float


@dataclass
class PositionStatus:
    """Estado actual de una posición."""
    current_pnl_usd: float
    current_pnl_percent: float
    distance_to_sl: float
    distance_to_tp: float
    dte_remaining: int
    risk_level: RiskLevel
    alerts: List[Dict]
    last_updated: datetime


class RiskManagementSystem:
    """Sistema principal de gestión de riesgo automático."""
    
    def __init__(self):
        self.default_sl_percent = 50.0  # Stop Loss al 50% de pérdida máxima
        self.default_tp_percent = 75.0  # Take Profit al 75% de ganancia máxima
        self.default_dte_alert = 21     # Alerta a 21 DTE
        self.positions: Dict[str, Dict] = {}
        self.alert_history: List[Dict] = []
    
    def calculate_risk_levels(self, 
                            premium_paid: float, 
                            max_profit: float, 
                            max_loss: float,
                            current_price: float,
                            expiration_date: str) -> RiskLevels:
        """
        Calcula los niveles exactos de Stop Loss y Take Profit.
        
        Args:
            premium_paid: Prima pagada por la estrategia
            max_profit: Ganancia máxima teórica
            max_loss: Pérdida máxima teórica
            current_price: Precio actual del subyacente
            expiration_date: Fecha de expiración (YYYY-MM-DD)
        
        Returns:
            RiskLevels: Objeto con todos los niveles calculados
        """
        
        # Calcular niveles de Stop Loss y Take Profit
        stop_loss_usd = max_loss * (self.default_sl_percent / 100.0)
        take_profit_usd = max_profit * (self.default_tp_percent / 100.0)
        
        # Calcular porcentajes
        stop_loss_percent = (stop_loss_usd / max_loss) * 100 if max_loss > 0 else 0
        take_profit_percent = (take_profit_usd / max_profit) * 100 if max_profit > 0 else 0
        
        # Calcular DTE para alerta
        expiration = datetime.strptime(expiration_date, "%Y-%m-%d")
        dte_alert = self.default_dte_alert
        
        return RiskLevels(
            stop_loss_usd=stop_loss_usd,
            take_profit_usd=take_profit_usd,
            stop_loss_percent=stop_loss_percent,
            take_profit_percent=take_profit_percent,
            dte_alert=dte_alert,
            max_loss_usd=max_loss,
            max_profit_usd=max_profit
        )
    
    def add_position(self, 
                    position_id: str,
                    symbol: str,
                    strategy_name: str,
                    risk_levels: RiskLevels,
                    entry_date: str,
                    expiration_date: str,
                    initial_premium: float):
        """Agrega una nueva posición al sistema de monitoreo."""
        
        self.positions[position_id] = {
            'symbol': symbol,
            'strategy_name': strategy_name,
            'risk_levels': risk_levels,
            'entry_date': entry_date,
            'expiration_date': expiration_date,
            'initial_premium': initial_premium,
            'current_pnl_usd': 0.0,
            'current_pnl_percent': 0.0,
            'status': PositionStatus(
                current_pnl_usd=0.0,
                current_pnl_percent=0.0,
                distance_to_sl=risk_levels.stop_loss_usd,
                distance_to_tp=risk_levels.take_profit_usd,
                dte_remaining=self._calculate_dte(expiration_date),
                risk_level=RiskLevel.LOW,
                alerts=[],
                last_updated=datetime.now()
            )
        }
    
    def update_position_pnl(self, position_id: str, current_pnl_usd: float):
        """Actualiza el P&L de una posición y evalúa alertas."""
        
        if position_id not in self.positions:
            return
        
        position = self.positions[position_id]
        risk_levels = position['risk_levels']
        
        # Calcular P&L porcentual
        max_loss = risk_levels.max_loss_usd
        max_profit = risk_levels.max_profit_usd
        
        if max_loss > 0:
            pnl_percent = (current_pnl_usd / max_loss) * 100
        else:
            pnl_percent = 0
        
        # Actualizar estado
        position['current_pnl_usd'] = current_pnl_usd
        position['current_pnl_percent'] = pnl_percent
        
        # Calcular distancias a niveles
        distance_to_sl = abs(current_pnl_usd - (-risk_levels.stop_loss_usd))
        distance_to_tp = abs(current_pnl_usd - risk_levels.take_profit_usd)
        
        # Determinar nivel de riesgo
        risk_level = self._determine_risk_level(current_pnl_usd, risk_levels)
        
        # Actualizar estado de la posición
        position['status'] = PositionStatus(
            current_pnl_usd=current_pnl_usd,
            current_pnl_percent=pnl_percent,
            distance_to_sl=distance_to_sl,
            distance_to_tp=distance_to_tp,
            dte_remaining=self._calculate_dte(position['expiration_date']),
            risk_level=risk_level,
            alerts=position['status'].alerts if 'status' in position else [],
            last_updated=datetime.now()
        )
        
        # Evaluar alertas
        self._evaluate_alerts(position_id, current_pnl_usd, risk_levels)
    
    def _determine_risk_level(self, current_pnl: float, risk_levels: RiskLevels) -> RiskLevel:
        """Determina el nivel de riesgo actual de la posición."""
        
        # Si estamos en pérdidas
        if current_pnl < 0:
            loss_percent = abs(current_pnl) / risk_levels.max_loss_usd * 100
            
            if loss_percent >= 80:
                return RiskLevel.CRITICAL
            elif loss_percent >= 60:
                return RiskLevel.HIGH
            elif loss_percent >= 40:
                return RiskLevel.MEDIUM
            else:
                return RiskLevel.LOW
        
        # Si estamos en ganancias
        else:
            profit_percent = current_pnl / risk_levels.max_profit_usd * 100
            
            if profit_percent >= 80:
                return RiskLevel.HIGH  # Alto riesgo de reversión
            elif profit_percent >= 60:
                return RiskLevel.MEDIUM
            else:
                return RiskLevel.LOW
    
    def _evaluate_alerts(self, position_id: str, current_pnl: float, risk_levels: RiskLevels):
        """Evalúa y genera alertas basadas en el P&L actual."""
        
        position = self.positions[position_id]
        alerts = position['status'].alerts
        
        # Alerta de Stop Loss
        if current_pnl <= -risk_levels.stop_loss_usd:
            if not any(alert['type'] == 'stop_loss' and alert['status'] == AlertStatus.ACTIVE for alert in alerts):
                alert = {
                    'type': 'stop_loss',
                    'message': f"🚨 STOP LOSS ACTIVADO: P&L = ${current_pnl:.2f}",
                    'recommendation': 'Cerrar posición inmediatamente',
                    'status': AlertStatus.ACTIVE,
                    'timestamp': datetime.now(),
                    'pnl_at_alert': current_pnl
                }
                alerts.append(alert)
                self.alert_history.append(alert)
        
        # Alerta de Take Profit
        elif current_pnl >= risk_levels.take_profit_usd:
            if not any(alert['type'] == 'take_profit' and alert['status'] == AlertStatus.ACTIVE for alert in alerts):
                alert = {
                    'type': 'take_profit',
                    'message': f"🎯 TAKE PROFIT ACTIVADO: P&L = ${current_pnl:.2f}",
                    'recommendation': 'Considerar cerrar posición o ajustar',
                    'status': AlertStatus.ACTIVE,
                    'timestamp': datetime.now(),
                    'pnl_at_alert': current_pnl
                }
                alerts.append(alert)
                self.alert_history.append(alert)
        
        # Alerta de DTE
        dte_remaining = position['status'].dte_remaining
        if dte_remaining <= risk_levels.dte_alert:
            if not any(alert['type'] == 'dte_warning' and alert['status'] == AlertStatus.ACTIVE for alert in alerts):
                alert = {
                    'type': 'dte_warning',
                    'message': f"⏰ ALERTA DTE: {dte_remaining} días hasta expiración",
                    'recommendation': 'Evaluar rollover o cierre de posición',
                    'status': AlertStatus.ACTIVE,
                    'timestamp': datetime.now(),
                    'dte_at_alert': dte_remaining
                }
                alerts.append(alert)
                self.alert_history.append(alert)
    
    def _calculate_dte(self, expiration_date: str) -> int:
        """Calcula los días hasta expiración."""
        expiration = datetime.strptime(expiration_date, "%Y-%m-%d")
        return (expiration - datetime.now()).days
    
    def get_position_status(self, position_id: str) -> Optional[PositionStatus]:
        """Obtiene el estado actual de una posición."""
        if position_id in self.positions:
            return self.positions[position_id]['status']
        return None
    
    def get_all_positions(self) -> Dict[str, Dict]:
        """Obtiene todas las posiciones activas."""
        return self.positions
    
    def close_position(self, position_id: str, reason: str = "Manual"):
        """Cierra una posición y archiva sus alertas."""
        if position_id in self.positions:
            position = self.positions[position_id]
            
            # Marcar todas las alertas como cerradas
            for alert in position['status'].alerts:
                if alert['status'] == AlertStatus.ACTIVE:
                    alert['status'] = AlertStatus.CLOSED
                    alert['close_reason'] = reason
                    alert['close_timestamp'] = datetime.now()
            
            # Remover de posiciones activas
            del self.positions[position_id]


class RiskManagementUI:
    """Interfaz de usuario para el sistema de gestión de riesgo."""
    
    def __init__(self, risk_system: RiskManagementSystem):
        self.risk_system = risk_system
    
    def render_risk_configuration(self, 
                                strategy_name: str,
                                premium_paid: float,
                                max_profit: float,
                                max_loss: float,
                                current_price: float,
                                expiration_date: str) -> RiskLevels:
        """Renderiza el panel de configuración de gestión de riesgo."""
        
        st.markdown("---")
        st.subheader("🛡️ Configuración de Gestión de Riesgo")
        
        # Configuración personalizable
        col1, col2, col3 = st.columns(3)
        
        with col1:
            sl_percent = st.slider(
                "Stop Loss (%)", 
                min_value=10, 
                max_value=90, 
                value=50,
                help="Porcentaje de la pérdida máxima para activar Stop Loss"
            )
        
        with col2:
            tp_percent = st.slider(
                "Take Profit (%)", 
                min_value=25, 
                max_value=95, 
                value=75,
                help="Porcentaje de la ganancia máxima para activar Take Profit"
            )
        
        with col3:
            dte_alert = st.number_input(
                "Alerta DTE", 
                min_value=1, 
                max_value=45, 
                value=21,
                help="Días hasta expiración para activar alerta"
            )
        
        # Calcular niveles con configuración personalizada
        risk_levels = RiskLevels(
            stop_loss_usd=max_loss * (sl_percent / 100.0),
            take_profit_usd=max_profit * (tp_percent / 100.0),
            stop_loss_percent=sl_percent,
            take_profit_percent=tp_percent,
            dte_alert=dte_alert,
            max_loss_usd=max_loss,
            max_profit_usd=max_profit
        )
        
        return risk_levels
    
    def render_monitoring_panel(self, position_id: str):
        """Renderiza el panel de monitoreo en tiempo real."""
        
        position_status = self.risk_system.get_position_status(position_id)
        if not position_status:
            st.warning("Posición no encontrada")
            return
        
        st.markdown("---")
        st.subheader("📈 Panel de Monitoreo en Tiempo Real")
        
        # Métricas principales
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            pnl_color = "normal" if position_status.current_pnl_usd >= 0 else "inverse"
            st.metric(
                "P&L Actual",
                f"${position_status.current_pnl_usd:.2f}",
                f"{position_status.current_pnl_percent:.1f}%",
                delta_color=pnl_color
            )
        
        with col2:
            st.metric(
                "Distancia a SL",
                f"${position_status.distance_to_sl:.2f}",
                f"{position_status.dte_remaining} DTE"
            )
        
        with col3:
            st.metric(
                "Distancia a TP",
                f"${position_status.distance_to_tp:.2f}",
                f"{position_status.dte_remaining} DTE"
            )
        
        with col4:
            risk_color = {
                RiskLevel.LOW: "normal",
                RiskLevel.MEDIUM: "off",
                RiskLevel.HIGH: "inverse",
                RiskLevel.CRITICAL: "inverse"
            }.get(position_status.risk_level, "normal")
            
            st.metric(
                "Nivel de Riesgo",
                position_status.risk_level.value.upper(),
                delta_color=risk_color
            )
        
        # Alertas activas
        self._render_active_alerts(position_status.alerts)
        
        # Historial de alertas
        self._render_alert_history()
    
    def _render_active_alerts(self, alerts: List[Dict]):
        """Renderiza las alertas activas."""
        
        active_alerts = [alert for alert in alerts if alert['status'] == AlertStatus.ACTIVE]
        
        if active_alerts:
            st.markdown("### 🚨 Alertas Activas")
            
            for alert in active_alerts:
                if alert['type'] == 'stop_loss':
                    st.error(alert['message'])
                elif alert['type'] == 'take_profit':
                    st.success(alert['message'])
                elif alert['type'] == 'dte_warning':
                    st.warning(alert['message'])
                
                st.info(f"💡 Recomendación: {alert['recommendation']}")
        else:
            st.success("✅ No hay alertas activas")
    
    def _render_alert_history(self):
        """Renderiza el historial de alertas."""
        
        if self.risk_system.alert_history:
            st.markdown("### 📋 Historial de Alertas")
            
            for alert in self.risk_system.alert_history[-5:]:  # Últimas 5 alertas
                timestamp = alert['timestamp'].strftime("%H:%M:%S")
                
                if alert['status'] == AlertStatus.ACTIVE:
                    status_icon = "🟢"
                elif alert['status'] == AlertStatus.TRIGGERED:
                    status_icon = "🟡"
                else:
                    status_icon = "🔴"
                
                st.text(f"{status_icon} {timestamp} - {alert['message']}")


# Instancia global del sistema de gestión de riesgo
risk_management_system = RiskManagementSystem()
risk_management_ui = RiskManagementUI(risk_management_system) 