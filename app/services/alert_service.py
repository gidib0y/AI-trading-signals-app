import asyncio
import json
import time
from typing import Dict, List, Optional, Callable, Any
from datetime import datetime, timedelta
import logging
from dataclasses import dataclass, asdict
from enum import Enum

class AlertType(Enum):
    """Types of alerts"""
    PRICE_TARGET = "price_target"
    SIGNAL_CHANGE = "signal_change"
    VOLATILITY_SPIKE = "volatility_spike"
    PATTERN_DETECTED = "pattern_detected"
    REGIME_CHANGE = "regime_change"
    VOLUME_SPIKE = "volume_spike"
    TECHNICAL_BREAKOUT = "technical_breakout"

class AlertStatus(Enum):
    """Alert status"""
    ACTIVE = "active"
    TRIGGERED = "triggered"
    EXPIRED = "expired"
    CANCELLED = "cancelled"

@dataclass
class Alert:
    """Represents a trading alert"""
    id: str
    symbol: str
    alert_type: AlertType
    condition: Dict[str, Any]
    message: str
    created_at: datetime
    expires_at: Optional[datetime]
    status: AlertStatus
    triggered_at: Optional[datetime] = None
    triggered_value: Optional[float] = None
    priority: str = "medium"  # low, medium, high, critical

class AlertService:
    """Comprehensive alert service for trading notifications"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.alerts: Dict[str, Alert] = {}
        self.subscribers: List[Callable] = []
        self.is_running = False
        self.alert_counter = 0
        
    async def start(self):
        """Start the alert service"""
        self.is_running = True
        logging.info("Alert service started")
        
        # Start alert monitoring
        asyncio.create_task(self._monitor_alerts())
        
    async def stop(self):
        """Stop the alert service"""
        self.is_running = False
        logging.info("Alert service stopped")
    
    def create_price_target_alert(self, symbol: str, target_price: float, 
                                 direction: str, current_price: float,
                                 expires_in_hours: int = 24) -> Alert:
        """Create a price target alert"""
        
        alert_id = f"price_{symbol}_{self.alert_counter}"
        self.alert_counter += 1
        
        condition = {
            'type': 'price_target',
            'target_price': target_price,
            'direction': direction,  # 'above' or 'below'
            'current_price': current_price
        }
        
        message = f"{symbol} {direction} ${target_price:.2f} (Current: ${current_price:.2f})"
        
        alert = Alert(
            id=alert_id,
            symbol=symbol,
            alert_type=AlertType.PRICE_TARGET,
            condition=condition,
            message=message,
            created_at=datetime.now(),
            expires_at=datetime.now() + timedelta(hours=expires_in_hours),
            status=AlertStatus.ACTIVE,
            priority='high'
        )
        
        self.alerts[alert_id] = alert
        self.logger.info(f"Created price target alert: {alert_id}")
        
        return alert
    
    def create_signal_change_alert(self, symbol: str, current_signal: str,
                                  new_signal: str, confidence: float,
                                  expires_in_hours: int = 6) -> Alert:
        """Create a signal change alert"""
        
        alert_id = f"signal_{symbol}_{self.alert_counter}"
        self.alert_counter += 1
        
        condition = {
            'type': 'signal_change',
            'current_signal': current_signal,
            'new_signal': new_signal,
            'confidence': confidence
        }
        
        message = f"{symbol} signal changed from {current_signal} to {new_signal} (Confidence: {confidence:.1%})"
        
        alert = Alert(
            id=alert_id,
            symbol=symbol,
            alert_type=AlertType.SIGNAL_CHANGE,
            condition=condition,
            message=message,
            created_at=datetime.now(),
            expires_at=datetime.now() + timedelta(hours=expires_in_hours),
            status=AlertStatus.ACTIVE,
            priority='critical'
        )
        
        self.alerts[alert_id] = alert
        self.logger.info(f"Created signal change alert: {alert_id}")
        
        return alert
    
    def create_volatility_spike_alert(self, symbol: str, current_vol: float,
                                     threshold_vol: float, expires_in_hours: int = 12) -> Alert:
        """Create a volatility spike alert"""
        
        alert_id = f"vol_{symbol}_{self.alert_counter}"
        self.alert_counter += 1
        
        condition = {
            'type': 'volatility_spike',
            'current_volatility': current_vol,
            'threshold_volatility': threshold_vol
        }
        
        message = f"{symbol} volatility spike detected: {current_vol:.2%} (Threshold: {threshold_vol:.2%})"
        
        alert = Alert(
            id=alert_id,
            symbol=symbol,
            alert_type=AlertType.VOLATILITY_SPIKE,
            condition=condition,
            message=message,
            created_at=datetime.now(),
            expires_at=datetime.now() + timedelta(hours=expires_in_hours),
            status=AlertStatus.ACTIVE,
            priority='high'
        )
        
        self.alerts[alert_id] = alert
        self.logger.info(f"Created volatility spike alert: {alert_id}")
        
        return alert
    
    def create_pattern_detected_alert(self, symbol: str, pattern_name: str,
                                    pattern_strength: float, price: float,
                                    expires_in_hours: int = 4) -> Alert:
        """Create a pattern detection alert"""
        
        alert_id = f"pattern_{symbol}_{self.alert_counter}"
        self.alert_counter += 1
        
        condition = {
            'type': 'pattern_detected',
            'pattern_name': pattern_name,
            'pattern_strength': pattern_strength,
            'price': price
        }
        
        message = f"{symbol} {pattern_name} pattern detected (Strength: {pattern_strength:.1%}) at ${price:.2f}"
        
        alert = Alert(
            id=alert_id,
            symbol=symbol,
            alert_type=AlertType.PATTERN_DETECTED,
            condition=condition,
            message=message,
            created_at=datetime.now(),
            expires_at=datetime.now() + timedelta(hours=expires_in_hours),
            status=AlertStatus.ACTIVE,
            priority='medium'
        )
        
        self.alerts[alert_id] = alert
        self.logger.info(f"Created pattern detection alert: {alert_id}")
        
        return alert
    
    def create_regime_change_alert(self, symbol: str, old_regime: str,
                                  new_regime: str, confidence: float,
                                  expires_in_hours: int = 8) -> Alert:
        """Create a market regime change alert"""
        
        alert_id = f"regime_{symbol}_{self.alert_counter}"
        self.alert_counter += 1
        
        condition = {
            'type': 'regime_change',
            'old_regime': old_regime,
            'new_regime': new_regime,
            'confidence': confidence
        }
        
        message = f"{symbol} market regime changed from {old_regime} to {new_regime} (Confidence: {confidence:.1%})"
        
        alert = Alert(
            id=alert_id,
            symbol=symbol,
            alert_type=AlertType.REGIME_CHANGE,
            condition=condition,
            message=message,
            created_at=datetime.now(),
            expires_at=datetime.now() + timedelta(hours=expires_in_hours),
            status=AlertStatus.ACTIVE,
            priority='high'
        )
        
        self.alerts[alert_id] = alert
        self.logger.info(f"Created regime change alert: {alert_id}")
        
        return alert
    
    def create_volume_spike_alert(self, symbol: str, current_volume: float,
                                 avg_volume: float, expires_in_hours: int = 2) -> Alert:
        """Create a volume spike alert"""
        
        alert_id = f"volume_{symbol}_{self.alert_counter}"
        self.alert_counter += 1
        
        volume_ratio = current_volume / avg_volume if avg_volume > 0 else 0
        
        condition = {
            'type': 'volume_spike',
            'current_volume': current_volume,
            'average_volume': avg_volume,
            'volume_ratio': volume_ratio
        }
        
        message = f"{symbol} volume spike: {current_volume:,.0f} ({volume_ratio:.1f}x average)"
        
        alert = Alert(
            id=alert_id,
            symbol=symbol,
            alert_type=AlertType.VOLUME_SPIKE,
            condition=condition,
            message=message,
            created_at=datetime.now(),
            expires_at=datetime.now() + timedelta(hours=expires_in_hours),
            status=AlertStatus.ACTIVE,
            priority='medium'
        )
        
        self.alerts[alert_id] = alert
        self.logger.info(f"Created volume spike alert: {alert_id}")
        
        return alert
    
    def create_technical_breakout_alert(self, symbol: str, breakout_type: str,
                                       price: float, level: float,
                                       expires_in_hours: int = 6) -> Alert:
        """Create a technical breakout alert"""
        
        alert_id = f"breakout_{symbol}_{self.alert_counter}"
        self.alert_counter += 1
        
        condition = {
            'type': 'technical_breakout',
            'breakout_type': breakout_type,
            'price': price,
            'level': level
        }
        
        message = f"{symbol} {breakout_type} breakout at ${price:.2f} (Level: ${level:.2f})"
        
        alert = Alert(
            id=alert_id,
            symbol=symbol,
            alert_type=AlertType.TECHNICAL_BREAKOUT,
            condition=condition,
            message=message,
            created_at=datetime.now(),
            expires_at=datetime.now() + timedelta(hours=expires_in_hours),
            status=AlertStatus.ACTIVE,
            priority='high'
        )
        
        self.alerts[alert_id] = alert
        self.logger.info(f"Created technical breakout alert: {alert_id}")
        
        return alert
    
    async def _monitor_alerts(self):
        """Monitor all active alerts"""
        while self.is_running:
            try:
                current_time = datetime.now()
                
                # Check each active alert
                for alert_id, alert in list(self.alerts.items()):
                    if alert.status != AlertStatus.ACTIVE:
                        continue
                    
                    # Check if alert has expired
                    if alert.expires_at and current_time > alert.expires_at:
                        alert.status = AlertStatus.EXPIRED
                        self.logger.info(f"Alert expired: {alert_id}")
                        continue
                    
                    # Check if alert should be triggered
                    if await self._check_alert_condition(alert):
                        await self._trigger_alert(alert)
                
                # Clean up expired alerts
                self._cleanup_expired_alerts()
                
                await asyncio.sleep(10)  # Check every 10 seconds
                
            except Exception as e:
                self.logger.error(f"Error monitoring alerts: {e}")
                await asyncio.sleep(30)
    
    async def _check_alert_condition(self, alert: Alert) -> bool:
        """Check if an alert condition is met"""
        try:
            condition = alert.condition
            
            if condition['type'] == 'price_target':
                return await self._check_price_target(alert)
            elif condition['type'] == 'signal_change':
                return await self._check_signal_change(alert)
            elif condition['type'] == 'volatility_spike':
                return await self._check_volatility_spike(alert)
            elif condition['type'] == 'pattern_detected':
                return await self._check_pattern_detected(alert)
            elif condition['type'] == 'regime_change':
                return await self._check_regime_change(alert)
            elif condition['type'] == 'volume_spike':
                return await self._check_volume_spike(alert)
            elif condition['type'] == 'technical_breakout':
                return await self._check_technical_breakout(alert)
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error checking alert condition: {e}")
            return False
    
    async def _check_price_target(self, alert: Alert) -> bool:
        """Check if price target is reached"""
        # This would integrate with real-time price data
        # For now, return False to prevent immediate triggering
        return False
    
    async def _check_signal_change(self, alert: Alert) -> bool:
        """Check if signal has changed"""
        # This would integrate with signal generation
        return False
    
    async def _check_volatility_spike(self, alert: Alert) -> bool:
        """Check if volatility spike occurred"""
        # This would integrate with volatility monitoring
        return False
    
    async def _check_pattern_detected(self, alert: Alert) -> bool:
        """Check if pattern was detected"""
        # This would integrate with pattern recognition
        return False
    
    async def _check_regime_change(self, alert: Alert) -> bool:
        """Check if regime changed"""
        # This would integrate with regime detection
        return False
    
    async def _check_volume_spike(self, alert: Alert) -> bool:
        """Check if volume spike occurred"""
        # This would integrate with volume monitoring
        return False
    
    async def _check_technical_breakout(self, alert: Alert) -> bool:
        """Check if technical breakout occurred"""
        # This would integrate with technical analysis
        return False
    
    async def _trigger_alert(self, alert: Alert):
        """Trigger an alert"""
        try:
            alert.status = AlertStatus.TRIGGERED
            alert.triggered_at = datetime.now()
            
            # Notify subscribers
            await self._notify_subscribers(alert)
            
            self.logger.info(f"Alert triggered: {alert.id} - {alert.message}")
            
        except Exception as e:
            self.logger.error(f"Error triggering alert: {e}")
    
    async def _notify_subscribers(self, alert: Alert):
        """Notify all subscribers about the alert"""
        for subscriber in self.subscribers:
            try:
                await subscriber(alert)
            except Exception as e:
                self.logger.error(f"Error notifying subscriber: {e}")
    
    def subscribe(self, callback: Callable):
        """Subscribe to alert notifications"""
        self.subscribers.append(callback)
    
    def unsubscribe(self, callback: Callable):
        """Unsubscribe from alert notifications"""
        if callback in self.subscribers:
            self.subscribers.remove(callback)
    
    def _cleanup_expired_alerts(self):
        """Remove expired alerts"""
        current_time = datetime.now()
        expired_alerts = [
            alert_id for alert_id, alert in self.alerts.items()
            if alert.status == AlertStatus.EXPIRED
        ]
        
        for alert_id in expired_alerts:
            del self.alerts[alert_id]
    
    def get_active_alerts(self, symbol: Optional[str] = None) -> List[Alert]:
        """Get all active alerts, optionally filtered by symbol"""
        if symbol:
            return [
                alert for alert in self.alerts.values()
                if alert.status == AlertStatus.ACTIVE and alert.symbol == symbol
            ]
        else:
            return [
                alert for alert in self.alerts.values()
                if alert.status == AlertStatus.ACTIVE
            ]
    
    def get_alert_history(self, symbol: Optional[str] = None, 
                         alert_type: Optional[AlertType] = None,
                         limit: int = 100) -> List[Alert]:
        """Get alert history with optional filtering"""
        alerts = list(self.alerts.values())
        
        # Filter by symbol
        if symbol:
            alerts = [a for a in alerts if a.symbol == symbol]
        
        # Filter by type
        if alert_type:
            alerts = [a for a in alerts if a.alert_type == alert_type]
        
        # Sort by creation time (newest first)
        alerts.sort(key=lambda x: x.created_at, reverse=True)
        
        return alerts[:limit]
    
    def cancel_alert(self, alert_id: str) -> bool:
        """Cancel an active alert"""
        if alert_id in self.alerts:
            alert = self.alerts[alert_id]
            if alert.status == AlertStatus.ACTIVE:
                alert.status = AlertStatus.CANCELLED
                self.logger.info(f"Alert cancelled: {alert_id}")
                return True
        return False
    
    def get_alert_statistics(self) -> Dict[str, Any]:
        """Get alert statistics"""
        total_alerts = len(self.alerts)
        active_alerts = len([a for a in self.alerts.values() if a.status == AlertStatus.ACTIVE])
        triggered_alerts = len([a for a in self.alerts.values() if a.status == AlertStatus.TRIGGERED])
        expired_alerts = len([a for a in self.alerts.values() if a.status == AlertStatus.EXPIRED])
        
        # Count by type
        type_counts = {}
        for alert in self.alerts.values():
            alert_type = alert.alert_type.value
            type_counts[alert_type] = type_counts.get(alert_type, 0) + 1
        
        # Count by priority
        priority_counts = {}
        for alert in self.alerts.values():
            priority = alert.priority
            priority_counts[priority] = priority_counts.get(priority, 0) + 1
        
        return {
            'total_alerts': total_alerts,
            'active_alerts': active_alerts,
            'triggered_alerts': triggered_alerts,
            'expired_alerts': expired_alerts,
            'type_distribution': type_counts,
            'priority_distribution': priority_counts
        }
    
    def export_alerts(self, format: str = 'json') -> str:
        """Export alerts in specified format"""
        if format == 'json':
            return json.dumps([asdict(alert) for alert in self.alerts.values()], 
                            default=str, indent=2)
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def import_alerts(self, data: str, format: str = 'json'):
        """Import alerts from specified format"""
        if format == 'json':
            alerts_data = json.loads(data)
            for alert_data in alerts_data:
                # Convert string back to enum
                alert_data['alert_type'] = AlertType(alert_data['alert_type'])
                alert_data['status'] = AlertStatus(alert_data['status'])
                
                # Create alert object
                alert = Alert(**alert_data)
                self.alerts[alert.id] = alert
        else:
            raise ValueError(f"Unsupported format: {format}")
