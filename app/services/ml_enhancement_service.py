import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
import math
import logging

class MLEnhancementService:
    """Machine Learning enhancement service for improved trading signals"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.pattern_weights = {
            'bullish_engulfing': 0.85,
            'bearish_engulfing': 0.85,
            'doji': 0.70,
            'hammer': 0.80,
            'shooting_star': 0.80,
            'three_white_soldiers': 0.90,
            'three_black_crows': 0.90,
            'morning_star': 0.88,
            'evening_star': 0.88
        }
        
        self.regime_thresholds = {
            'trend_strength': 0.7,
            'volatility_regime': 0.6,
            'volume_confirmation': 0.65
        }
    
    def detect_candlestick_patterns(self, open_prices: List[float], high_prices: List[float], 
                                  low_prices: List[float], close_prices: List[float]) -> Dict:
        """Detect candlestick patterns for signal validation"""
        
        if len(open_prices) < 3:
            return {}
        
        patterns = {}
        
        # Get last 3 candles for pattern detection
        o1, o2, o3 = open_prices[-3:]
        h1, h2, h3 = high_prices[-3:]
        l1, l2, l3 = low_prices[-3:]
        c1, c2, c3 = close_prices[-3:]
        
        # Calculate body and shadow sizes
        body1, body2, body3 = abs(c1 - o1), abs(c2 - o2), abs(c3 - o3)
        upper_shadow1 = h1 - max(o1, c1)
        lower_shadow1 = min(o1, c1) - l1
        
        # 1. Bullish Engulfing
        if (c2 < o2 and  # Previous candle is bearish
            c1 > o1 and  # Current candle is bullish
            c1 > o2 and  # Current close above previous open
            o1 < c2):    # Current open below previous close
            patterns['bullish_engulfing'] = {
                'strength': 0.85,
                'description': 'Strong reversal pattern',
                'signal': 'BUY'
            }
        
        # 2. Bearish Engulfing
        if (c2 > o2 and  # Previous candle is bullish
            c1 < o1 and  # Current candle is bearish
            c1 < o2 and  # Current close below previous open
            o1 > c2):    # Current open above previous close
            patterns['bearish_engulfing'] = {
                'strength': 0.85,
                'description': 'Strong reversal pattern',
                'signal': 'SELL'
            }
        
        # 3. Doji
        doji_threshold = (h1 - l1) * 0.1
        if body1 <= doji_threshold:
            patterns['doji'] = {
                'strength': 0.70,
                'description': 'Indecision pattern',
                'signal': 'NEUTRAL'
            }
        
        # 4. Hammer
        if (lower_shadow1 > 2 * body1 and  # Long lower shadow
            upper_shadow1 < body1 * 0.5 and  # Short upper shadow
            c1 > o1):  # Bullish close
            patterns['hammer'] = {
                'strength': 0.80,
                'description': 'Bullish reversal pattern',
                'signal': 'BUY'
            }
        
        # 5. Shooting Star
        if (upper_shadow1 > 2 * body1 and  # Long upper shadow
            lower_shadow1 < body1 * 0.5 and  # Short lower shadow
            c1 < o1):  # Bearish close
            patterns['shooting_star'] = {
                'strength': 0.80,
                'description': 'Bearish reversal pattern',
                'signal': 'SELL'
            }
        
        # 6. Three White Soldiers
        if (len(open_prices) >= 3 and
            c1 > o1 and c2 > o2 and c3 > o3 and  # All bullish
            c1 > c2 > c3 and  # Higher highs
            o1 > o2 > o3):    # Higher opens
            patterns['three_white_soldiers'] = {
                'strength': 0.90,
                'description': 'Strong bullish continuation',
                'signal': 'BUY'
            }
        
        # 7. Three Black Crows
        if (len(open_prices) >= 3 and
            c1 < o1 and c2 < o2 and c3 < o3 and  # All bearish
            c1 < c2 < c3 and  # Lower lows
            o1 < o2 < o3):    # Lower opens
            patterns['three_black_crows'] = {
                'strength': 0.90,
                'description': 'Strong bearish continuation',
                'signal': 'SELL'
            }
        
        # 8. Morning Star
        if (len(open_prices) >= 3 and
            c3 < o3 and  # First candle bearish
            abs(c2 - o2) < (h2 - l2) * 0.3 and  # Second candle small
            c1 > o1 and  # Third candle bullish
            c1 > (o3 + c3) / 2):  # Third close above first midpoint
            patterns['morning_star'] = {
                'strength': 0.88,
                'description': 'Bullish reversal pattern',
                'signal': 'BUY'
            }
        
        # 9. Evening Star
        if (len(open_prices) >= 3 and
            c3 > o3 and  # First candle bullish
            abs(c2 - o2) < (h2 - l2) * 0.3 and  # Second candle small
            c1 < o1 and  # Third candle bearish
            c1 < (o3 + c3) / 2):  # Third close below first midpoint
            patterns['evening_star'] = {
                'strength': 0.88,
                'description': 'Bearish reversal pattern',
                'signal': 'SELL'
            }
        
        return patterns
    
    def detect_market_regime(self, prices: List[float], volumes: List[float], 
                           rsi_values: List[float], macd_values: List[float]) -> Dict:
        """Detect market regime for adaptive signal generation"""
        
        if len(prices) < 20:
            return {'regime': 'UNKNOWN', 'confidence': 0.0}
        
        # 1. Trend Detection
        trend_strength = self._calculate_trend_strength(prices)
        
        # 2. Volatility Regime
        volatility_regime = self._detect_volatility_regime(prices)
        
        # 3. Volume Confirmation
        volume_confirmation = self._analyze_volume_confirmation(volumes, prices)
        
        # 4. Momentum Analysis
        momentum_regime = self._analyze_momentum(rsi_values, macd_values)
        
        # Determine overall regime
        regime_score = (trend_strength + volatility_regime + volume_confirmation + momentum_regime) / 4
        
        if regime_score > 0.7:
            regime = 'TRENDING'
        elif regime_score > 0.4:
            regime = 'CONSOLIDATING'
        else:
            regime = 'CHOPPY'
        
        return {
            'regime': regime,
            'confidence': round(regime_score, 3),
            'trend_strength': round(trend_strength, 3),
            'volatility_regime': round(volatility_regime, 3),
            'volume_confirmation': round(volume_confirmation, 3),
            'momentum_regime': round(momentum_regime, 3),
            'characteristics': self._get_regime_characteristics(regime, regime_score)
        }
    
    def _calculate_trend_strength(self, prices: List[float]) -> float:
        """Calculate trend strength using linear regression"""
        if len(prices) < 10:
            return 0.5
        
        # Use last 10 prices for trend calculation
        recent_prices = prices[-10:]
        x = np.arange(len(recent_prices))
        
        # Linear regression
        slope, intercept = np.polyfit(x, recent_prices, 1)
        
        # Calculate R-squared (trend strength)
        y_pred = slope * x + intercept
        ss_res = np.sum((recent_prices - y_pred) ** 2)
        ss_tot = np.sum((recent_prices - np.mean(recent_prices)) ** 2)
        r_squared = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0
        
        # Normalize to 0-1 scale
        trend_strength = min(r_squared, 1.0)
        
        return trend_strength
    
    def _detect_volatility_regime(self, prices: List[float]) -> float:
        """Detect volatility regime using rolling standard deviation"""
        if len(prices) < 20:
            return 0.5
        
        # Calculate rolling volatility
        returns = np.diff(np.log(prices))
        rolling_vol = np.std(returns[-20:])
        
        # Compare to historical volatility
        historical_vol = np.std(returns)
        
        if rolling_vol > historical_vol * 1.5:
            return 0.9  # High volatility
        elif rolling_vol < historical_vol * 0.7:
            return 0.3  # Low volatility
        else:
            return 0.6  # Normal volatility
    
    def _analyze_volume_confirmation(self, volumes: List[float], prices: List[float]) -> float:
        """Analyze volume confirmation of price movements"""
        if len(volumes) < 10 or len(prices) < 10:
            return 0.5
        
        # Calculate volume trend
        recent_volumes = volumes[-10:]
        recent_prices = prices[-10:]
        
        # Check if volume increases with price movement
        volume_confirmation = 0.0
        
        for i in range(1, len(recent_prices)):
            price_change = recent_prices[i] - recent_prices[i-1]
            volume_change = recent_volumes[i] - recent_volumes[i-1]
            
            # Volume should increase with significant price moves
            if abs(price_change) > np.std(recent_prices) * 0.5:
                if (price_change > 0 and volume_change > 0) or (price_change < 0 and volume_change > 0):
                    volume_confirmation += 0.1
        
        return min(volume_confirmation, 1.0)
    
    def _analyze_momentum(self, rsi_values: List[float], macd_values: List[float]) -> float:
        """Analyze momentum regime using RSI and MACD"""
        if len(rsi_values) < 5 or len(macd_values) < 5:
            return 0.5
        
        # RSI momentum
        rsi_momentum = 0.0
        if len(rsi_values) >= 3:
            rsi_trend = rsi_values[-1] - rsi_values[-3]
            if rsi_trend > 10:
                rsi_momentum = 0.8  # Strong bullish momentum
            elif rsi_trend < -10:
                rsi_momentum = 0.2  # Strong bearish momentum
            else:
                rsi_momentum = 0.5  # Neutral momentum
        
        # MACD momentum
        macd_momentum = 0.0
        if len(macd_values) >= 3:
            macd_trend = macd_values[-1] - macd_values[-3]
            if abs(macd_trend) > 0.1:
                macd_momentum = 0.8 if macd_trend > 0 else 0.2
            else:
                macd_momentum = 0.5
        
        return (rsi_momentum + macd_momentum) / 2
    
    def _get_regime_characteristics(self, regime: str, confidence: float) -> Dict:
        """Get characteristics and recommendations for each regime"""
        characteristics = {
            'TRENDING': {
                'description': 'Strong directional movement with clear trend',
                'strategy': 'Trend following with pullback entries',
                'position_sizing': 'MEDIUM to LARGE',
                'stop_loss': 'Tighter stops below trend lines',
                'take_profit': 'Extend targets in trend direction'
            },
            'CONSOLIDATING': {
                'description': 'Sideways movement with defined range',
                'strategy': 'Range trading with support/resistance',
                'position_sizing': 'SMALL to MEDIUM',
                'stop_loss': 'Wider stops outside range',
                'take_profit': 'Target range boundaries'
            },
            'CHOPPY': {
                'description': 'Unpredictable, low-quality movements',
                'strategy': 'Wait for clear setups or reduce position size',
                'position_sizing': 'SMALL only',
                'stop_loss': 'Very tight stops',
                'take_profit': 'Quick profits, don\'t hold'
            }
        }
        
        return characteristics.get(regime, {})
    
    def enhance_signal_confidence(self, base_signal: str, base_confidence: float,
                                patterns: Dict, regime: Dict, 
                                technical_indicators: Dict) -> Dict:
        """Enhance signal confidence using ML analysis"""
        
        # Start with base confidence
        enhanced_confidence = base_confidence
        
        # 1. Pattern confirmation
        pattern_boost = 0.0
        if patterns:
            for pattern_name, pattern_data in patterns.items():
                if pattern_data['signal'] == base_signal:
                    pattern_boost += pattern_data['strength'] * 0.1
                elif pattern_data['signal'] == 'NEUTRAL':
                    pattern_boost += 0.05
                else:
                    pattern_boost -= 0.1  # Contradictory pattern
        
        # 2. Regime alignment
        regime_boost = 0.0
        if regime['regime'] == 'TRENDING':
            if base_signal in ['BUY', 'SELL']:
                regime_boost += 0.15  # Trending markets favor directional trades
        elif regime['regime'] == 'CONSOLIDATING':
            if base_signal == 'HOLD':
                regime_boost += 0.1  # Consolidating markets favor waiting
        
        # 3. Technical indicator confirmation
        tech_boost = 0.0
        if technical_indicators:
            # RSI confirmation
            rsi = technical_indicators.get('rsi', 50)
            if base_signal == 'BUY' and rsi < 30:
                tech_boost += 0.1
            elif base_signal == 'SELL' and rsi > 70:
                tech_boost += 0.1
            
            # MACD confirmation
            macd = technical_indicators.get('macd', 0)
            macd_signal = technical_indicators.get('macd_signal', 0)
            if base_signal == 'BUY' and macd > macd_signal:
                tech_boost += 0.05
            elif base_signal == 'SELL' and macd < macd_signal:
                tech_boost += 0.05
        
        # Apply boosts
        enhanced_confidence += pattern_boost + regime_boost + tech_boost
        
        # Clamp to 0-1 range
        enhanced_confidence = max(0.0, min(1.0, enhanced_confidence))
        
        return {
            'original_confidence': base_confidence,
            'enhanced_confidence': round(enhanced_confidence, 3),
            'pattern_boost': round(pattern_boost, 3),
            'regime_boost': round(regime_boost, 3),
            'technical_boost': round(tech_boost, 3),
            'confidence_increase': round(enhanced_confidence - base_confidence, 3),
            'recommendation': self._get_confidence_recommendation(enhanced_confidence)
        }
    
    def _get_confidence_recommendation(self, confidence: float) -> str:
        """Get recommendation based on confidence level"""
        if confidence >= 0.9:
            return "STRONG SIGNAL - High probability setup"
        elif confidence >= 0.8:
            return "GOOD SIGNAL - Well-confirmed setup"
        elif confidence >= 0.7:
            return "MODERATE SIGNAL - Decent setup with some risk"
        elif confidence >= 0.6:
            return "WEAK SIGNAL - Low probability, consider waiting"
        else:
            return "AVOID - Poor setup, high risk"
    
    def generate_adaptive_signals(self, base_analysis: Dict, 
                                market_data: Dict) -> Dict:
        """Generate adaptive signals based on market regime and patterns"""
        
        # Extract data
        base_signal = base_analysis.get('signals', [{}])[0].get('type', 'HOLD')
        base_confidence = base_analysis.get('signals', [{}])[0].get('confidence', 0.5)
        
        # Detect patterns
        patterns = self.detect_candlestick_patterns(
            market_data.get('open_prices', []),
            market_data.get('high_prices', []),
            market_data.get('low_prices', []),
            market_data.get('close_prices', [])
        )
        
        # Detect market regime
        regime = self.detect_market_regime(
            market_data.get('close_prices', []),
            market_data.get('volumes', []),
            market_data.get('rsi_values', []),
            market_data.get('macd_values', [])
        )
        
        # Enhance signal confidence
        enhanced_confidence = self.enhance_signal_confidence(
            base_signal, base_confidence, patterns, regime,
            base_analysis.get('technical_analysis', {})
        )
        
        # Generate adaptive recommendations
        adaptive_recommendations = self._generate_adaptive_recommendations(
            base_signal, enhanced_confidence, patterns, regime
        )
        
        return {
            'base_signal': base_signal,
            'enhanced_confidence': enhanced_confidence,
            'detected_patterns': patterns,
            'market_regime': regime,
            'adaptive_recommendations': adaptive_recommendations,
            'signal_quality': self._assess_signal_quality(enhanced_confidence, patterns, regime)
        }
    
    def _generate_adaptive_recommendations(self, signal: str, confidence: Dict, 
                                         patterns: Dict, regime: Dict) -> Dict:
        """Generate adaptive trading recommendations"""
        
        recommendations = {
            'position_sizing': 'MEDIUM',
            'entry_strategy': 'Standard entry',
            'stop_loss_strategy': 'Standard stop',
            'take_profit_strategy': 'Standard target',
            'risk_management': 'Standard risk',
            'timing': 'Immediate entry'
        }
        
        # Adjust based on confidence
        if confidence['enhanced_confidence'] >= 0.9:
            recommendations['position_sizing'] = 'LARGE'
            recommendations['entry_strategy'] = 'Aggressive entry'
        elif confidence['enhanced_confidence'] <= 0.6:
            recommendations['position_sizing'] = 'SMALL'
            recommendations['entry_strategy'] = 'Conservative entry'
            recommendations['timing'] = 'Wait for confirmation'
        
        # Adjust based on regime
        if regime['regime'] == 'TRENDING':
            recommendations['stop_loss_strategy'] = 'Trend-following stops'
            recommendations['take_profit_strategy'] = 'Extend targets'
        elif regime['regime'] == 'CHOPPY':
            recommendations['stop_loss_strategy'] = 'Tight stops'
            recommendations['take_profit_strategy'] = 'Quick profits'
        
        # Adjust based on patterns
        if patterns:
            strong_patterns = [p for p in patterns.values() if p['strength'] >= 0.8]
            if strong_patterns:
                recommendations['entry_strategy'] = 'Pattern-based entry'
                recommendations['timing'] = 'Enter on pattern completion'
        
        return recommendations
    
    def _assess_signal_quality(self, confidence: Dict, patterns: Dict, regime: Dict) -> str:
        """Assess overall signal quality"""
        
        quality_score = 0
        
        # Confidence contribution (40%)
        quality_score += confidence['enhanced_confidence'] * 0.4
        
        # Pattern contribution (30%)
        if patterns:
            avg_pattern_strength = np.mean([p['strength'] for p in patterns.values()])
            quality_score += avg_pattern_strength * 0.3
        
        # Regime contribution (30%)
        quality_score += regime['confidence'] * 0.3
        
        # Determine quality level
        if quality_score >= 0.8:
            return "EXCELLENT"
        elif quality_score >= 0.7:
            return "GOOD"
        elif quality_score >= 0.6:
            return "FAIR"
        else:
            return "POOR"
