import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
import math

class EnhancedIndicatorsService:
    """Enhanced technical indicators service with SMC/ICT integration"""
    
    def __init__(self):
        self.fibonacci_levels = [0, 0.236, 0.382, 0.5, 0.618, 0.786, 1.0]
    
    def calculate_bollinger_bands(self, prices: List[float], period: int = 20, std_dev: float = 2.0) -> Dict:
        """Calculate Bollinger Bands with SMC/ICT integration"""
        if len(prices) < period:
            return {}
        
        prices_array = np.array(prices)
        sma = np.mean(prices_array[-period:])
        std = np.std(prices_array[-period:])
        
        upper_band = sma + (std_dev * std)
        lower_band = sma - (std_dev * std)
        middle_band = sma
        
        # SMC/ICT Analysis
        current_price = prices[-1]
        bb_position = (current_price - lower_band) / (upper_band - lower_band)  # 0-1 scale
        
        # Identify premium/discount zones
        premium_zone = bb_position > 0.8  # Above 80% of BB range
        discount_zone = bb_position < 0.2  # Below 20% of BB range
        
        # Squeeze detection (bands narrowing)
        band_width = upper_band - lower_band
        avg_band_width = np.mean([upper_band - lower_band for _ in range(period)])
        squeeze = band_width < (avg_band_width * 0.7)
        
        return {
            'upper_band': round(upper_band, 4),
            'middle_band': round(middle_band, 4),
            'lower_band': round(lower_band, 4),
            'bb_position': round(bb_position, 4),
            'premium_zone': premium_zone,
            'discount_zone': discount_zone,
            'squeeze': squeeze,
            'band_width': round(band_width, 4),
            'volatility': 'HIGH' if band_width > (avg_band_width * 1.3) else 'LOW' if squeeze else 'NORMAL'
        }
    
    def calculate_fibonacci_retracements(self, high: float, low: float) -> Dict:
        """Calculate Fibonacci retracement levels for SMC/ICT order blocks"""
        price_range = high - low
        
        retracements = {}
        for level in self.fibonacci_levels:
            if level == 0:
                retracements[f'fib_{int(level*100)}'] = low
            elif level == 1.0:
                retracements[f'fib_{int(level*100)}'] = high
            else:
                retracement_price = high - (price_range * level)
                retracements[f'fib_{int(level*100)}'] = round(retracement_price, 4)
        
        # SMC/ICT Integration
        # Key levels for order blocks
        key_levels = {
            'order_block_zone_1': retracements['fib_382'],  # 38.2% - Strong support/resistance
            'order_block_zone_2': retracements['fib_618'],  # 61.8% - Golden ratio
            'fair_value_gap_zone': retracements['fib_500'],  # 50% - Fair value
            'liquidity_zone_1': retracements['fib_236'],   # 23.6% - Shallow retracement
            'liquidity_zone_2': retracements['fib_786']    # 78.6% - Deep retracement
        }
        
        return {
            'retracements': retracements,
            'key_levels': key_levels,
            'price_range': round(price_range, 4),
            'high': high,
            'low': low
        }
    
    def calculate_fibonacci_extensions(self, high: float, low: float, retracement: float) -> Dict:
        """Calculate Fibonacci extensions for take profit targets"""
        price_range = high - low
        retracement_price = high - (price_range * retracement)
        
        extensions = {}
        for level in [1.272, 1.618, 2.0, 2.618]:
            extension_price = retracement_price + (price_range * level)
            extensions[f'fib_{int(level*100)}'] = round(extension_price, 4)
        
        return {
            'extensions': extensions,
            'retracement_price': round(retracement_price, 4),
            'retracement_level': retracement
        }
    
    def calculate_volume_profile(self, prices: List[float], volumes: List[float], bins: int = 10) -> Dict:
        """Calculate Volume Profile for SMC/ICT liquidity analysis"""
        if len(prices) != len(volumes) or len(prices) == 0:
            return {}
        
        # Create price bins
        min_price, max_price = min(prices), max(prices)
        price_bins = np.linspace(min_price, max_price, bins + 1)
        
        volume_profile = {}
        for i in range(bins):
            bin_low = price_bins[i]
            bin_high = price_bins[i + 1]
            bin_volume = 0
            
            for price, volume in zip(prices, volumes):
                if bin_low <= price < bin_high:
                    bin_volume += volume
            
            volume_profile[f'bin_{i+1}'] = {
                'price_range': (round(bin_low, 4), round(bin_high, 4)),
                'volume': round(bin_volume, 2)
            }
        
        # Find high volume nodes (liquidity zones)
        volumes_list = [v['volume'] for v in volume_profile.values()]
        avg_volume = np.mean(volumes_list)
        high_volume_nodes = []
        
        for bin_name, bin_data in volume_profile.items():
            if bin_data['volume'] > (avg_volume * 1.5):
                high_volume_nodes.append({
                    'bin': bin_name,
                    'price_range': bin_data['price_range'],
                    'volume': bin_data['volume']
                })
        
        # Find low volume nodes (fair value gaps)
        low_volume_nodes = []
        for bin_name, bin_data in volume_profile.items():
            if bin_data['volume'] < (avg_volume * 0.5):
                low_volume_nodes.append({
                    'bin': bin_name,
                    'price_range': bin_data['price_range'],
                    'volume': bin_data['volume']
                })
        
        return {
            'volume_profile': volume_profile,
            'high_volume_nodes': high_volume_nodes,
            'low_volume_nodes': low_volume_nodes,
            'average_volume': round(avg_volume, 2),
            'total_volume': round(sum(volumes), 2)
        }
    
    def calculate_market_structure(self, highs: List[float], lows: List[float], prices: List[float]) -> Dict:
        """Analyze market structure for SMC/ICT trend identification"""
        if len(highs) < 3 or len(lows) < 3:
            return {'structure': 'UNKNOWN', 'trend': 'NEUTRAL'}
        
        # Higher Highs and Lower Lows analysis
        recent_highs = highs[-3:]
        recent_lows = lows[-3:]
        
        # Check for Higher Highs (HH)
        higher_highs = all(recent_highs[i] > recent_highs[i-1] for i in range(1, len(recent_highs)))
        
        # Check for Lower Lows (LL)
        lower_lows = all(recent_lows[i] < recent_lows[i-1] for i in range(1, len(recent_lows)))
        
        # Check for Higher Lows (HL)
        higher_lows = all(recent_lows[i] > recent_lows[i-1] for i in range(1, len(recent_lows)))
        
        # Check for Lower Highs (LH)
        lower_highs = all(recent_highs[i] < recent_highs[i-1] for i in range(1, len(recent_highs)))
        
        # Determine market structure
        if higher_highs and higher_lows:
            structure = 'BULLISH'
            trend = 'UPTREND'
        elif lower_highs and lower_lows:
            structure = 'BEARISH'
            trend = 'DOWNTREND'
        elif higher_highs and lower_lows:
            structure = 'BULLISH'
            trend = 'WEAK_UPTREND'
        elif lower_highs and higher_lows:
            structure = 'BEARISH'
            trend = 'WEAK_DOWNTREND'
        else:
            structure = 'CONSOLIDATION'
            trend = 'SIDEWAYS'
        
        # Current price position relative to recent structure
        current_price = prices[-1]
        recent_high = max(recent_highs)
        recent_low = min(recent_lows)
        
        if current_price > recent_high:
            position = 'ABOVE_STRUCTURE'
        elif current_price < recent_low:
            position = 'BELOW_STRUCTURE'
        else:
            position = 'WITHIN_STRUCTURE'
        
        return {
            'structure': structure,
            'trend': trend,
            'position': position,
            'recent_high': round(recent_high, 4),
            'recent_low': round(recent_low, 4),
            'current_price': round(current_price, 4),
            'higher_highs': higher_highs,
            'higher_lows': higher_lows,
            'lower_highs': lower_highs,
            'lower_lows': lower_lows
        }
    
    def calculate_support_resistance(self, prices: List[float], volumes: List[float], sensitivity: float = 0.02) -> Dict:
        """Calculate dynamic support and resistance levels"""
        if len(prices) < 20:
            return {}
        
        # Find local highs and lows
        highs = []
        lows = []
        
        for i in range(1, len(prices) - 1):
            if prices[i] > prices[i-1] and prices[i] > prices[i+1]:
                highs.append((i, prices[i], volumes[i]))
            elif prices[i] < prices[i-1] and prices[i] < prices[i+1]:
                lows.append((i, prices[i], volumes[i]))
        
        # Cluster nearby levels
        def cluster_levels(levels, threshold):
            if not levels:
                return []
            
            clusters = []
            current_cluster = [levels[0]]
            
            for level in levels[1:]:
                if abs(level[1] - current_cluster[-1][1]) / current_cluster[-1][1] < threshold:
                    current_cluster.append(level)
                else:
                    clusters.append(current_cluster)
                    current_cluster = [level]
            
            clusters.append(current_cluster)
            return clusters
        
        high_clusters = cluster_levels(highs, sensitivity)
        low_clusters = cluster_levels(lows, sensitivity)
        
        # Calculate weighted levels
        resistance_levels = []
        for cluster in high_clusters:
            total_volume = sum(level[2] for level in cluster)
            weighted_price = sum(level[1] * level[2] for level in cluster) / total_volume
            resistance_levels.append({
                'price': round(weighted_price, 4),
                'strength': len(cluster),
                'volume': total_volume,
                'type': 'resistance'
            })
        
        support_levels = []
        for cluster in low_clusters:
            total_volume = sum(level[2] for level in cluster)
            weighted_price = sum(level[1] * level[2] for level in cluster) / total_volume
            support_levels.append({
                'price': round(weighted_price, 4),
                'strength': len(cluster),
                'volume': total_volume,
                'type': 'support'
            })
        
        # Sort by strength
        resistance_levels.sort(key=lambda x: x['strength'], reverse=True)
        support_levels.sort(key=lambda x: x['strength'], reverse=True)
        
        return {
            'resistance_levels': resistance_levels[:5],  # Top 5
            'support_levels': support_levels[:5],        # Top 5
            'total_highs': len(highs),
            'total_lows': len(lows)
        }
    
    def calculate_momentum_divergence(self, prices: List[float], rsi_values: List[float]) -> Dict:
        """Detect RSI divergence for SMC/ICT confirmation"""
        if len(prices) < 10 or len(rsi_values) < 10:
            return {}
        
        # Find recent highs and lows in price and RSI
        price_highs = []
        price_lows = []
        rsi_highs = []
        rsi_lows = []
        
        for i in range(1, len(prices) - 1):
            if prices[i] > prices[i-1] and prices[i] > prices[i+1]:
                price_highs.append((i, prices[i]))
            elif prices[i] < prices[i-1] and prices[i] < prices[i+1]:
                price_lows.append((i, prices[i]))
        
        for i in range(1, len(rsi_values) - 1):
            if rsi_values[i] > rsi_values[i-1] and rsi_values[i] > rsi_values[i+1]:
                rsi_highs.append((i, rsi_values[i]))
            elif rsi_values[i] < rsi_values[i-1] and rsi_values[i] < rsi_values[i+1]:
                rsi_lows.append((i, rsi_values[i]))
        
        # Check for divergence
        bullish_divergence = False
        bearish_divergence = False
        
        if len(price_lows) >= 2 and len(rsi_lows) >= 2:
            # Bullish divergence: Price makes lower low, RSI makes higher low
            if (price_lows[-1][1] < price_lows[-2][1] and 
                rsi_lows[-1][1] > rsi_lows[-2][1]):
                bullish_divergence = True
        
        if len(price_highs) >= 2 and len(rsi_highs) >= 2:
            # Bearish divergence: Price makes higher high, RSI makes lower high
            if (price_highs[-1][1] > price_highs[-2][1] and 
                rsi_highs[-1][1] < rsi_highs[-2][1]):
                bearish_divergence = True
        
        return {
            'bullish_divergence': bullish_divergence,
            'bearish_divergence': bearish_divergence,
            'price_highs': len(price_highs),
            'price_lows': len(price_lows),
            'rsi_highs': len(rsi_highs),
            'rsi_lows': len(rsi_lows)
        }
    
    def calculate_volatility_forecast(self, prices: List[float], period: int = 20) -> Dict:
        """Forecast volatility for position sizing"""
        if len(prices) < period:
            return {}
        
        # Calculate historical volatility
        returns = np.diff(np.log(prices))
        historical_vol = np.std(returns) * np.sqrt(252)  # Annualized
        
        # Calculate current volatility
        recent_returns = returns[-period:]
        current_vol = np.std(recent_returns) * np.sqrt(252)
        
        # Volatility trend
        vol_trend = 'INCREASING' if current_vol > historical_vol * 1.1 else 'DECREASING' if current_vol < historical_vol * 0.9 else 'STABLE'
        
        # Volatility regime
        if current_vol > 0.3:
            regime = 'HIGH'
        elif current_vol > 0.15:
            regime = 'MEDIUM'
        else:
            regime = 'LOW'
        
        # Position size recommendation based on volatility
        if regime == 'HIGH':
            position_size = 'SMALL'
        elif regime == 'MEDIUM':
            position_size = 'MEDIUM'
        else:
            position_size = 'LARGE'
        
        return {
            'historical_volatility': round(historical_vol, 4),
            'current_volatility': round(current_vol, 4),
            'volatility_trend': vol_trend,
            'volatility_regime': regime,
            'position_size_recommendation': position_size,
            'volatility_change': round((current_vol - historical_vol) / historical_vol * 100, 2)
        }
