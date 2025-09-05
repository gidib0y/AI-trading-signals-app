import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime, timedelta
import math
import logging

class MultiTimeframeService:
    """Multi-timeframe analysis service for comprehensive trading analysis"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Define timeframes
        self.timeframes = {
            'intraday': {
                '1m': {'minutes': 1, 'description': '1 Minute'},
                '5m': {'minutes': 5, 'description': '5 Minutes'},
                '15m': {'minutes': 15, 'description': '15 Minutes'},
                '30m': {'minutes': 30, 'description': '30 Minutes'},
                '1h': {'minutes': 60, 'description': '1 Hour'},
                '2h': {'minutes': 120, 'description': '2 Hours'},
                '4h': {'minutes': 240, 'description': '4 Hours'}
            },
            'daily': {
                '1D': {'days': 1, 'description': 'Daily'},
                '1W': {'days': 7, 'description': 'Weekly'},
                '1M': {'days': 30, 'description': 'Monthly'},
                '3M': {'days': 90, 'description': 'Quarterly'},
                '6M': {'days': 180, 'description': 'Semi-Annual'},
                '1Y': {'days': 365, 'description': 'Annual'},
                '5Y': {'days': 1825, 'description': '5 Years'}
            }
        }
        
        # Timeframe analysis weights
        self.timeframe_weights = {
            '1m': 0.05,    # 5% weight
            '5m': 0.10,    # 10% weight
            '15m': 0.15,   # 15% weight
            '30m': 0.15,   # 15% weight
            '1h': 0.20,    # 20% weight
            '2h': 0.15,    # 15% weight
            '4h': 0.20,    # 20% weight
            '1D': 0.25,    # 25% weight
            '1W': 0.20,    # 20% weight
            '1M': 0.15,    # 15% weight
            '3M': 0.10,    # 10% weight
            '6M': 0.05,    # 5% weight
            '1Y': 0.03,    # 3% weight
            '5Y': 0.02     # 2% weight
        }
    
    def analyze_multi_timeframe(self, symbol: str, prices: List[float], 
                               volumes: List[float] = None) -> Dict:
        """Analyze a symbol across multiple timeframes"""
        
        try:
            analysis = {
                'symbol': symbol,
                'timestamp': datetime.now().isoformat(),
                'timeframe_analysis': {},
                'consensus_analysis': {},
                'recommendations': {}
            }
            
            # Analyze each timeframe
            for category, timeframes in self.timeframes.items():
                analysis['timeframe_analysis'][category] = {}
                
                for tf, config in timeframes.items():
                    tf_analysis = self._analyze_timeframe(
                        prices, volumes, tf, config
                    )
                    analysis['timeframe_analysis'][category][tf] = tf_analysis
            
            # Generate consensus analysis
            analysis['consensus_analysis'] = self._generate_consensus_analysis(
                analysis['timeframe_analysis']
            )
            
            # Generate recommendations
            analysis['recommendations'] = self._generate_recommendations(
                analysis['consensus_analysis']
            )
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"Multi-timeframe analysis failed: {e}")
            return {'error': str(e)}
    
    def _analyze_timeframe(self, prices: List[float], volumes: List[float],
                          timeframe: str, config: Dict) -> Dict:
        """Analyze a specific timeframe"""
        
        try:
            # Calculate technical indicators for this timeframe
            rsi = self._calculate_rsi(prices)
            macd, macd_signal = self._calculate_macd(prices)
            sma_20 = self._calculate_sma(prices, 20)
            sma_50 = self._calculate_sma(prices, 50)
            
            # Trend analysis
            trend = self._analyze_trend(prices, sma_20, sma_50)
            
            # Support and resistance
            support_resistance = self._calculate_support_resistance(prices)
            
            # Volume analysis
            volume_analysis = self._analyze_volume(volumes) if volumes else {}
            
            # Momentum analysis
            momentum = self._analyze_momentum(prices, rsi, macd)
            
            # Volatility analysis
            volatility = self._calculate_volatility(prices)
            
            return {
                'timeframe': timeframe,
                'description': config['description'],
                'technical_indicators': {
                    'rsi': round(rsi, 2),
                    'macd': round(macd, 4),
                    'macd_signal': round(macd_signal, 4),
                    'sma_20': round(sma_20, 2),
                    'sma_50': round(sma_50, 2)
                },
                'trend': trend,
                'support_resistance': support_resistance,
                'volume_analysis': volume_analysis,
                'momentum': momentum,
                'volatility': volatility,
                'signal': self._generate_timeframe_signal(trend, rsi, macd, macd_signal)
            }
            
        except Exception as e:
            self.logger.error(f"Timeframe analysis failed for {timeframe}: {e}")
            return {'error': str(e)}
    
    def _calculate_rsi(self, prices: List[float], period: int = 14) -> float:
        """Calculate RSI"""
        if len(prices) < period + 1:
            return 50.0
        
        deltas = np.diff(prices)
        gains = np.where(deltas > 0, deltas, 0)
        losses = np.where(deltas < 0, -deltas, 0)
        
        avg_gain = np.mean(gains[-period:])
        avg_loss = np.mean(losses[-period:])
        
        if avg_loss == 0:
            return 100.0
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
    def _calculate_macd(self, prices: List[float], fast: int = 12, slow: int = 26, signal: int = 9) -> Tuple[float, float]:
        """Calculate MACD"""
        if len(prices) < slow + signal:
            return 0.0, 0.0
        
        # Calculate EMAs
        ema_fast = self._calculate_ema(prices, fast)
        ema_slow = self._calculate_ema(prices, slow)
        
        macd_line = ema_fast - ema_slow
        
        # Signal line (EMA of MACD)
        macd_values = []
        for i in range(slow, len(prices)):
            macd_values.append(self._calculate_ema(prices[:i+1], fast) - self._calculate_ema(prices[:i+1], slow))
        
        if len(macd_values) >= signal:
            signal_line = self._calculate_ema(macd_values, signal)
        else:
            signal_line = macd_line
        
        return macd_line, signal_line
    
    def _calculate_ema(self, prices: List[float], period: int) -> float:
        """Calculate Exponential Moving Average"""
        if len(prices) < period:
            return prices[-1] if prices else 0.0
        
        multiplier = 2 / (period + 1)
        ema = prices[0]
        
        for price in prices[1:]:
            ema = (price * multiplier) + (ema * (1 - multiplier))
        
        return ema
    
    def _calculate_sma(self, prices: List[float], period: int) -> float:
        """Calculate Simple Moving Average"""
        if len(prices) < period:
            return prices[-1] if prices else 0.0
        
        return np.mean(prices[-period:])
    
    def _analyze_trend(self, prices: List[float], sma_20: float, sma_50: float) -> Dict:
        """Analyze trend direction and strength"""
        
        current_price = prices[-1]
        
        # Trend direction
        if sma_20 > sma_50 and current_price > sma_20:
            trend_direction = 'BULLISH'
        elif sma_20 < sma_50 and current_price < sma_20:
            trend_direction = 'BEARISH'
        else:
            trend_direction = 'NEUTRAL'
        
        # Trend strength
        trend_strength = abs(sma_20 - sma_50) / sma_50 * 100
        
        # Price position relative to moving averages
        if current_price > sma_20 > sma_50:
            position = 'ABOVE_ALL_MA'
        elif current_price < sma_20 < sma_50:
            position = 'BELOW_ALL_MA'
        elif sma_20 > current_price > sma_50:
            position = 'BETWEEN_MA'
        else:
            position = 'MIXED_MA'
        
        return {
            'direction': trend_direction,
            'strength': round(trend_strength, 2),
            'position': position,
            'sma_20': round(sma_20, 2),
            'sma_50': round(sma_50, 2)
        }
    
    def _calculate_support_resistance(self, prices: List[float]) -> Dict:
        """Calculate support and resistance levels"""
        
        if len(prices) < 20:
            return {}
        
        # Find local highs and lows
        highs = []
        lows = []
        
        for i in range(1, len(prices) - 1):
            if prices[i] > prices[i-1] and prices[i] > prices[i+1]:
                highs.append(prices[i])
            elif prices[i] < prices[i-1] and prices[i] < prices[i+1]:
                lows.append(prices[i])
        
        # Calculate levels
        resistance = max(highs) if highs else prices[-1]
        support = min(lows) if lows else prices[-1]
        
        current_price = prices[-1]
        
        # Distance to levels
        distance_to_resistance = ((resistance - current_price) / current_price) * 100
        distance_to_support = ((current_price - support) / current_price) * 100
        
        return {
            'resistance': round(resistance, 2),
            'support': round(support, 2),
            'distance_to_resistance': round(distance_to_resistance, 2),
            'distance_to_support': round(distance_to_support, 2)
        }
    
    def _analyze_volume(self, volumes: List[float]) -> Dict:
        """Analyze volume patterns"""
        
        if not volumes or len(volumes) < 20:
            return {}
        
        current_volume = volumes[-1]
        avg_volume = np.mean(volumes[-20:])
        
        volume_ratio = current_volume / avg_volume if avg_volume > 0 else 0
        
        # Volume trend
        recent_volumes = volumes[-5:]
        volume_trend = 'INCREASING' if recent_volumes[-1] > recent_volumes[0] else 'DECREASING'
        
        return {
            'current_volume': current_volume,
            'average_volume': round(avg_volume, 2),
            'volume_ratio': round(volume_ratio, 2),
            'volume_trend': volume_trend,
            'volume_status': 'HIGH' if volume_ratio > 1.5 else 'LOW' if volume_ratio < 0.5 else 'NORMAL'
        }
    
    def _analyze_momentum(self, prices: List[float], rsi: float, macd: float, macd_signal: float) -> Dict:
        """Analyze momentum indicators"""
        
        # RSI momentum
        rsi_momentum = 'OVERSOLD' if rsi < 30 else 'OVERBOUGHT' if rsi > 70 else 'NEUTRAL'
        
        # MACD momentum
        macd_momentum = 'BULLISH' if macd > macd_signal else 'BEARISH'
        macd_strength = abs(macd - macd_signal)
        
        # Price momentum
        if len(prices) >= 5:
            price_change = ((prices[-1] - prices[-5]) / prices[-5]) * 100
            price_momentum = 'BULLISH' if price_change > 0 else 'BEARISH'
        else:
            price_change = 0
            price_momentum = 'NEUTRAL'
        
        return {
            'rsi_momentum': rsi_momentum,
            'macd_momentum': macd_momentum,
            'macd_strength': round(macd_strength, 4),
            'price_momentum': price_momentum,
            'price_change_5_periods': round(price_change, 2)
        }
    
    def _calculate_volatility(self, prices: List[float]) -> Dict:
        """Calculate volatility metrics"""
        
        if len(prices) < 20:
            return {}
        
        # Calculate returns
        returns = np.diff(np.log(prices))
        
        # Historical volatility
        historical_vol = np.std(returns) * np.sqrt(252)
        
        # Recent volatility
        recent_vol = np.std(returns[-10:]) * np.sqrt(252)
        
        # Volatility trend
        vol_trend = 'INCREASING' if recent_vol > historical_vol else 'DECREASING'
        
        # Volatility regime
        if recent_vol > 0.3:
            regime = 'HIGH'
        elif recent_vol > 0.15:
            regime = 'MEDIUM'
        else:
            regime = 'LOW'
        
        return {
            'historical_volatility': round(historical_vol, 4),
            'recent_volatility': round(recent_vol, 4),
            'volatility_trend': vol_trend,
            'volatility_regime': regime
        }
    
    def _generate_timeframe_signal(self, trend: Dict, rsi: float, macd: float, macd_signal: float) -> Dict:
        """Generate trading signal for a timeframe"""
        
        # Base signal from trend
        base_signal = 'BUY' if trend['direction'] == 'BULLISH' else 'SELL' if trend['direction'] == 'BEARISH' else 'HOLD'
        
        # RSI confirmation
        rsi_confirmation = 'BULLISH' if rsi < 30 else 'BEARISH' if rsi > 70 else 'NEUTRAL'
        
        # MACD confirmation
        macd_confirmation = 'BULLISH' if macd > macd_signal else 'BEARISH'
        
        # Signal strength
        confirmations = 0
        if base_signal == 'BUY' and rsi_confirmation == 'BULLISH':
            confirmations += 1
        if base_signal == 'BUY' and macd_confirmation == 'BULLISH':
            confirmations += 1
        if base_signal == 'SELL' and rsi_confirmation == 'BEARISH':
            confirmations += 1
        if base_signal == 'SELL' and macd_confirmation == 'BEARISH':
            confirmations += 1
        
        # Calculate confidence
        confidence = min(confirmations / 2, 1.0)
        
        # Final signal
        if confidence >= 0.5:
            final_signal = base_signal
        else:
            final_signal = 'HOLD'
        
        return {
            'signal': final_signal,
            'confidence': round(confidence, 2),
            'base_signal': base_signal,
            'rsi_confirmation': rsi_confirmation,
            'macd_confirmation': macd_confirmation,
            'confirmations': confirmations
        }
    
    def _generate_consensus_analysis(self, timeframe_analysis: Dict) -> Dict:
        """Generate consensus analysis across timeframes"""
        
        try:
            # Collect all signals
            all_signals = []
            weighted_signals = []
            
            for category, timeframes in timeframe_analysis.items():
                for tf, analysis in timeframes.items():
                    if 'signal' in analysis and 'error' not in analysis:
                        signal_data = analysis['signal']
                        weight = self.timeframe_weights.get(tf, 0.1)
                        
                        all_signals.append(signal_data)
                        weighted_signals.append((signal_data, weight))
            
            if not all_signals:
                return {'error': 'No valid signals found'}
            
            # Calculate consensus
            buy_signals = [s for s in all_signals if s['signal'] == 'BUY']
            sell_signals = [s for s in all_signals if s['signal'] == 'SELL']
            hold_signals = [s for s in all_signals if s['signal'] == 'HOLD']
            
            total_signals = len(all_signals)
            buy_percentage = len(buy_signals) / total_signals
            sell_percentage = len(sell_signals) / total_signals
            hold_percentage = len(hold_signals) / total_signals
            
            # Weighted consensus
            weighted_buy = sum(w for s, w in weighted_signals if s['signal'] == 'BUY')
            weighted_sell = sum(w for s, w in weighted_signals if s['signal'] == 'SELL')
            weighted_hold = sum(w for s, w in weighted_signals if s['signal'] == 'HOLD')
            
            # Determine consensus signal
            if weighted_buy > weighted_sell and weighted_buy > weighted_hold:
                consensus_signal = 'BUY'
                consensus_strength = weighted_buy
            elif weighted_sell > weighted_buy and weighted_sell > weighted_hold:
                consensus_signal = 'SELL'
                consensus_strength = weighted_sell
            else:
                consensus_signal = 'HOLD'
                consensus_strength = weighted_hold
            
            # Calculate average confidence
            avg_confidence = np.mean([s['confidence'] for s in all_signals])
            
            return {
                'consensus_signal': consensus_signal,
                'consensus_strength': round(consensus_strength, 3),
                'average_confidence': round(avg_confidence, 3),
                'signal_distribution': {
                    'buy_percentage': round(buy_percentage * 100, 1),
                    'sell_percentage': round(sell_percentage * 100, 1),
                    'hold_percentage': round(hold_percentage * 100, 1)
                },
                'weighted_distribution': {
                    'weighted_buy': round(weighted_buy, 3),
                    'weighted_sell': round(weighted_sell, 3),
                    'weighted_hold': round(weighted_hold, 3)
                },
                'total_timeframes_analyzed': total_signals
            }
            
        except Exception as e:
            self.logger.error(f"Consensus analysis failed: {e}")
            return {'error': str(e)}
    
    def _generate_recommendations(self, consensus_analysis: Dict) -> Dict:
        """Generate trading recommendations based on consensus"""
        
        if 'error' in consensus_analysis:
            return {'error': consensus_analysis['error']}
        
        consensus_signal = consensus_analysis['consensus_signal']
        consensus_strength = consensus_analysis['consensus_strength']
        avg_confidence = consensus_analysis['average_confidence']
        
        # Position sizing recommendation
        if consensus_strength > 0.7 and avg_confidence > 0.7:
            position_size = 'LARGE'
            recommendation = 'STRONG_SIGNAL'
        elif consensus_strength > 0.5 and avg_confidence > 0.5:
            position_size = 'MEDIUM'
            recommendation = 'MODERATE_SIGNAL'
        else:
            position_size = 'SMALL'
            recommendation = 'WEAK_SIGNAL'
        
        # Risk management
        if consensus_signal == 'BUY':
            risk_level = 'MODERATE' if consensus_strength > 0.6 else 'HIGH'
            strategy = 'TREND_FOLLOWING' if consensus_strength > 0.7 else 'MEAN_REVERSION'
        elif consensus_signal == 'SELL':
            risk_level = 'HIGH' if consensus_strength > 0.6 else 'VERY_HIGH'
            strategy = 'TREND_FOLLOWING' if consensus_strength > 0.7 else 'MEAN_REVERSION'
        else:
            risk_level = 'LOW'
            strategy = 'WAIT_AND_WATCH'
        
        # Timeframe priority
        if consensus_strength > 0.6:
            priority_timeframes = ['1h', '4h', '1D']  # Focus on medium-term
        else:
            priority_timeframes = ['15m', '30m', '1h']  # Focus on short-term
        
        return {
            'position_sizing': position_size,
            'recommendation': recommendation,
            'risk_level': risk_level,
            'strategy': strategy,
            'priority_timeframes': priority_timeframes,
            'entry_timing': 'IMMEDIATE' if consensus_strength > 0.7 else 'WAIT_FOR_CONFIRMATION',
            'stop_loss_strategy': 'TIGHT' if consensus_strength > 0.7 else 'WIDE',
            'take_profit_strategy': 'EXTEND' if consensus_strength > 0.7 else 'QUICK'
        }
    
    def get_timeframe_summary(self, symbol: str, analysis: Dict) -> Dict:
        """Get a summary of multi-timeframe analysis"""
        
        if 'error' in analysis:
            return {'error': analysis['error']}
        
        # Extract key information
        consensus = analysis.get('consensus_analysis', {})
        recommendations = analysis.get('recommendations', {})
        
        summary = {
            'symbol': symbol,
            'timestamp': analysis.get('timestamp'),
            'consensus_signal': consensus.get('consensus_signal', 'UNKNOWN'),
            'consensus_strength': consensus.get('consensus_strength', 0),
            'average_confidence': consensus.get('average_confidence', 0),
            'position_sizing': recommendations.get('position_sizing', 'UNKNOWN'),
            'risk_level': recommendations.get('risk_level', 'UNKNOWN'),
            'strategy': recommendations.get('strategy', 'UNKNOWN'),
            'total_timeframes': consensus.get('total_timeframes_analyzed', 0)
        }
        
        # Add signal distribution
        signal_dist = consensus.get('signal_distribution', {})
        summary['signal_distribution'] = signal_dist
        
        return summary
    
    def export_analysis(self, analysis: Dict, format: str = 'json') -> str:
        """Export analysis in specified format"""
        
        if format == 'json':
            import json
            return json.dumps(analysis, default=str, indent=2)
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def compare_symbols(self, symbols: List[str], analyses: List[Dict]) -> Dict:
        """Compare multiple symbols across timeframes"""
        
        if len(symbols) != len(analyses):
            return {'error': 'Number of symbols and analyses must match'}
        
        comparison = {
            'timestamp': datetime.now().isoformat(),
            'symbols': symbols,
            'comparison': {}
        }
        
        # Compare consensus signals
        consensus_signals = []
        consensus_strengths = []
        confidences = []
        
        for analysis in analyses:
            if 'consensus_analysis' in analysis:
                consensus = analysis['consensus_analysis']
                consensus_signals.append(consensus.get('consensus_signal', 'UNKNOWN'))
                consensus_strengths.append(consensus.get('consensus_strength', 0))
                confidences.append(consensus.get('average_confidence', 0))
        
        comparison['comparison'] = {
            'consensus_signals': consensus_signals,
            'consensus_strengths': consensus_strengths,
            'confidences': confidences,
            'strongest_signal': symbols[np.argmax(consensus_strengths)] if consensus_strengths else 'N/A',
            'highest_confidence': symbols[np.argmax(confidences)] if confidences else 'N/A'
        }
        
        return comparison
