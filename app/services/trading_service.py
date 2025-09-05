import pandas as pd
import numpy as np
from typing import List, Dict, Any
from datetime import datetime
from app.models.schemas import Signal, SignalType

class TradingService:
    """Service for generating trading signals based on technical analysis and ML predictions"""
    
    def __init__(self):
        self.signal_thresholds = {
            'rsi_oversold': 30,
            'rsi_overbought': 70,
            'macd_signal_threshold': 0.001,
            'volume_threshold': 1.5,  # 1.5x average volume
            'price_change_threshold': 0.02  # 2% price change
        }
    
    def generate_signals(self, data: pd.DataFrame, predictions: Dict[str, Any]) -> List[Signal]:
        """Generate trading signals based on technical indicators and ML predictions"""
        signals = []
        
        if data.empty:
            return signals
        
        # Get the latest data point
        latest = data.iloc[-1]
        latest_timestamp = data.index[-1]
        
        # Analyze RSI
        rsi_signal = self._analyze_rsi(latest)
        
        # Analyze MACD
        macd_signal = self._analyze_macd(latest)
        
        # Analyze Bollinger Bands
        bb_signal = self._analyze_bollinger_bands(latest)
        
        # Analyze Moving Averages
        ma_signal = self._analyze_moving_averages(latest)
        
        # Analyze Volume
        volume_signal = self._analyze_volume(latest, data)
        
        # Combine signals with ML predictions
        combined_signal = self._combine_signals(
            [rsi_signal, macd_signal, bb_signal, ma_signal, volume_signal],
            predictions
        )
        
        # Create signal object
        signal = Signal(
            timestamp=latest_timestamp.isoformat(),
            signal_type=combined_signal['type'],
            price=float(latest['Close']),
            confidence=combined_signal['confidence'],
            reason=combined_signal['reason'],
            indicators={
                'rsi': float(latest.get('RSI', 0)),
                'macd': float(latest.get('MACD', 0)),
                'macd_signal': float(latest.get('MACD_Signal', 0)),
                'bb_upper': float(latest.get('BB_Upper', 0)),
                'bb_lower': float(latest.get('BB_Lower', 0)),
                'sma_20': float(latest.get('SMA_20', 0)),
                'ema_12': float(latest.get('EMA_12', 0))
            }
        )
        
        signals.append(signal)
        
        # Add historical signals if there are significant changes
        historical_signals = self._generate_historical_signals(data)
        signals.extend(historical_signals)
        
        return signals
    
    def _analyze_rsi(self, data_point: pd.Series) -> Dict[str, Any]:
        """Analyze RSI for trading signals"""
        rsi = data_point.get('RSI', 50)
        
        if rsi < self.signal_thresholds['rsi_oversold']:
            return {
                'type': SignalType.BUY,
                'confidence': 0.8,
                'reason': f'RSI oversold ({rsi:.2f})'
            }
        elif rsi > self.signal_thresholds['rsi_overbought']:
            return {
                'type': SignalType.SELL,
                'confidence': 0.8,
                'reason': f'RSI overbought ({rsi:.2f})'
            }
        else:
            return {
                'type': SignalType.HOLD,
                'confidence': 0.6,
                'reason': f'RSI neutral ({rsi:.2f})'
            }
    
    def _analyze_macd(self, data_point: pd.Series) -> Dict[str, Any]:
        """Analyze MACD for trading signals"""
        macd = data_point.get('MACD', 0)
        macd_signal = data_point.get('MACD_Signal', 0)
        macd_histogram = data_point.get('MACD_Histogram', 0)
        
        # MACD crossover signals
        if macd > macd_signal and macd_histogram > 0:
            return {
                'type': SignalType.BUY,
                'confidence': 0.7,
                'reason': 'MACD bullish crossover'
            }
        elif macd < macd_signal and macd_histogram < 0:
            return {
                'type': SignalType.SELL,
                'confidence': 0.7,
                'reason': 'MACD bearish crossover'
            }
        else:
            return {
                'type': SignalType.HOLD,
                'confidence': 0.5,
                'reason': 'MACD neutral'
            }
    
    def _analyze_bollinger_bands(self, data_point: pd.Series) -> Dict[str, Any]:
        """Analyze Bollinger Bands for trading signals"""
        close = data_point['Close']
        bb_upper = data_point.get('BB_Upper', close)
        bb_lower = data_point.get('BB_Lower', close)
        bb_middle = data_point.get('BB_Middle', close)
        
        # Price relative to Bollinger Bands
        if close <= bb_lower:
            return {
                'type': SignalType.BUY,
                'confidence': 0.75,
                'reason': 'Price at lower Bollinger Band'
            }
        elif close >= bb_upper:
            return {
                'type': SignalType.SELL,
                'confidence': 0.75,
                'reason': 'Price at upper Bollinger Band'
            }
        else:
            return {
                'type': SignalType.HOLD,
                'confidence': 0.6,
                'reason': 'Price within Bollinger Bands'
            }
    
    def _analyze_moving_averages(self, data_point: pd.Series) -> Dict[str, Any]:
        """Analyze Moving Averages for trading signals"""
        close = data_point['Close']
        sma_20 = data_point.get('SMA_20', close)
        ema_12 = data_point.get('EMA_12', close)
        
        # Moving average crossover signals
        if close > sma_20 and close > ema_12:
            return {
                'type': SignalType.BUY,
                'confidence': 0.7,
                'reason': 'Price above moving averages'
            }
        elif close < sma_20 and close < ema_12:
            return {
                'type': SignalType.SELL,
                'confidence': 0.7,
                'reason': 'Price below moving averages'
            }
        else:
            return {
                'type': SignalType.HOLD,
                'confidence': 0.5,
                'reason': 'Mixed moving average signals'
            }
    
    def _analyze_volume(self, data_point: pd.Series, data: pd.DataFrame) -> Dict[str, Any]:
        """Analyze volume for trading signals"""
        current_volume = data_point['Volume']
        avg_volume = data['Volume'].rolling(20).mean().iloc[-1]
        
        if current_volume > avg_volume * self.signal_thresholds['volume_threshold']:
            return {
                'type': SignalType.HOLD,  # High volume doesn't indicate direction
                'confidence': 0.6,
                'reason': 'High volume detected'
            }
        else:
            return {
                'type': SignalType.HOLD,
                'confidence': 0.5,
                'reason': 'Normal volume'
            }
    
    def _combine_signals(self, signals: List[Dict[str, Any]], predictions: Dict[str, Any]) -> Dict[str, Any]:
        """Combine multiple signals and ML predictions into a final signal"""
        # Count signal types
        signal_counts = {'BUY': 0, 'SELL': 0, 'HOLD': 0}
        total_confidence = 0
        
        for signal in signals:
            signal_counts[signal['type']] += 1
            total_confidence += signal['confidence']
        
        # Get ML prediction confidence
        ml_confidence = predictions.get('confidence_score', 0.5)
        
        # Determine final signal type
        if signal_counts['BUY'] > signal_counts['SELL']:
            final_type = SignalType.BUY
        elif signal_counts['SELL'] > signal_counts['BUY']:
            final_type = SignalType.SELL
        else:
            final_type = SignalType.HOLD
        
        # Calculate combined confidence
        avg_confidence = total_confidence / len(signals) if signals else 0.5
        combined_confidence = (avg_confidence + ml_confidence) / 2
        
        # Generate reason
        reasons = [s['reason'] for s in signals if s['type'] == final_type]
        reason = f"Combined analysis: {', '.join(reasons[:3])}"
        
        return {
            'type': final_type,
            'confidence': min(combined_confidence, 0.95),
            'reason': reason
        }
    
    def _generate_historical_signals(self, data: pd.DataFrame) -> List[Signal]:
        """Generate signals for significant historical price movements"""
        signals = []
        
        # Look for significant price changes in the last 30 days
        recent_data = data.tail(30)
        
        for i in range(1, len(recent_data)):
            current = recent_data.iloc[i]
            previous = recent_data.iloc[i-1]
            
            price_change = (current['Close'] - previous['Close']) / previous['Close']
            
            if abs(price_change) > self.signal_thresholds['price_change_threshold']:
                signal_type = SignalType.BUY if price_change > 0 else SignalType.SELL
                
                signal = Signal(
                    timestamp=current.name.isoformat(),
                    signal_type=signal_type,
                    price=float(current['Close']),
                    confidence=0.7,
                    reason=f"Significant price change: {price_change:.2%}",
                    indicators={}
                )
                signals.append(signal)
        
        return signals













