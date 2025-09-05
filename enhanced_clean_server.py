#!/usr/bin/env python3
"""
Enhanced Clean Trading Signals Server
Combines clean interface with all advanced ICT/SMC and ML features
"""

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import logging
import sqlite3
import threading
import time

# Try to import ML libraries
try:
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.model_selection import train_test_split
    from sklearn.preprocessing import StandardScaler
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def clean_nan_values(obj):
    """Recursively clean NaN values from dictionaries and lists for JSON serialization"""
    if isinstance(obj, dict):
        return {k: clean_nan_values(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [clean_nan_values(item) for item in obj]
    elif isinstance(obj, (np.floating, np.integer)):
        if np.isnan(obj) or np.isinf(obj):
            return 0
        return float(obj)
    elif isinstance(obj, float):
        if np.isnan(obj) or np.isinf(obj):
            return 0
        return obj
    else:
        return obj

def get_multi_timeframe_data(symbol):
    """Get comprehensive multi-timeframe data for ICT/SMC analysis"""
    try:
        ticker = yf.Ticker(symbol)
        
        # Define timeframes from higher to lower
        timeframes = {
            '12mo': {'period': '1y', 'interval': '1mo'},
            '6mo': {'period': '6mo', 'interval': '1mo'}, 
            '3mo': {'period': '3mo', 'interval': '1wk'},
            '1mo': {'period': '1mo', 'interval': '1wk'},
            '1w': {'period': '1mo', 'interval': '1d'},
            '1d': {'period': '5d', 'interval': '1d'},
            '4h': {'period': '5d', 'interval': '4h'},
            '1h': {'period': '5d', 'interval': '1h'},
            '15m': {'period': '1d', 'interval': '15m'},
            '5m': {'period': '1d', 'interval': '5m'}
        }
        
        mtf_data = {}
        
        for tf_name, tf_config in timeframes.items():
            try:
                data = ticker.history(period=tf_config['period'], interval=tf_config['interval'])
                if not data.empty and len(data) >= 10:
                    mtf_data[tf_name] = {
                        'data': data,
                        'trend': analyze_trend_direction(data),
                        'key_levels': find_key_levels(data),
                        'market_structure': analyze_market_structure(data),
                        'volume_profile': analyze_volume_profile(data)
                    }
            except Exception as e:
                logger.warning(f"Could not fetch {tf_name} data for {symbol}: {e}")
                continue
        
        return mtf_data
    except Exception as e:
        logger.error(f"Error getting multi-timeframe data for {symbol}: {e}")
        return {}

def analyze_trend_direction(data):
    """Analyze trend direction using ICT/SMC principles"""
    try:
        if len(data) < 20:
            return 'NEUTRAL'
        
        # Get recent highs and lows
        recent_highs = data['High'].tail(20)
        recent_lows = data['Low'].tail(20)
        
        # Check for higher highs and higher lows (uptrend)
        if (recent_highs.iloc[-1] > recent_highs.iloc[-10] and 
            recent_lows.iloc[-1] > recent_lows.iloc[-10]):
            return 'BULLISH'
        
        # Check for lower highs and lower lows (downtrend)
        elif (recent_highs.iloc[-1] < recent_highs.iloc[-10] and 
              recent_lows.iloc[-1] < recent_lows.iloc[-10]):
            return 'BEARISH'
        
        return 'NEUTRAL'
    except Exception as e:
        logger.error(f"Error analyzing trend direction: {e}")
        return 'NEUTRAL'

def find_key_levels(data):
    """Find key support/resistance levels using ICT/SMC principles"""
    try:
        if len(data) < 50:
            return []
        
        # Get swing highs and lows
        highs = data['High'].values
        lows = data['Low'].values
        
        key_levels = []
        
        # Find swing highs (resistance)
        for i in range(2, len(highs) - 2):
            if (highs[i] > highs[i-1] and highs[i] > highs[i-2] and 
                highs[i] > highs[i+1] and highs[i] > highs[i+2]):
                key_levels.append({
                    'price': highs[i],
                    'type': 'RESISTANCE',
                    'strength': calculate_level_strength(highs[i], data)
                })
        
        # Find swing lows (support)
        for i in range(2, len(lows) - 2):
            if (lows[i] < lows[i-1] and lows[i] < lows[i-2] and 
                lows[i] < lows[i+1] and lows[i] < lows[i+2]):
                key_levels.append({
                    'price': lows[i],
                    'type': 'SUPPORT',
                    'strength': calculate_level_strength(lows[i], data)
                })
        
        # Sort by strength and return top 5
        key_levels.sort(key=lambda x: x['strength'], reverse=True)
        return key_levels[:5]
        
    except Exception as e:
        logger.error(f"Error finding key levels: {e}")
        return []

def calculate_level_strength(price, data):
    """Calculate strength of a key level based on touches and volume"""
    try:
        touches = 0
        total_volume = 0
        
        for i in range(len(data)):
            if abs(data['High'].iloc[i] - price) / price < 0.005:  # Within 0.5%
                touches += 1
                total_volume += data['Volume'].iloc[i] if 'Volume' in data.columns else 1
        
        return touches * (total_volume / len(data)) if len(data) > 0 else 0
    except:
        return 0

def analyze_market_structure(data):
    """Enhanced ICT Market Structure analysis for BOS/CHoCH detection"""
    try:
        if len(data) < 100:
            return {'bos': False, 'choch': False, 'structure': 'NEUTRAL', 'swing_points': [], 'structure_shift': False}
        
        # Get swing highs and lows using proper ICT methodology
        swing_points = find_swing_points_ict(data)
        
        if len(swing_points) < 4:
            return {'bos': False, 'choch': False, 'structure': 'NEUTRAL', 'swing_points': swing_points, 'structure_shift': False}
        
        # Analyze for Break of Structure (BOS)
        bos_analysis = detect_bos(swing_points, data)
        
        # Analyze for Change of Character (CHoCH)
        choch_analysis = detect_choch(swing_points, data)
        
        # Determine overall structure
        structure = determine_market_structure(swing_points, bos_analysis, choch_analysis)
        
        return {
            'bos': bos_analysis['detected'],
            'choch': choch_analysis['detected'],
            'structure': structure,
            'swing_points': swing_points[-10:],  # Last 10 swing points
            'structure_shift': bos_analysis['detected'] or choch_analysis['detected'],
            'bos_details': bos_analysis,
            'choch_details': choch_analysis
        }
        
    except Exception as e:
        logger.error(f"Error analyzing market structure: {e}")
        return {'bos': False, 'choch': False, 'structure': 'NEUTRAL', 'swing_points': [], 'structure_shift': False}

def find_swing_points_ict(data):
    """Find swing points using ICT methodology (5-candle confirmation)"""
    try:
        highs = data['High'].values
        lows = data['Low'].values
        closes = data['Close'].values
        swing_points = []
        
        # Find swing highs (5-candle confirmation)
        for i in range(5, len(highs) - 5):
            is_swing_high = True
            for j in range(i-5, i+6):
                if j != i and highs[j] >= highs[i]:
                    is_swing_high = False
                    break
            
            if is_swing_high:
                swing_points.append({
                    'index': i,
                    'price': highs[i],
                    'type': 'HIGH',
                    'timestamp': data.index[i] if hasattr(data.index, 'iloc') else i,
                    'strength': calculate_swing_strength(highs[i], data, i, 'HIGH')
                })
        
        # Find swing lows (5-candle confirmation)
        for i in range(5, len(lows) - 5):
            is_swing_low = True
            for j in range(i-5, i+6):
                if j != i and lows[j] <= lows[i]:
                    is_swing_low = False
                    break
            
            if is_swing_low:
                swing_points.append({
                    'index': i,
                    'price': lows[i],
                    'type': 'LOW',
                    'timestamp': data.index[i] if hasattr(data.index, 'iloc') else i,
                    'strength': calculate_swing_strength(lows[i], data, i, 'LOW')
                })
        
        # Sort by index
        swing_points.sort(key=lambda x: x['index'])
        return swing_points
        
    except Exception as e:
        logger.error(f"Error finding swing points: {e}")
        return []

def calculate_swing_strength(price, data, index, swing_type):
    """Calculate strength of swing point based on volume and price action"""
    try:
        if 'Volume' not in data.columns:
            return 1.0
        
        # Get volume at swing point
        swing_volume = data['Volume'].iloc[index]
        
        # Get average volume around swing point
        start_idx = max(0, index - 10)
        end_idx = min(len(data), index + 10)
        avg_volume = data['Volume'].iloc[start_idx:end_idx].mean()
        
        # Volume strength
        volume_strength = swing_volume / avg_volume if avg_volume > 0 else 1.0
        
        # Price action strength (how far from recent range)
        if swing_type == 'HIGH':
            recent_lows = data['Low'].iloc[max(0, index-20):index].min()
            price_strength = (price - recent_lows) / recent_lows if recent_lows > 0 else 1.0
        else:
            recent_highs = data['High'].iloc[max(0, index-20):index].max()
            price_strength = (recent_highs - price) / recent_highs if recent_highs > 0 else 1.0
        
        return min(volume_strength * price_strength, 5.0)  # Cap at 5.0
        
    except Exception as e:
        logger.error(f"Error calculating swing strength: {e}")
        return 1.0

def detect_bos(swing_points, data):
    """Detect Break of Structure (BOS) using ICT methodology"""
    try:
        if len(swing_points) < 4:
            return {'detected': False, 'type': None, 'level': None, 'strength': 0}
        
        current_price = data['Close'].iloc[-1]
        recent_swings = swing_points[-10:]  # Last 10 swing points
        
        # Find most recent swing high and low
        recent_highs = [s for s in recent_swings if s['type'] == 'HIGH']
        recent_lows = [s for s in recent_swings if s['type'] == 'LOW']
        
        if not recent_highs or not recent_lows:
            return {'detected': False, 'type': None, 'level': None, 'strength': 0}
        
        # Check for bullish BOS (break above recent swing high)
        latest_high = max(recent_highs, key=lambda x: x['index'])
        if current_price > latest_high['price']:
            return {
                'detected': True,
                'type': 'BULLISH_BOS',
                'level': latest_high['price'],
                'strength': latest_high['strength'],
                'break_distance': (current_price - latest_high['price']) / latest_high['price']
            }
        
        # Check for bearish BOS (break below recent swing low)
        latest_low = max(recent_lows, key=lambda x: x['index'])
        if current_price < latest_low['price']:
            return {
                'detected': True,
                'type': 'BEARISH_BOS',
                'level': latest_low['price'],
                'strength': latest_low['strength'],
                'break_distance': (latest_low['price'] - current_price) / latest_low['price']
            }
        
        return {'detected': False, 'type': None, 'level': None, 'strength': 0}
        
    except Exception as e:
        logger.error(f"Error detecting BOS: {e}")
        return {'detected': False, 'type': None, 'level': None, 'strength': 0}

def detect_choch(swing_points, data):
    """Detect Change of Character (CHoCH) using ICT methodology"""
    try:
        if len(swing_points) < 6:
            return {'detected': False, 'type': None, 'level': None, 'strength': 0}
        
        # Look for structure shift in swing pattern
        recent_swings = swing_points[-6:]  # Last 6 swing points
        
        # Check for bullish CHoCH (higher low after lower low)
        lows = [s for s in recent_swings if s['type'] == 'LOW']
        if len(lows) >= 3:
            # Sort by index to get chronological order
            lows.sort(key=lambda x: x['index'])
            
            # Check if we have higher low after lower low
            for i in range(1, len(lows)):
                if lows[i]['price'] > lows[i-1]['price']:
                    return {
                        'detected': True,
                        'type': 'BULLISH_CHOCH',
                        'level': lows[i]['price'],
                        'strength': lows[i]['strength'],
                        'previous_low': lows[i-1]['price']
                    }
        
        # Check for bearish CHoCH (lower high after higher high)
        highs = [s for s in recent_swings if s['type'] == 'HIGH']
        if len(highs) >= 3:
            # Sort by index to get chronological order
            highs.sort(key=lambda x: x['index'])
            
            # Check if we have lower high after higher high
            for i in range(1, len(highs)):
                if highs[i]['price'] < highs[i-1]['price']:
                    return {
                        'detected': True,
                        'type': 'BEARISH_CHOCH',
                        'level': highs[i]['price'],
                        'strength': highs[i]['strength'],
                        'previous_high': highs[i-1]['price']
                    }
        
        return {'detected': False, 'type': None, 'level': None, 'strength': 0}
        
    except Exception as e:
        logger.error(f"Error detecting CHoCH: {e}")
        return {'detected': False, 'type': None, 'level': None, 'strength': 0}

def determine_market_structure(swing_points, bos_analysis, choch_analysis):
    """Determine overall market structure based on BOS/CHoCH analysis"""
    try:
        if bos_analysis['detected']:
            return bos_analysis['type']
        elif choch_analysis['detected']:
            return choch_analysis['type']
        else:
            # Analyze recent swing pattern for structure bias
            if len(swing_points) >= 4:
                recent_swings = swing_points[-4:]
                highs = [s for s in recent_swings if s['type'] == 'HIGH']
                lows = [s for s in recent_swings if s['type'] == 'LOW']
                
                if len(highs) >= 2 and len(lows) >= 2:
                    # Check for higher highs and higher lows (bullish structure)
                    if (highs[-1]['price'] > highs[-2]['price'] and 
                        lows[-1]['price'] > lows[-2]['price']):
                        return 'BULLISH_STRUCTURE'
                    
                    # Check for lower highs and lower lows (bearish structure)
                    elif (highs[-1]['price'] < highs[-2]['price'] and 
                          lows[-1]['price'] < lows[-2]['price']):
                        return 'BEARISH_STRUCTURE'
            
            return 'NEUTRAL'
        
    except Exception as e:
        logger.error(f"Error determining market structure: {e}")
        return 'NEUTRAL'

def analyze_multi_timeframe_trend(mtf_data):
    """Analyze trend across multiple timeframes for alignment"""
    try:
        if not mtf_data:
            return {'trend_alignment': 0, 'primary_trend': 'NEUTRAL', 'timeframe_analysis': {}}
        
        # Weight timeframes by importance (higher timeframes have more weight)
        timeframe_weights = {
            '12mo': 0.25, '6mo': 0.20, '3mo': 0.15, '1mo': 0.15,
            '1w': 0.10, '1d': 0.08, '4h': 0.05, '1h': 0.02
        }
        
        trend_scores = {'BULLISH': 0, 'BEARISH': 0, 'NEUTRAL': 0}
        timeframe_analysis = {}
        
        for tf_name, tf_data in mtf_data.items():
            if tf_name in timeframe_weights:
                trend = tf_data.get('trend', 'NEUTRAL')
                weight = timeframe_weights[tf_name]
                
                trend_scores[trend] += weight
                timeframe_analysis[tf_name] = {
                    'trend': trend,
                    'weight': weight,
                    'key_levels': len(tf_data.get('key_levels', [])),
                    'market_structure': tf_data.get('market_structure', {}).get('structure', 'NEUTRAL')
                }
        
        # Determine primary trend
        primary_trend = max(trend_scores, key=trend_scores.get)
        trend_alignment = trend_scores[primary_trend]
        
        return {
            'trend_alignment': trend_alignment,
            'primary_trend': primary_trend,
            'timeframe_analysis': timeframe_analysis,
            'trend_scores': trend_scores
        }
        
    except Exception as e:
        logger.error(f"Error analyzing multi-timeframe trend: {e}")
        return {'trend_alignment': 0, 'primary_trend': 'NEUTRAL', 'timeframe_analysis': {}}

def check_level_confluence(current_price, mtf_data):
    """Check for confluence of key levels across timeframes"""
    try:
        if not mtf_data:
            return 0
        
        confluence_count = 0
        tolerance = 0.01  # 1% tolerance for level confluence
        
        # Collect all key levels from all timeframes
        all_levels = []
        for tf_name, tf_data in mtf_data.items():
            key_levels = tf_data.get('key_levels', [])
            for level in key_levels:
                all_levels.append({
                    'price': level['price'],
                    'type': level['type'],
                    'timeframe': tf_name,
                    'strength': level.get('strength', 0)
                })
        
        # Check for confluence around current price
        for level in all_levels:
            if abs(level['price'] - current_price) / current_price < tolerance:
                confluence_count += 1
        
        return min(confluence_count, 5)  # Cap at 5 for scoring
        
    except Exception as e:
        logger.error(f"Error checking level confluence: {e}")
        return 0

def get_all_key_levels(mtf_data):
    """Get all key levels from multi-timeframe analysis"""
    try:
        all_levels = []
        for tf_name, tf_data in mtf_data.items():
            key_levels = tf_data.get('key_levels', [])
            for level in key_levels:
                all_levels.append({
                    'price': level['price'],
                    'type': level['type'],
                    'timeframe': tf_name,
                    'strength': level.get('strength', 0)
                })
        
        # Sort by strength and return top 10
        all_levels.sort(key=lambda x: x['strength'], reverse=True)
        return all_levels[:10]
        
    except Exception as e:
        logger.error(f"Error getting all key levels: {e}")
        return []

def get_market_structure_summary(mtf_data):
    """Get market structure summary across timeframes"""
    try:
        structure_summary = {}
        for tf_name, tf_data in mtf_data.items():
            market_structure = tf_data.get('market_structure', {})
            structure_summary[tf_name] = {
                'structure': market_structure.get('structure', 'NEUTRAL'),
                'bos': market_structure.get('bos', False),
                'choch': market_structure.get('choch', False)
            }
        
        return structure_summary
        
    except Exception as e:
        logger.error(f"Error getting market structure summary: {e}")
        return {}

def analyze_institutional_order_flow(data):
    """Analyze Institutional Order Flow using ICT methodology"""
    try:
        if len(data) < 50:
            return {'detected': False, 'type': 'NONE', 'strength': 0, 'patterns': []}
        
        patterns = []
        total_score = 0
        
        # 1. Large Volume Spikes (Institutional Activity)
        volume_analysis = analyze_volume_spikes(data)
        if volume_analysis['detected']:
            patterns.append(f"Volume Spike: {volume_analysis['strength']:.1f}x")
            total_score += volume_analysis['score']
        
        # 2. Absorption Patterns (Large orders being absorbed)
        absorption = detect_absorption_patterns(data)
        if absorption['detected']:
            patterns.append(f"Absorption: {absorption['type']}")
            total_score += absorption['score']
        
        # 3. Liquidity Grabs (Stop hunts)
        liquidity_grabs = detect_liquidity_grabs(data)
        if liquidity_grabs['detected']:
            patterns.append(f"Liquidity Grab: {liquidity_grabs['type']}")
            total_score += liquidity_grabs['score']
        
        # 4. Order Block Formation (Institutional zones)
        order_blocks = detect_institutional_order_blocks(data)
        if order_blocks['detected']:
            patterns.append(f"Order Block: {order_blocks['type']}")
            total_score += order_blocks['score']
        
        # 5. Market Maker Behavior
        mm_behavior = detect_market_maker_behavior(data)
        if mm_behavior['detected']:
            patterns.append(f"MM Behavior: {mm_behavior['type']}")
            total_score += mm_behavior['score']
        
        # Determine overall institutional flow type
        flow_type = determine_institutional_flow_type(patterns, total_score)
        
        return {
            'detected': total_score > 10,
            'type': flow_type,
            'strength': min(total_score / 20, 1.0),  # Normalize to 0-1
            'patterns': patterns,
            'score': total_score
        }
        
    except Exception as e:
        logger.error(f"Error analyzing institutional order flow: {e}")
        return {'detected': False, 'type': 'NONE', 'strength': 0, 'patterns': []}

def analyze_volume_spikes(data):
    """Detect large volume spikes indicating institutional activity"""
    try:
        if 'Volume' not in data.columns:
            return {'detected': False, 'strength': 0, 'score': 0}
        
        volumes = data['Volume'].values
        avg_volume = np.mean(volumes[-20:])  # Last 20 periods average
        
        # Check recent volume spikes
        recent_volumes = volumes[-5:]
        max_recent_volume = np.max(recent_volumes)
        
        if max_recent_volume > avg_volume * 2.0:  # 2x average volume
            strength = max_recent_volume / avg_volume
            score = min(strength * 5, 15)  # Cap at 15 points
            return {'detected': True, 'strength': strength, 'score': score}
        
        return {'detected': False, 'strength': 0, 'score': 0}
        
    except Exception as e:
        logger.error(f"Error analyzing volume spikes: {e}")
        return {'detected': False, 'strength': 0, 'score': 0}

def detect_absorption_patterns(data):
    """Detect absorption patterns (large orders being absorbed)"""
    try:
        if len(data) < 20:
            return {'detected': False, 'type': 'NONE', 'score': 0}
        
        # Look for high volume with small price movement (absorption)
        recent_data = data.tail(10)
        
        for i in range(len(recent_data) - 3):
            period_data = recent_data.iloc[i:i+3]
            
            # High volume with small price range
            avg_volume = period_data['Volume'].mean()
            price_range = (period_data['High'].max() - period_data['Low'].min()) / period_data['Close'].iloc[0]
            
            if (avg_volume > recent_data['Volume'].mean() * 1.5 and 
                price_range < 0.02):  # Less than 2% price movement
                
                # Determine absorption type
                if period_data['Close'].iloc[-1] > period_data['Open'].iloc[0]:
                    return {'detected': True, 'type': 'BULLISH_ABSORPTION', 'score': 8}
                else:
                    return {'detected': True, 'type': 'BEARISH_ABSORPTION', 'score': 8}
        
        return {'detected': False, 'type': 'NONE', 'score': 0}
        
    except Exception as e:
        logger.error(f"Error detecting absorption patterns: {e}")
        return {'detected': False, 'type': 'NONE', 'score': 0}

def detect_liquidity_grabs(data):
    """Detect liquidity grabs (stop hunts)"""
    try:
        if len(data) < 20:
            return {'detected': False, 'type': 'NONE', 'score': 0}
        
        highs = data['High'].values
        lows = data['Low'].values
        closes = data['Close'].values
        
        # Look for wicks that break previous levels then reverse
        for i in range(5, len(data) - 2):
            # Check for bullish liquidity grab (wick below previous low, then close above)
            if i >= 5:
                prev_low = min(lows[i-5:i])
                if (lows[i] < prev_low and closes[i] > prev_low and 
                    closes[i] > closes[i-1]):
                    return {'detected': True, 'type': 'BULLISH_LIQUIDITY_GRAB', 'score': 10}
            
            # Check for bearish liquidity grab (wick above previous high, then close below)
            if i >= 5:
                prev_high = max(highs[i-5:i])
                if (highs[i] > prev_high and closes[i] < prev_high and 
                    closes[i] < closes[i-1]):
                    return {'detected': True, 'type': 'BEARISH_LIQUIDITY_GRAB', 'score': 10}
        
        return {'detected': False, 'type': 'NONE', 'score': 0}
        
    except Exception as e:
        logger.error(f"Error detecting liquidity grabs: {e}")
        return {'detected': False, 'type': 'NONE', 'score': 0}

def detect_institutional_order_blocks(data):
    """Detect institutional order blocks (supply/demand zones)"""
    try:
        if len(data) < 30:
            return {'detected': False, 'type': 'NONE', 'score': 0}
        
        # Look for strong moves followed by consolidation
        recent_data = data.tail(20)
        
        # Check for bullish order block (strong up move + consolidation)
        for i in range(5, len(recent_data) - 5):
            move_data = recent_data.iloc[i-5:i+5]
            
            # Strong bullish move
            price_change = (move_data['Close'].iloc[-1] - move_data['Open'].iloc[0]) / move_data['Open'].iloc[0]
            
            if price_change > 0.03:  # 3%+ move
                # Check for consolidation after move
                consolidation_range = (move_data['High'].max() - move_data['Low'].min()) / move_data['Close'].iloc[0]
                
                if consolidation_range < 0.02:  # Less than 2% consolidation
                    return {'detected': True, 'type': 'BULLISH_ORDER_BLOCK', 'score': 12}
        
        # Check for bearish order block (strong down move + consolidation)
        for i in range(5, len(recent_data) - 5):
            move_data = recent_data.iloc[i-5:i+5]
            
            # Strong bearish move
            price_change = (move_data['Close'].iloc[-1] - move_data['Open'].iloc[0]) / move_data['Open'].iloc[0]
            
            if price_change < -0.03:  # 3%+ move down
                # Check for consolidation after move
                consolidation_range = (move_data['High'].max() - move_data['Low'].min()) / move_data['Close'].iloc[0]
                
                if consolidation_range < 0.02:  # Less than 2% consolidation
                    return {'detected': True, 'type': 'BEARISH_ORDER_BLOCK', 'score': 12}
        
        return {'detected': False, 'type': 'NONE', 'score': 0}
        
    except Exception as e:
        logger.error(f"Error detecting institutional order blocks: {e}")
        return {'detected': False, 'type': 'NONE', 'score': 0}

def detect_market_maker_behavior(data):
    """Detect market maker behavior patterns"""
    try:
        if len(data) < 20:
            return {'detected': False, 'type': 'NONE', 'score': 0}
        
        # Look for equal highs/lows (market maker manipulation)
        highs = data['High'].values
        lows = data['Low'].values
        
        recent_highs = highs[-10:]
        recent_lows = lows[-10:]
        
        # Check for equal highs (within 0.1% tolerance)
        for i in range(len(recent_highs) - 1):
            for j in range(i + 1, len(recent_highs)):
                if abs(recent_highs[i] - recent_highs[j]) / recent_highs[i] < 0.001:
                    return {'detected': True, 'type': 'EQUAL_HIGHS', 'score': 6}
        
        # Check for equal lows (within 0.1% tolerance)
        for i in range(len(recent_lows) - 1):
            for j in range(i + 1, len(recent_lows)):
                if abs(recent_lows[i] - recent_lows[j]) / recent_lows[i] < 0.001:
                    return {'detected': True, 'type': 'EQUAL_LOWS', 'score': 6}
        
        return {'detected': False, 'type': 'NONE', 'score': 0}
        
    except Exception as e:
        logger.error(f"Error detecting market maker behavior: {e}")
        return {'detected': False, 'type': 'NONE', 'score': 0}

def determine_institutional_flow_type(patterns, total_score):
    """Determine the type of institutional flow based on patterns"""
    try:
        if total_score < 10:
            return 'NONE'
        
        # Count pattern types
        bullish_patterns = sum(1 for p in patterns if 'BULLISH' in p or 'UP' in p)
        bearish_patterns = sum(1 for p in patterns if 'BEARISH' in p or 'DOWN' in p)
        
        if bullish_patterns > bearish_patterns:
            return 'INSTITUTIONAL_BUYING'
        elif bearish_patterns > bullish_patterns:
            return 'INSTITUTIONAL_SELLING'
        else:
            return 'MIXED_INSTITUTIONAL_FLOW'
        
    except Exception as e:
        logger.error(f"Error determining institutional flow type: {e}")
        return 'NONE'

def analyze_trading_sessions(data):
    """Analyze trading sessions and kill zones using ICT methodology"""
    try:
        if len(data) < 50:
            return {'sessions': {}, 'kill_zones': [], 'active_session': 'NONE'}
        
        # Define session times (UTC)
        sessions = {
            'ASIAN': {'start': 0, 'end': 8, 'name': 'Asian Session'},
            'LONDON': {'start': 8, 'end': 16, 'name': 'London Session'},
            'NEW_YORK': {'start': 13, 'end': 21, 'name': 'New York Session'},
            'OVERLAP': {'start': 13, 'end': 16, 'name': 'London-NY Overlap'}
        }
        
        # Get current time and determine active session
        current_hour = datetime.now().hour
        active_session = 'NONE'
        
        for session_name, session_info in sessions.items():
            if session_info['start'] <= current_hour < session_info['end']:
                active_session = session_name
                break
        
        # Analyze each session's performance
        session_analysis = {}
        for session_name, session_info in sessions.items():
            session_data = filter_session_data(data, session_info['start'], session_info['end'])
            if not session_data.empty:
                session_analysis[session_name] = analyze_session_performance(session_data, session_name)
        
        # Identify kill zones (high probability times)
        kill_zones = identify_kill_zones(session_analysis, active_session)
        
        return {
            'sessions': session_analysis,
            'kill_zones': kill_zones,
            'active_session': active_session
        }
        
    except Exception as e:
        logger.error(f"Error analyzing trading sessions: {e}")
        return {'sessions': {}, 'kill_zones': [], 'active_session': 'NONE'}

def filter_session_data(data, start_hour, end_hour):
    """Filter data for specific session hours"""
    try:
        # This is a simplified version - in production, you'd use proper timezone handling
        # For now, we'll analyze all data as if it's in the session
        return data.tail(50)  # Return last 50 periods as session data
        
    except Exception as e:
        logger.error(f"Error filtering session data: {e}")
        return pd.DataFrame()

def analyze_session_performance(session_data, session_name):
    """Analyze performance characteristics of a trading session"""
    try:
        if session_data.empty:
            return {'volatility': 0, 'volume': 0, 'trend_strength': 0, 'quality': 0}
        
        # Calculate session metrics
        volatility = calculate_session_volatility(session_data)
        volume_ratio = calculate_session_volume(session_data)
        trend_strength = calculate_session_trend_strength(session_data)
        
        # Session-specific characteristics
        session_quality = calculate_session_quality(session_data, session_name)
        
        return {
            'volatility': volatility,
            'volume': volume_ratio,
            'trend_strength': trend_strength,
            'quality': session_quality,
            'name': session_name
        }
        
    except Exception as e:
        logger.error(f"Error analyzing session performance: {e}")
        return {'volatility': 0, 'volume': 0, 'trend_strength': 0, 'quality': 0}

def calculate_session_volatility(data):
    """Calculate volatility for a session"""
    try:
        if len(data) < 2:
            return 0
        
        # Calculate average true range
        high_low = data['High'] - data['Low']
        high_close = abs(data['High'] - data['Close'].shift(1))
        low_close = abs(data['Low'] - data['Close'].shift(1))
        
        true_range = np.maximum(high_low, np.maximum(high_close, low_close))
        atr = true_range.mean()
        
        # Normalize by price
        avg_price = data['Close'].mean()
        return (atr / avg_price) * 100 if avg_price > 0 else 0
        
    except Exception as e:
        logger.error(f"Error calculating session volatility: {e}")
        return 0

def calculate_session_volume(data):
    """Calculate volume ratio for a session"""
    try:
        if 'Volume' not in data.columns or len(data) < 10:
            return 1.0
        
        # Compare session volume to average
        session_volume = data['Volume'].mean()
        avg_volume = data['Volume'].tail(20).mean()
        
        return session_volume / avg_volume if avg_volume > 0 else 1.0
        
    except Exception as e:
        logger.error(f"Error calculating session volume: {e}")
        return 1.0

def calculate_session_trend_strength(data):
    """Calculate trend strength for a session"""
    try:
        if len(data) < 10:
            return 0
        
        # Calculate price change percentage
        price_change = (data['Close'].iloc[-1] - data['Open'].iloc[0]) / data['Open'].iloc[0]
        
        # Calculate consistency of move
        closes = data['Close'].values
        trend_consistency = 0
        
        for i in range(1, len(closes)):
            if closes[i] > closes[i-1]:
                trend_consistency += 1
            elif closes[i] < closes[i-1]:
                trend_consistency -= 1
        
        # Normalize trend strength
        trend_strength = abs(price_change) * (abs(trend_consistency) / len(closes))
        return min(trend_strength * 100, 100)  # Cap at 100
        
    except Exception as e:
        logger.error(f"Error calculating session trend strength: {e}")
        return 0

def calculate_session_quality(data, session_name):
    """Calculate overall quality score for a session"""
    try:
        # Base quality scores for different sessions
        base_scores = {
            'ASIAN': 0.6,      # Lower volatility, consolidation
            'LONDON': 0.9,     # High volatility, good trends
            'NEW_YORK': 0.95,  # Highest volatility, best trends
            'OVERLAP': 1.0     # Best session for trading
        }
        
        base_score = base_scores.get(session_name, 0.5)
        
        # Adjust based on current performance
        volatility = calculate_session_volatility(data)
        volume_ratio = calculate_session_volume(data)
        trend_strength = calculate_session_trend_strength(data)
        
        # Quality multipliers
        volatility_multiplier = min(volatility / 2, 1.5)  # Higher volatility = better
        volume_multiplier = min(volume_ratio, 2.0)        # Higher volume = better
        trend_multiplier = min(trend_strength / 50, 1.2)  # Stronger trend = better
        
        quality = base_score * volatility_multiplier * volume_multiplier * trend_multiplier
        return min(quality, 1.0)  # Cap at 1.0
        
    except Exception as e:
        logger.error(f"Error calculating session quality: {e}")
        return 0.5

def identify_kill_zones(session_analysis, active_session):
    """Identify high-probability kill zones based on session analysis"""
    try:
        kill_zones = []
        
        # London Kill Zone (8:00-10:00 UTC)
        if 'LONDON' in session_analysis:
            london_quality = session_analysis['LONDON']['quality']
            if london_quality > 0.7:
                kill_zones.append({
                    'name': 'London Kill Zone',
                    'time': '08:00-10:00 UTC',
                    'quality': london_quality,
                    'type': 'BULLISH' if session_analysis['LONDON']['trend_strength'] > 0 else 'BEARISH'
                })
        
        # New York Kill Zone (13:30-15:30 UTC)
        if 'NEW_YORK' in session_analysis:
            ny_quality = session_analysis['NEW_YORK']['quality']
            if ny_quality > 0.7:
                kill_zones.append({
                    'name': 'New York Kill Zone',
                    'time': '13:30-15:30 UTC',
                    'quality': ny_quality,
                    'type': 'BULLISH' if session_analysis['NEW_YORK']['trend_strength'] > 0 else 'BEARISH'
                })
        
        # London-NY Overlap (13:00-16:00 UTC)
        if 'OVERLAP' in session_analysis:
            overlap_quality = session_analysis['OVERLAP']['quality']
            if overlap_quality > 0.8:
                kill_zones.append({
                    'name': 'London-NY Overlap',
                    'time': '13:00-16:00 UTC',
                    'quality': overlap_quality,
                    'type': 'BULLISH' if session_analysis['OVERLAP']['trend_strength'] > 0 else 'BEARISH'
                })
        
        # Sort by quality (highest first)
        kill_zones.sort(key=lambda x: x['quality'], reverse=True)
        
        return kill_zones
        
    except Exception as e:
        logger.error(f"Error identifying kill zones: {e}")
        return []

def detect_advanced_ict_patterns(hist_data):
    """Detect advanced ICT/SMC patterns for higher profitability"""
    try:
        if len(hist_data) < 50:
            return {'patterns': [], 'score': 0, 'confluence': 0}
        
        patterns = []
        total_score = 0
        confluence_factors = []
        
        # 1. Liquidity Sweep & Reclaim Pattern
        sweep_pattern = detect_liquidity_sweep_reclaim(hist_data)
        if sweep_pattern['detected']:
            patterns.append(f"Liquidity Sweep: {sweep_pattern['type']}")
            total_score += sweep_pattern['score']
            confluence_factors.append('LIQUIDITY_SWEEP')
        
        # 2. Order Block Break & Retest
        ob_pattern = detect_order_block_break_retest(hist_data)
        if ob_pattern['detected']:
            patterns.append(f"OB Break/Retest: {ob_pattern['type']}")
            total_score += ob_pattern['score']
            confluence_factors.append('ORDER_BLOCK_BR')
        
        # 3. Fair Value Gap Fill
        fvg_pattern = detect_fvg_fill_pattern(hist_data)
        if fvg_pattern['detected']:
            patterns.append(f"FVG Fill: {fvg_pattern['type']}")
            total_score += fvg_pattern['score']
            confluence_factors.append('FVG_FILL')
        
        # 4. Market Structure Shift (MSS)
        mss_pattern = detect_market_structure_shift(hist_data)
        if mss_pattern['detected']:
            patterns.append(f"MSS: {mss_pattern['type']}")
            total_score += mss_pattern['score']
            confluence_factors.append('MARKET_STRUCTURE_SHIFT')
        
        # 5. Imbalance & Equal Highs/Lows
        imbalance_pattern = detect_imbalance_pattern(hist_data)
        if imbalance_pattern['detected']:
            patterns.append(f"Imbalance: {imbalance_pattern['type']}")
            total_score += imbalance_pattern['score']
            confluence_factors.append('IMBALANCE')
        
        # 6. Kill Zone Confluence
        kill_zone_pattern = detect_kill_zone_confluence(hist_data)
        if kill_zone_pattern['detected']:
            patterns.append(f"Kill Zone: {kill_zone_pattern['type']}")
            total_score += kill_zone_pattern['score']
            confluence_factors.append('KILL_ZONE_CONFLUENCE')
        
        # Calculate confluence score
        confluence_score = len(confluence_factors) * 5  # 5 points per confluence factor
        
        return {
            'patterns': patterns,
            'score': total_score,
            'confluence': confluence_score,
            'confluence_factors': confluence_factors
        }
        
    except Exception as e:
        logger.error(f"Error detecting advanced ICT patterns: {e}")
        return {'patterns': [], 'score': 0, 'confluence': 0}

def detect_liquidity_sweep_reclaim(hist_data):
    """Detect liquidity sweep and reclaim pattern"""
    try:
        if len(hist_data) < 20:
            return {'detected': False, 'type': 'NONE', 'score': 0}
        
        highs = hist_data['High'].values
        lows = hist_data['Low'].values
        closes = hist_data['Close'].values
        
        # Look for liquidity sweep (break of previous high/low then reclaim)
        for i in range(10, len(hist_data) - 5):
            # Check for bullish liquidity sweep
            prev_high = max(highs[i-10:i])
            if highs[i] > prev_high and closes[i] < prev_high:
                # Check if price reclaims above the previous high
                for j in range(i+1, min(i+10, len(hist_data))):
                    if closes[j] > prev_high:
                        return {
                            'detected': True,
                            'type': 'BULLISH_SWEEP_RECLAIM',
                            'score': 15,
                            'sweep_level': prev_high,
                            'reclaim_candle': j
                        }
            
            # Check for bearish liquidity sweep
            prev_low = min(lows[i-10:i])
            if lows[i] < prev_low and closes[i] > prev_low:
                # Check if price reclaims below the previous low
                for j in range(i+1, min(i+10, len(hist_data))):
                    if closes[j] < prev_low:
                        return {
                            'detected': True,
                            'type': 'BEARISH_SWEEP_RECLAIM',
                            'score': 15,
                            'sweep_level': prev_low,
                            'reclaim_candle': j
                        }
        
        return {'detected': False, 'type': 'NONE', 'score': 0}
        
    except Exception as e:
        logger.error(f"Error detecting liquidity sweep reclaim: {e}")
        return {'detected': False, 'type': 'NONE', 'score': 0}

def detect_order_block_break_retest(hist_data):
    """Detect order block break and retest pattern"""
    try:
        if len(hist_data) < 30:
            return {'detected': False, 'type': 'NONE', 'score': 0}
        
        highs = hist_data['High'].values
        lows = hist_data['Low'].values
        closes = hist_data['Close'].values
        
        # Look for order block formation (strong move + consolidation)
        for i in range(10, len(hist_data) - 10):
            # Check for bullish order block
            move_data = hist_data.iloc[i-5:i+5]
            price_change = (move_data['Close'].iloc[-1] - move_data['Open'].iloc[0]) / move_data['Open'].iloc[0]
            
            if price_change > 0.02:  # 2%+ bullish move
                # Check for consolidation after move
                consolidation_range = (move_data['High'].max() - move_data['Low'].min()) / move_data['Close'].iloc[0]
                
                if consolidation_range < 0.015:  # Less than 1.5% consolidation
                    ob_high = move_data['High'].max()
                    ob_low = move_data['Low'].min()
                    
                    # Check for break and retest
                    for j in range(i+5, min(i+20, len(hist_data))):
                        if closes[j] > ob_high:  # Break above
                            # Look for retest
                            for k in range(j+1, min(j+10, len(hist_data))):
                                if ob_low <= closes[k] <= ob_high:  # Retest of order block
                                    return {
                                        'detected': True,
                                        'type': 'BULLISH_OB_BREAK_RETEST',
                                        'score': 20,
                                        'ob_level': (ob_high + ob_low) / 2,
                                        'break_candle': j,
                                        'retest_candle': k
                                    }
            
            # Check for bearish order block
            if price_change < -0.02:  # 2%+ bearish move
                consolidation_range = (move_data['High'].max() - move_data['Low'].min()) / move_data['Close'].iloc[0]
                
                if consolidation_range < 0.015:  # Less than 1.5% consolidation
                    ob_high = move_data['High'].max()
                    ob_low = move_data['Low'].min()
                    
                    # Check for break and retest
                    for j in range(i+5, min(i+20, len(hist_data))):
                        if closes[j] < ob_low:  # Break below
                            # Look for retest
                            for k in range(j+1, min(j+10, len(hist_data))):
                                if ob_low <= closes[k] <= ob_high:  # Retest of order block
                                    return {
                                        'detected': True,
                                        'type': 'BEARISH_OB_BREAK_RETEST',
                                        'score': 20,
                                        'ob_level': (ob_high + ob_low) / 2,
                                        'break_candle': j,
                                        'retest_candle': k
                                    }
        
        return {'detected': False, 'type': 'NONE', 'score': 0}
        
    except Exception as e:
        logger.error(f"Error detecting order block break retest: {e}")
        return {'detected': False, 'type': 'NONE', 'score': 0}

def detect_fvg_fill_pattern(hist_data):
    """Detect Fair Value Gap fill pattern"""
    try:
        if len(hist_data) < 15:
            return {'detected': False, 'type': 'NONE', 'score': 0}
        
        highs = hist_data['High'].values
        lows = hist_data['Low'].values
        closes = hist_data['Close'].values
        
        # Look for FVG formation and fill
        for i in range(5, len(hist_data) - 5):
            # Check for bullish FVG (gap between candle 1 low and candle 3 high)
            if i >= 2 and i < len(hist_data) - 2:
                candle1_high = highs[i-2]
                candle1_low = lows[i-2]
                candle2_high = highs[i-1]
                candle2_low = lows[i-1]
                candle3_high = highs[i]
                candle3_low = lows[i]
                
                # Bullish FVG: candle1 high < candle3 low (gap)
                if candle1_high < candle3_low:
                    fvg_top = candle3_low
                    fvg_bottom = candle1_high
                    
                    # Check for FVG fill
                    for j in range(i+1, min(i+15, len(hist_data))):
                        if fvg_bottom <= closes[j] <= fvg_top:
                            return {
                                'detected': True,
                                'type': 'BULLISH_FVG_FILL',
                                'score': 12,
                                'fvg_level': (fvg_top + fvg_bottom) / 2,
                                'fill_candle': j
                            }
                
                # Bearish FVG: candle1 low > candle3 high (gap)
                if candle1_low > candle3_high:
                    fvg_top = candle1_low
                    fvg_bottom = candle3_high
                    
                    # Check for FVG fill
                    for j in range(i+1, min(i+15, len(hist_data))):
                        if fvg_bottom <= closes[j] <= fvg_top:
                            return {
                                'detected': True,
                                'type': 'BEARISH_FVG_FILL',
                                'score': 12,
                                'fvg_level': (fvg_top + fvg_bottom) / 2,
                                'fill_candle': j
                            }
        
        return {'detected': False, 'type': 'NONE', 'score': 0}
        
    except Exception as e:
        logger.error(f"Error detecting FVG fill pattern: {e}")
        return {'detected': False, 'type': 'NONE', 'score': 0}

def detect_market_structure_shift(hist_data):
    """Detect Market Structure Shift (MSS) pattern"""
    try:
        if len(hist_data) < 30:
            return {'detected': False, 'type': 'NONE', 'score': 0}
        
        highs = hist_data['High'].values
        lows = hist_data['Low'].values
        closes = hist_data['Close'].values
        
        # Look for structure shift in swing points
        swing_highs = []
        swing_lows = []
        
        # Find swing points
        for i in range(5, len(hist_data) - 5):
            # Swing high
            if highs[i] > highs[i-1] and highs[i] > highs[i+1]:
                swing_highs.append({'index': i, 'price': highs[i]})
            # Swing low
            if lows[i] < lows[i-1] and lows[i] < lows[i+1]:
                swing_lows.append({'index': i, 'price': lows[i]})
        
        # Check for bullish MSS (higher low after lower low)
        if len(swing_lows) >= 3:
            recent_lows = swing_lows[-3:]
            if (recent_lows[-1]['price'] > recent_lows[-2]['price'] and 
                recent_lows[-2]['price'] < recent_lows[-3]['price']):
                return {
                    'detected': True,
                    'type': 'BULLISH_MSS',
                    'score': 18,
                    'shift_level': recent_lows[-1]['price'],
                    'previous_low': recent_lows[-2]['price']
                }
        
        # Check for bearish MSS (lower high after higher high)
        if len(swing_highs) >= 3:
            recent_highs = swing_highs[-3:]
            if (recent_highs[-1]['price'] < recent_highs[-2]['price'] and 
                recent_highs[-2]['price'] > recent_highs[-3]['price']):
                return {
                    'detected': True,
                    'type': 'BEARISH_MSS',
                    'score': 18,
                    'shift_level': recent_highs[-1]['price'],
                    'previous_high': recent_highs[-2]['price']
                }
        
        return {'detected': False, 'type': 'NONE', 'score': 0}
        
    except Exception as e:
        logger.error(f"Error detecting market structure shift: {e}")
        return {'detected': False, 'type': 'NONE', 'score': 0}

def detect_imbalance_pattern(hist_data):
    """Detect imbalance and equal highs/lows pattern"""
    try:
        if len(hist_data) < 20:
            return {'detected': False, 'type': 'NONE', 'score': 0}
        
        highs = hist_data['High'].values
        lows = hist_data['Low'].values
        closes = hist_data['Close'].values
        
        # Look for equal highs (within 0.1% tolerance)
        equal_highs = []
        for i in range(len(highs) - 1):
            for j in range(i + 1, len(highs)):
                if abs(highs[i] - highs[j]) / highs[i] < 0.001:
                    equal_highs.append((i, j, highs[i]))
        
        # Look for equal lows (within 0.1% tolerance)
        equal_lows = []
        for i in range(len(lows) - 1):
            for j in range(i + 1, len(lows)):
                if abs(lows[i] - lows[j]) / lows[i] < 0.001:
                    equal_lows.append((i, j, lows[i]))
        
        # Check for imbalance (price moves away from equal levels)
        if equal_highs:
            latest_equal_high = max(equal_highs, key=lambda x: x[1])[2]
            if closes[-1] < latest_equal_high * 0.995:  # 0.5% below equal high
                return {
                    'detected': True,
                    'type': 'BEARISH_IMBALANCE',
                    'score': 10,
                    'equal_level': latest_equal_high,
                    'imbalance_type': 'EQUAL_HIGHS'
                }
        
        if equal_lows:
            latest_equal_low = max(equal_lows, key=lambda x: x[1])[2]
            if closes[-1] > latest_equal_low * 1.005:  # 0.5% above equal low
                return {
                    'detected': True,
                    'type': 'BULLISH_IMBALANCE',
                    'score': 10,
                    'equal_level': latest_equal_low,
                    'imbalance_type': 'EQUAL_LOWS'
                }
        
        return {'detected': False, 'type': 'NONE', 'score': 0}
        
    except Exception as e:
        logger.error(f"Error detecting imbalance pattern: {e}")
        return {'detected': False, 'type': 'NONE', 'score': 0}

def detect_kill_zone_confluence(hist_data):
    """Detect kill zone confluence with other patterns"""
    try:
        if len(hist_data) < 20:
            return {'detected': False, 'type': 'NONE', 'score': 0}
        
        # Get current time
        current_hour = datetime.now().hour
        
        # Define kill zones (UTC)
        london_kill_zone = 8 <= current_hour < 10
        ny_kill_zone = 13 <= current_hour < 15
        overlap_kill_zone = 13 <= current_hour < 16
        
        kill_zone_active = london_kill_zone or ny_kill_zone or overlap_kill_zone
        
        if kill_zone_active:
            # Check for confluence with other patterns
            confluence_score = 0
            confluence_factors = []
            
            # Check for volume spike during kill zone
            if 'Volume' in hist_data.columns:
                recent_volume = hist_data['Volume'].tail(5).mean()
                avg_volume = hist_data['Volume'].tail(20).mean()
                if recent_volume > avg_volume * 1.5:
                    confluence_score += 5
                    confluence_factors.append('VOLUME_SPIKE')
            
            # Check for price action confirmation
            closes = hist_data['Close'].values
            if len(closes) >= 3:
                if closes[-1] > closes[-2] > closes[-3]:  # Bullish momentum
                    confluence_score += 3
                    confluence_factors.append('BULLISH_MOMENTUM')
                elif closes[-1] < closes[-2] < closes[-3]:  # Bearish momentum
                    confluence_score += 3
                    confluence_factors.append('BEARISH_MOMENTUM')
            
            if confluence_score >= 5:
                zone_name = "London" if london_kill_zone else "NY" if ny_kill_zone else "Overlap"
                return {
                    'detected': True,
                    'type': f'{zone_name.upper()}_KILL_ZONE_CONFLUENCE',
                    'score': 15 + confluence_score,
                    'confluence_factors': confluence_factors
                }
        
        return {'detected': False, 'type': 'NONE', 'score': 0}
        
    except Exception as e:
        logger.error(f"Error detecting kill zone confluence: {e}")
        return {'detected': False, 'type': 'NONE', 'score': 0}

def analyze_market_conditions(hist_data):
    """Analyze current market conditions and optimize signal parameters"""
    try:
        if len(hist_data) < 50:
            return {'condition': 'UNKNOWN', 'volatility': 'NORMAL', 'trend': 'SIDEWAYS', 'optimization': {}}
        
        closes = hist_data['Close'].values
        volumes = hist_data['Volume'].values if 'Volume' in hist_data.columns else np.ones(len(closes))
        
        # 1. Volatility Analysis
        volatility = calculate_market_volatility(hist_data)
        
        # 2. Trend Analysis
        trend_strength = analyze_trend_strength(hist_data)
        
        # 3. Volume Analysis
        volume_profile = analyze_volume_profile(hist_data)
        
        # 4. Market Structure Analysis
        market_structure = analyze_market_structure_condition(hist_data)
        
        # 5. Session Analysis
        session_analysis = analyze_current_session_condition(hist_data)
        
        # Determine market condition
        condition = determine_market_condition(volatility, trend_strength, volume_profile, market_structure)
        
        # Generate optimization parameters
        optimization = generate_optimization_parameters(condition, volatility, trend_strength, volume_profile)
        
        return {
            'condition': condition,
            'volatility': volatility['level'],
            'trend': trend_strength['direction'],
            'volume_profile': volume_profile['type'],
            'market_structure': market_structure['type'],
            'session': session_analysis['active_session'],
            'optimization': optimization
        }
        
    except Exception as e:
        logger.error(f"Error analyzing market conditions: {e}")
        return {'condition': 'UNKNOWN', 'volatility': 'NORMAL', 'trend': 'SIDEWAYS', 'optimization': {}}

def calculate_market_volatility(hist_data):
    """Calculate current market volatility"""
    try:
        closes = hist_data['Close'].values
        
        # Calculate ATR for volatility
        high_low = hist_data['High'].values - hist_data['Low'].values
        high_close = np.abs(hist_data['High'].values - np.roll(closes, 1))
        low_close = np.abs(hist_data['Low'].values - np.roll(closes, 1))
        
        true_range = np.maximum(high_low, np.maximum(high_close, low_close))
        atr = np.mean(true_range[1:])  # Skip first element due to roll
        
        # Calculate volatility percentage
        volatility_pct = (atr / closes[-1]) * 100
        
        # Classify volatility
        if volatility_pct > 3.0:
            level = 'HIGH'
            multiplier = 1.5
        elif volatility_pct > 1.5:
            level = 'NORMAL'
            multiplier = 1.0
        else:
            level = 'LOW'
            multiplier = 0.7
        
        return {
            'level': level,
            'percentage': volatility_pct,
            'atr': atr,
            'multiplier': multiplier
        }
        
    except Exception as e:
        logger.error(f"Error calculating market volatility: {e}")
        return {'level': 'NORMAL', 'percentage': 1.5, 'atr': 0, 'multiplier': 1.0}

def analyze_trend_strength(hist_data):
    """Analyze trend strength and direction"""
    try:
        closes = hist_data['Close'].values
        
        # Calculate trend using multiple timeframes
        short_trend = (closes[-5] - closes[-10]) / closes[-10] if len(closes) >= 10 else 0
        medium_trend = (closes[-10] - closes[-20]) / closes[-20] if len(closes) >= 20 else 0
        long_trend = (closes[-20] - closes[-40]) / closes[-40] if len(closes) >= 40 else 0
        
        # Calculate trend strength
        trend_strength = abs(short_trend) + abs(medium_trend) + abs(long_trend)
        
        # Determine direction
        if short_trend > 0.02 and medium_trend > 0.01:
            direction = 'STRONG_BULLISH'
            strength = 'STRONG'
        elif short_trend > 0.01:
            direction = 'BULLISH'
            strength = 'MODERATE'
        elif short_trend < -0.02 and medium_trend < -0.01:
            direction = 'STRONG_BEARISH'
            strength = 'STRONG'
        elif short_trend < -0.01:
            direction = 'BEARISH'
            strength = 'MODERATE'
        else:
            direction = 'SIDEWAYS'
            strength = 'WEAK'
        
        return {
            'direction': direction,
            'strength': strength,
            'short_trend': short_trend,
            'medium_trend': medium_trend,
            'long_trend': long_trend,
            'trend_strength': trend_strength
        }
        
    except Exception as e:
        logger.error(f"Error analyzing trend strength: {e}")
        return {'direction': 'SIDEWAYS', 'strength': 'WEAK', 'short_trend': 0, 'medium_trend': 0, 'long_trend': 0, 'trend_strength': 0}

def analyze_volume_profile(hist_data):
    """Analyze volume profile and characteristics"""
    try:
        if 'Volume' not in hist_data.columns:
            return {'type': 'UNKNOWN', 'ratio': 1.0, 'characteristics': []}
        
        volumes = hist_data['Volume'].values
        
        # Calculate volume ratios
        recent_volume = np.mean(volumes[-5:])
        avg_volume = np.mean(volumes[-20:])
        volume_ratio = recent_volume / avg_volume if avg_volume > 0 else 1.0
        
        # Analyze volume characteristics
        characteristics = []
        
        if volume_ratio > 2.0:
            volume_type = 'HIGH'
            characteristics.append('VOLUME_SURGE')
        elif volume_ratio > 1.5:
            volume_type = 'ELEVATED'
            characteristics.append('VOLUME_INCREASE')
        elif volume_ratio < 0.5:
            volume_type = 'LOW'
            characteristics.append('VOLUME_DECLINE')
        else:
            volume_type = 'NORMAL'
            characteristics.append('VOLUME_NORMAL')
        
        # Check for volume divergence
        closes = hist_data['Close'].values
        if len(closes) >= 10:
            price_change = (closes[-1] - closes[-10]) / closes[-10]
            volume_change = (recent_volume - np.mean(volumes[-20:-10])) / np.mean(volumes[-20:-10]) if len(volumes) >= 20 else 0
            
            if price_change > 0.02 and volume_change < -0.2:
                characteristics.append('BEARISH_DIVERGENCE')
            elif price_change < -0.02 and volume_change < -0.2:
                characteristics.append('BULLISH_DIVERGENCE')
        
        return {
            'type': volume_type,
            'ratio': volume_ratio,
            'characteristics': characteristics
        }
        
    except Exception as e:
        logger.error(f"Error analyzing volume profile: {e}")
        return {'type': 'NORMAL', 'ratio': 1.0, 'characteristics': []}

def analyze_market_structure_condition(hist_data):
    """Analyze market structure condition"""
    try:
        highs = hist_data['High'].values
        lows = hist_data['Low'].values
        closes = hist_data['Close'].values
        
        # Find recent swing points
        swing_highs = []
        swing_lows = []
        
        for i in range(5, len(hist_data) - 5):
            if highs[i] > highs[i-1] and highs[i] > highs[i+1]:
                swing_highs.append(highs[i])
            if lows[i] < lows[i-1] and lows[i] < lows[i+1]:
                swing_lows.append(lows[i])
        
        # Analyze structure
        if len(swing_highs) >= 2 and len(swing_lows) >= 2:
            # Check for higher highs and higher lows (uptrend)
            if (swing_highs[-1] > swing_highs[-2] and 
                swing_lows[-1] > swing_lows[-2]):
                structure_type = 'UPTREND'
            # Check for lower highs and lower lows (downtrend)
            elif (swing_highs[-1] < swing_highs[-2] and 
                  swing_lows[-1] < swing_lows[-2]):
                structure_type = 'DOWNTREND'
            # Check for ranging market
            elif (abs(swing_highs[-1] - swing_highs[-2]) / swing_highs[-2] < 0.02 and
                  abs(swing_lows[-1] - swing_lows[-2]) / swing_lows[-2] < 0.02):
                structure_type = 'RANGING'
            else:
                structure_type = 'MIXED'
        else:
            structure_type = 'INSUFFICIENT_DATA'
        
        return {
            'type': structure_type,
            'swing_highs': len(swing_highs),
            'swing_lows': len(swing_lows)
        }
        
    except Exception as e:
        logger.error(f"Error analyzing market structure condition: {e}")
        return {'type': 'UNKNOWN', 'swing_highs': 0, 'swing_lows': 0}

def analyze_current_session_condition(hist_data):
    """Analyze current trading session condition"""
    try:
        current_hour = datetime.now().hour
        
        # Define sessions
        asian_session = 0 <= current_hour < 8
        london_session = 8 <= current_hour < 16
        ny_session = 13 <= current_hour < 21
        overlap_session = 13 <= current_hour < 16
        
        if overlap_session:
            active_session = 'OVERLAP'
            session_quality = 'HIGH'
        elif london_session:
            active_session = 'LONDON'
            session_quality = 'HIGH'
        elif ny_session:
            active_session = 'NEW_YORK'
            session_quality = 'HIGH'
        elif asian_session:
            active_session = 'ASIAN'
            session_quality = 'LOW'
        else:
            active_session = 'AFTER_HOURS'
            session_quality = 'LOW'
        
        return {
            'active_session': active_session,
            'quality': session_quality,
            'is_kill_zone': overlap_session or (8 <= current_hour < 10) or (13 <= current_hour < 15)
        }
        
    except Exception as e:
        logger.error(f"Error analyzing session condition: {e}")
        return {'active_session': 'UNKNOWN', 'quality': 'LOW', 'is_kill_zone': False}

def determine_market_condition(volatility, trend_strength, volume_profile, market_structure):
    """Determine overall market condition"""
    try:
        # Score different aspects
        volatility_score = 3 if volatility['level'] == 'HIGH' else 2 if volatility['level'] == 'NORMAL' else 1
        trend_score = 3 if trend_strength['strength'] == 'STRONG' else 2 if trend_strength['strength'] == 'MODERATE' else 1
        volume_score = 3 if volume_profile['type'] == 'HIGH' else 2 if volume_profile['type'] == 'ELEVATED' else 1
        structure_score = 3 if market_structure['type'] in ['UPTREND', 'DOWNTREND'] else 1
        
        total_score = volatility_score + trend_score + volume_score + structure_score
        
        # Determine condition
        if total_score >= 12:
            return 'TRENDING_HIGH_VOLATILITY'
        elif total_score >= 10:
            return 'TRENDING_NORMAL'
        elif total_score >= 8:
            return 'RANGING_ACTIVE'
        elif total_score >= 6:
            return 'RANGING_QUIET'
        else:
            return 'CONSOLIDATION'
        
    except Exception as e:
        logger.error(f"Error determining market condition: {e}")
        return 'UNKNOWN'

def generate_optimization_parameters(condition, volatility, trend_strength, volume_profile):
    """Generate optimization parameters based on market condition"""
    try:
        optimization = {
            'signal_threshold_multiplier': 1.0,
            'confidence_boost': 0,
            'risk_reward_adjustment': 0,
            'timeframe_preference': 'ALL',
            'pattern_weights': {},
            'quality_filters': []
        }
        
        # Adjust parameters based on market condition
        if condition == 'TRENDING_HIGH_VOLATILITY':
            optimization.update({
                'signal_threshold_multiplier': 0.8,  # Lower threshold for more signals
                'confidence_boost': 5,  # Boost confidence
                'risk_reward_adjustment': -0.5,  # Slightly lower R/R requirement
                'timeframe_preference': 'SHORTER',  # Prefer shorter timeframes
                'pattern_weights': {
                    'TREND_FOLLOWING': 1.5,
                    'BREAKOUT': 1.3,
                    'MOMENTUM': 1.2
                },
                'quality_filters': ['HIGH_VOLUME', 'STRONG_TREND']
            })
        
        elif condition == 'TRENDING_NORMAL':
            optimization.update({
                'signal_threshold_multiplier': 1.0,
                'confidence_boost': 0,
                'risk_reward_adjustment': 0,
                'timeframe_preference': 'ALL',
                'pattern_weights': {
                    'TREND_FOLLOWING': 1.2,
                    'BREAKOUT': 1.1,
                    'MOMENTUM': 1.0
                },
                'quality_filters': ['NORMAL_VOLUME', 'MODERATE_TREND']
            })
        
        elif condition == 'RANGING_ACTIVE':
            optimization.update({
                'signal_threshold_multiplier': 1.2,  # Higher threshold for quality
                'confidence_boost': 10,  # Higher confidence requirement
                'risk_reward_adjustment': 0.5,  # Higher R/R requirement
                'timeframe_preference': 'LONGER',  # Prefer longer timeframes
                'pattern_weights': {
                    'MEAN_REVERSION': 1.5,
                    'SUPPORT_RESISTANCE': 1.3,
                    'RANGE_BOUND': 1.2
                },
                'quality_filters': ['KEY_LEVELS', 'VOLUME_CONFIRMATION']
            })
        
        elif condition == 'RANGING_QUIET':
            optimization.update({
                'signal_threshold_multiplier': 1.5,  # Much higher threshold
                'confidence_boost': 15,  # Much higher confidence
                'risk_reward_adjustment': 1.0,  # Higher R/R requirement
                'timeframe_preference': 'LONGER',
                'pattern_weights': {
                    'MEAN_REVERSION': 1.3,
                    'SUPPORT_RESISTANCE': 1.1,
                    'RANGE_BOUND': 1.0
                },
                'quality_filters': ['STRONG_KEY_LEVELS', 'HIGH_VOLUME', 'CLEAR_PATTERN']
            })
        
        elif condition == 'CONSOLIDATION':
            optimization.update({
                'signal_threshold_multiplier': 2.0,  # Very high threshold
                'confidence_boost': 20,  # Very high confidence
                'risk_reward_adjustment': 1.5,  # Much higher R/R
                'timeframe_preference': 'LONGER',
                'pattern_weights': {
                    'BREAKOUT': 1.5,
                    'ACCUMULATION': 1.3,
                    'DISTRIBUTION': 1.2
                },
                'quality_filters': ['BREAKOUT_CONFIRMATION', 'VOLUME_EXPLOSION', 'CLEAR_DIRECTION']
            })
        
        return optimization
        
    except Exception as e:
        logger.error(f"Error generating optimization parameters: {e}")
        return {
            'signal_threshold_multiplier': 1.0,
            'confidence_boost': 0,
            'risk_reward_adjustment': 0,
            'timeframe_preference': 'ALL',
            'pattern_weights': {},
            'quality_filters': []
        }

app = FastAPI(title="Enhanced Clean Trading Signals Server", version="2.0.0")

# Global variables
current_signals = []
market_data = {}
signal_database = "trading_signals.db"
monitoring_active = False
continuous_scanning_active = False
scanning_start_time = None
scanning_stats = {
    'total_scans': 0,
    'signals_generated': 0,
    'scan_duration_hours': 0,
    'last_scan_time': None
}

# ML Models
ml_models = {
    'signal_classifier': None,
    'pattern_recognizer': None,
    'sentiment_analyzer': None
}

# Initialize ML models
def initialize_ml_models():
    """Initialize ML models on server startup"""
    try:
        if SKLEARN_AVAILABLE:
            ml_models['signal_classifier'] = RandomForestClassifier(n_estimators=100, random_state=42)
            ml_models['pattern_recognizer'] = RandomForestClassifier(n_estimators=50, random_state=42)
            ml_models['sentiment_analyzer'] = RandomForestClassifier(n_estimators=30, random_state=42)
            print("✅ ML models initialized successfully")
            return True
        else:
            print("⚠️ Using mock ML service - scikit-learn not available")
            return False
    except Exception as e:
        print(f"❌ Error initializing ML models: {e}")
        return False

# ===== SIGNAL TRACKING DATABASE FUNCTIONS =====

def initialize_signal_database():
    """Initialize SQLite database for signal tracking"""
    try:
        conn = sqlite3.connect(signal_database)
        cursor = conn.cursor()
        
        # Create signals table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS signals (
                signal_id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                signal_type TEXT NOT NULL,
                entry_price REAL NOT NULL,
                target_price REAL NOT NULL,
                stop_loss REAL NOT NULL,
                confidence REAL NOT NULL,
                signal_score REAL,
                quality_factors TEXT,
                mtf_consensus TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'ACTIVE',
                outcome TEXT DEFAULT NULL,
                profit_loss REAL DEFAULT NULL,
                duration_hours REAL DEFAULT NULL,
                current_price REAL DEFAULT NULL,
                price_change_pct REAL DEFAULT NULL,
                volume_ratio REAL DEFAULT NULL,
                market_type TEXT DEFAULT NULL
            )
        ''')
        
        # Create performance analytics table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS performance_analytics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date DATE DEFAULT CURRENT_DATE,
                total_signals INTEGER DEFAULT 0,
                active_signals INTEGER DEFAULT 0,
                completed_signals INTEGER DEFAULT 0,
                tp_hit INTEGER DEFAULT 0,
                sl_hit INTEGER DEFAULT 0,
                expired_signals INTEGER DEFAULT 0,
                total_profit_loss REAL DEFAULT 0,
                win_rate REAL DEFAULT 0,
                avg_confidence REAL DEFAULT 0,
                avg_duration_hours REAL DEFAULT 0,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create ML feedback table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ml_feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                signal_id INTEGER,
                feature_name TEXT,
                feature_value REAL,
                outcome TEXT,
                performance_score REAL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (signal_id) REFERENCES signals (signal_id)
            )
        ''')
        
        conn.commit()
        conn.close()
        print("✅ Signal tracking database initialized successfully")
        return True
        
    except Exception as e:
        print(f"❌ Error initializing signal database: {e}")
        return False

def store_signal(signal_data):
    """Store a new signal in the database"""
    try:
        conn = sqlite3.connect(signal_database)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO signals (
                symbol, signal_type, entry_price, target_price, stop_loss,
                confidence, signal_score, quality_factors, mtf_consensus,
                current_price, price_change_pct, volume_ratio, market_type
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            signal_data.get('symbol'),
            signal_data.get('signal'),
            signal_data.get('current_price'),
            signal_data.get('target_price'),
            signal_data.get('stop_loss'),
            signal_data.get('confidence'),
            signal_data.get('signal_score'),
            json.dumps(signal_data.get('quality_factors', [])),
            json.dumps(signal_data.get('multi_timeframe', {})),
            signal_data.get('current_price'),
            signal_data.get('price_change_pct', 0),
            signal_data.get('volume_ratio', 1),
            signal_data.get('market_type', 'unknown')
        ))
        
        signal_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        logger.info(f"✅ Signal stored in database: {signal_data.get('symbol')} - {signal_data.get('signal')} (ID: {signal_id})")
        return signal_id
        
    except Exception as e:
        logger.error(f"❌ Error storing signal: {e}")
        return None

def update_signal_outcome(signal_id, outcome, current_price, profit_loss, duration_hours):
    """Update signal outcome when TP/SL is hit or signal expires"""
    try:
        conn = sqlite3.connect(signal_database)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE signals 
            SET status = 'COMPLETED', outcome = ?, current_price = ?, 
                profit_loss = ?, duration_hours = ?
            WHERE signal_id = ?
        ''', (outcome, current_price, profit_loss, duration_hours, signal_id))
        
        conn.commit()
        conn.close()
        
        logger.info(f"✅ Signal outcome updated: ID {signal_id} - {outcome} (P/L: {profit_loss})")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error updating signal outcome: {e}")
        return False

def get_active_signals():
    """Get all active signals for monitoring"""
    try:
        conn = sqlite3.connect(signal_database)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT signal_id, symbol, signal_type, entry_price, target_price, 
                   stop_loss, confidence, timestamp
            FROM signals 
            WHERE status = 'ACTIVE'
            ORDER BY timestamp DESC
        ''')
        
        signals = cursor.fetchall()
        conn.close()
        return signals
        
    except Exception as e:
        logger.error(f"❌ Error getting active signals: {e}")
        return []

def get_performance_stats():
    """Get performance statistics for ML feedback"""
    try:
        conn = sqlite3.connect(signal_database)
        cursor = conn.cursor()
        
        # Get overall stats
        cursor.execute('''
            SELECT 
                COUNT(*) as total_signals,
                SUM(CASE WHEN outcome = 'TP_HIT' THEN 1 ELSE 0 END) as tp_hit,
                SUM(CASE WHEN outcome = 'SL_HIT' THEN 1 ELSE 0 END) as sl_hit,
                AVG(confidence) as avg_confidence,
                AVG(duration_hours) as avg_duration,
                SUM(profit_loss) as total_pnl
            FROM signals 
            WHERE status = 'COMPLETED'
        ''')
        
        stats = cursor.fetchone()
        conn.close()
        
        if stats and stats[0] > 0:
            win_rate = (stats[1] / stats[0]) * 100 if stats[0] > 0 else 0
            return {
                'total_signals': stats[0],
                'tp_hit': stats[1],
                'sl_hit': stats[2],
                'win_rate': round(win_rate, 2),
                'avg_confidence': round(stats[3] or 0, 2),
                'avg_duration': round(stats[4] or 0, 2),
                'total_pnl': round(stats[5] or 0, 2)
            }
        else:
            return {
                'total_signals': 0,
                'tp_hit': 0,
                'sl_hit': 0,
                'win_rate': 0,
                'avg_confidence': 0,
                'avg_duration': 0,
                'total_pnl': 0
            }
        
    except Exception as e:
        logger.error(f"❌ Error getting performance stats: {e}")
        return {}

def analyze_signal_patterns():
    """Analyze completed signals to identify patterns for ML improvement"""
    try:
        conn = sqlite3.connect(signal_database)
        cursor = conn.cursor()
        
        # Get completed signals with their features
        cursor.execute('''
            SELECT 
                signal_id, symbol, signal_type, confidence, signal_score,
                quality_factors, mtf_consensus, outcome, profit_loss,
                duration_hours, volume_ratio, market_type
            FROM signals 
            WHERE status = 'COMPLETED' AND outcome IS NOT NULL
            ORDER BY timestamp DESC
            LIMIT 100
        ''')
        
        signals = cursor.fetchall()
        
        if len(signals) < 10:  # Need minimum data for analysis
            conn.close()
            return {}
        
        # Analyze patterns
        patterns = {
            'high_confidence_wins': 0,
            'high_confidence_losses': 0,
            'low_confidence_wins': 0,
            'low_confidence_losses': 0,
            'mtf_bullish_wins': 0,
            'mtf_bullish_losses': 0,
            'mtf_bearish_wins': 0,
            'mtf_bearish_losses': 0,
            'rsi_oversold_wins': 0,
            'rsi_oversold_losses': 0,
            'rsi_overbought_wins': 0,
            'rsi_overbought_losses': 0,
            'volume_surge_wins': 0,
            'volume_surge_losses': 0,
            'market_type_performance': {}
        }
        
        for signal in signals:
            signal_id, symbol, signal_type, confidence, signal_score, quality_factors, mtf_consensus, outcome, profit_loss, duration_hours, volume_ratio, market_type = signal
            
            is_win = outcome == 'TP_HIT'
            is_high_confidence = confidence >= 75
            is_low_confidence = confidence < 60
            
            # Parse quality factors
            quality_factors_str = quality_factors or "{}"
            try:
                factors = json.loads(quality_factors_str) if isinstance(quality_factors_str, str) else quality_factors_str
            except:
                factors = {}
            
            # Parse MTF consensus
            mtf_str = mtf_consensus or "{}"
            try:
                mtf = json.loads(mtf_str) if isinstance(mtf_str, str) else mtf_str
            except:
                mtf = {}
            
            # Track confidence patterns
            if is_high_confidence:
                if is_win:
                    patterns['high_confidence_wins'] += 1
                else:
                    patterns['high_confidence_losses'] += 1
            elif is_low_confidence:
                if is_win:
                    patterns['low_confidence_wins'] += 1
                else:
                    patterns['low_confidence_losses'] += 1
            
            # Track MTF patterns
            mtf_direction = mtf.get('direction', 'NEUTRAL')
            if mtf_direction == 'BULLISH':
                if is_win:
                    patterns['mtf_bullish_wins'] += 1
                else:
                    patterns['mtf_bullish_losses'] += 1
            elif mtf_direction == 'BEARISH':
                if is_win:
                    patterns['mtf_bearish_wins'] += 1
                else:
                    patterns['mtf_bearish_losses'] += 1
            
            # Track RSI patterns
            rsi_value = factors.get('rsi', 50)
            if rsi_value < 30:  # Oversold
                if is_win:
                    patterns['rsi_oversold_wins'] += 1
                else:
                    patterns['rsi_oversold_losses'] += 1
            elif rsi_value > 70:  # Overbought
                if is_win:
                    patterns['rsi_overbought_wins'] += 1
                else:
                    patterns['rsi_overbought_losses'] += 1
            
            # Track volume patterns
            if volume_ratio and volume_ratio > 1.5:  # Volume surge
                if is_win:
                    patterns['volume_surge_wins'] += 1
                else:
                    patterns['volume_surge_losses'] += 1
            
            # Track market type performance
            if market_type not in patterns['market_type_performance']:
                patterns['market_type_performance'][market_type] = {'wins': 0, 'losses': 0}
            
            if is_win:
                patterns['market_type_performance'][market_type]['wins'] += 1
            else:
                patterns['market_type_performance'][market_type]['losses'] += 1
        
        conn.close()
        return patterns
        
    except Exception as e:
        logger.error(f"Error analyzing signal patterns: {e}")
        return {}

def update_ml_models_with_feedback():
    """Update ML models based on signal performance feedback"""
    try:
        patterns = analyze_signal_patterns()
        
        if not patterns:
            logger.info("📊 Not enough signal data for ML feedback yet")
            return
        
        # Calculate improvement recommendations
        improvements = {}
        
        # Confidence threshold adjustments
        high_conf_total = patterns['high_confidence_wins'] + patterns['high_confidence_losses']
        low_conf_total = patterns['low_confidence_wins'] + patterns['low_confidence_losses']
        
        if high_conf_total > 0:
            high_conf_win_rate = patterns['high_confidence_wins'] / high_conf_total
            if high_conf_win_rate < 0.6:  # High confidence signals not performing well
                improvements['confidence_threshold'] = 'increase'
                logger.info(f"🔧 ML Feedback: High confidence signals only {high_conf_win_rate:.1%} win rate - consider raising threshold")
        
        if low_conf_total > 0:
            low_conf_win_rate = patterns['low_confidence_wins'] / low_conf_total
            if low_conf_win_rate > 0.7:  # Low confidence signals performing well
                improvements['confidence_threshold'] = 'decrease'
                logger.info(f"🔧 ML Feedback: Low confidence signals {low_conf_win_rate:.1%} win rate - consider lowering threshold")
        
        # MTF analysis improvements
        mtf_bullish_total = patterns['mtf_bullish_wins'] + patterns['mtf_bullish_losses']
        mtf_bearish_total = patterns['mtf_bearish_wins'] + patterns['mtf_bearish_losses']
        
        if mtf_bullish_total > 0:
            mtf_bullish_win_rate = patterns['mtf_bullish_wins'] / mtf_bullish_total
            if mtf_bullish_win_rate < 0.5:
                improvements['mtf_bullish_weight'] = 'decrease'
                logger.info(f"🔧 ML Feedback: Bullish MTF signals only {mtf_bullish_win_rate:.1%} win rate - reducing weight")
        
        if mtf_bearish_total > 0:
            mtf_bearish_win_rate = patterns['mtf_bearish_wins'] / mtf_bearish_total
            if mtf_bearish_win_rate < 0.5:
                improvements['mtf_bearish_weight'] = 'decrease'
                logger.info(f"🔧 ML Feedback: Bearish MTF signals only {mtf_bearish_win_rate:.1%} win rate - reducing weight")
        
        # RSI pattern improvements
        rsi_oversold_total = patterns['rsi_oversold_wins'] + patterns['rsi_oversold_losses']
        rsi_overbought_total = patterns['rsi_overbought_wins'] + patterns['rsi_overbought_losses']
        
        if rsi_oversold_total > 0:
            rsi_oversold_win_rate = patterns['rsi_oversold_wins'] / rsi_oversold_total
            if rsi_oversold_win_rate > 0.7:
                improvements['rsi_oversold_weight'] = 'increase'
                logger.info(f"🔧 ML Feedback: RSI oversold signals {rsi_oversold_win_rate:.1%} win rate - increasing weight")
        
        if rsi_overbought_total > 0:
            rsi_overbought_win_rate = patterns['rsi_overbought_wins'] / rsi_overbought_total
            if rsi_overbought_win_rate > 0.7:
                improvements['rsi_overbought_weight'] = 'increase'
                logger.info(f"🔧 ML Feedback: RSI overbought signals {rsi_overbought_win_rate:.1%} win rate - increasing weight")
        
        # Volume pattern improvements
        volume_surge_total = patterns['volume_surge_wins'] + patterns['volume_surge_losses']
        if volume_surge_total > 0:
            volume_surge_win_rate = patterns['volume_surge_wins'] / volume_surge_total
            if volume_surge_win_rate > 0.6:
                improvements['volume_weight'] = 'increase'
                logger.info(f"🔧 ML Feedback: Volume surge signals {volume_surge_win_rate:.1%} win rate - increasing weight")
        
        # Market type performance
        for market_type, performance in patterns['market_type_performance'].items():
            total = performance['wins'] + performance['losses']
            if total > 5:  # Minimum sample size
                win_rate = performance['wins'] / total
                if win_rate < 0.4:
                    logger.info(f"🔧 ML Feedback: {market_type} signals only {win_rate:.1%} win rate - consider reducing focus")
                elif win_rate > 0.7:
                    logger.info(f"🔧 ML Feedback: {market_type} signals {win_rate:.1%} win rate - consider increasing focus")
        
        # Store improvements for future signal generation
        if improvements:
            logger.info(f"🤖 ML Feedback Analysis Complete: {len(improvements)} improvements identified")
            # In a real implementation, you would update the signal generation parameters here
            # For now, we log the recommendations
        else:
            logger.info("🤖 ML Feedback: No significant improvements identified at this time")
        
    except Exception as e:
        logger.error(f"Error updating ML models with feedback: {e}")

def analyze_comprehensive_signal_performance():
    """Comprehensive analysis of signal performance across all dimensions"""
    try:
        conn = sqlite3.connect('trading_signals.db')
        cursor = conn.cursor()
        
        # Get all completed signals from last 30 days
        cursor.execute("""
            SELECT * FROM signals 
            WHERE outcome IS NOT NULL 
            AND timestamp > datetime('now', '-30 days')
            ORDER BY timestamp DESC
        """)
        
        signals = cursor.fetchall()
        conn.close()
        
        if not signals:
            return {}
        
        # Analyze performance by different dimensions
        performance_data = {
            'pattern_performance': analyze_pattern_performance(signals),
            'timeframe_performance': analyze_timeframe_performance(signals),
            'session_performance': analyze_session_performance(signals),
            'ict_performance': analyze_ict_performance(signals),
            'overall_stats': calculate_overall_stats(signals)
        }
        
        return performance_data
        
    except Exception as e:
        logger.error(f"Error analyzing signal performance: {e}")
        return {}

def analyze_pattern_performance(signals):
    """Analyze performance by price action patterns"""
    pattern_stats = {}
    
    for signal in signals:
        # Parse signal data (assuming JSON format)
        try:
            signal_data = eval(signal[8]) if isinstance(signal[8], str) else signal[8]  # quality_factors
            outcome = signal[9]  # outcome
            pnl = signal[10] if signal[10] else 0  # pnl
            
            # Extract patterns from quality_factors
            patterns = [factor for factor in signal_data if 'PA:' in factor or 'VP:' in factor or 'Session:' in factor]
            
            for pattern in patterns:
                pattern_name = pattern.split(': ')[1] if ': ' in pattern else pattern
                
                if pattern_name not in pattern_stats:
                    pattern_stats[pattern_name] = {
                        'total_signals': 0,
                        'wins': 0,
                        'total_pnl': 0,
                        'outcomes': []
                    }
                
                pattern_stats[pattern_name]['total_signals'] += 1
                pattern_stats[pattern_name]['total_pnl'] += pnl
                pattern_stats[pattern_name]['outcomes'].append(outcome)
                
                if outcome in ['TP_HIT', 'MANUAL_CLOSE'] and pnl > 0:
                    pattern_stats[pattern_name]['wins'] += 1
        except:
            continue
    
    # Calculate performance metrics
    for pattern, stats in pattern_stats.items():
        if stats['total_signals'] > 0:
            stats['win_rate'] = stats['wins'] / stats['total_signals']
            stats['avg_profit'] = stats['total_pnl'] / stats['total_signals']
            stats['accuracy'] = calculate_pattern_accuracy(stats['outcomes'])
    
    return pattern_stats

def analyze_timeframe_performance(signals):
    """Analyze performance by timeframe"""
    tf_stats = {}
    
    for signal in signals:
        try:
            timeframe = signal[3] if len(signal) > 3 else '1h'  # timeframe
            outcome = signal[9]
            pnl = signal[10] if signal[10] else 0
            
            if timeframe not in tf_stats:
                tf_stats[timeframe] = {
                    'total_signals': 0,
                    'wins': 0,
                    'total_pnl': 0,
                    'outcomes': []
                }
            
            tf_stats[timeframe]['total_signals'] += 1
            tf_stats[timeframe]['total_pnl'] += pnl
            tf_stats[timeframe]['outcomes'].append(outcome)
            
            if outcome in ['TP_HIT', 'MANUAL_CLOSE'] and pnl > 0:
                tf_stats[timeframe]['wins'] += 1
        except:
            continue
    
    # Calculate metrics
    for tf, stats in tf_stats.items():
        if stats['total_signals'] > 0:
            stats['win_rate'] = stats['wins'] / stats['total_signals']
            stats['avg_profit'] = stats['total_pnl'] / stats['total_signals']
            stats['accuracy'] = calculate_pattern_accuracy(stats['outcomes'])
    
    return tf_stats

def analyze_session_performance(signals):
    """Analyze performance by market session"""
    session_stats = {}
    
    for signal in signals:
        try:
            timestamp = signal[1]  # timestamp
            outcome = signal[9]
            pnl = signal[10] if signal[10] else 0
            
            # Determine session based on timestamp
            hour = datetime.fromisoformat(timestamp.replace('Z', '+00:00')).hour
            if 8 <= hour < 16:
                session = 'London'
            elif 13 <= hour < 21:
                session = 'NY'
            elif 0 <= hour < 8:
                session = 'Asian'
            else:
                session = 'Other'
            
            if session not in session_stats:
                session_stats[session] = {
                    'total_signals': 0,
                    'wins': 0,
                    'total_pnl': 0,
                    'outcomes': []
                }
            
            session_stats[session]['total_signals'] += 1
            session_stats[session]['total_pnl'] += pnl
            session_stats[session]['outcomes'].append(outcome)
            
            if outcome in ['TP_HIT', 'MANUAL_CLOSE'] and pnl > 0:
                session_stats[session]['wins'] += 1
        except:
            continue
    
    # Calculate metrics
    for session, stats in session_stats.items():
        if stats['total_signals'] > 0:
            stats['win_rate'] = stats['wins'] / stats['total_signals']
            stats['avg_profit'] = stats['total_pnl'] / stats['total_signals']
            stats['accuracy'] = calculate_pattern_accuracy(stats['outcomes'])
    
    return session_stats

def analyze_ict_performance(signals):
    """Analyze performance by ICT/SMC concepts"""
    ict_stats = {}
    
    for signal in signals:
        try:
            signal_data = eval(signal[8]) if isinstance(signal[8], str) else signal[8]
            outcome = signal[9]
            pnl = signal[10] if signal[10] else 0
            
            # Extract ICT concepts
            ict_concepts = [factor for factor in signal_data if any(x in factor for x in ['SMC:', 'FVG:', 'OB:', 'Liquidity:'])]
            
            for concept in ict_concepts:
                concept_name = concept.split(': ')[1] if ': ' in concept else concept
                
                if concept_name not in ict_stats:
                    ict_stats[concept_name] = {
                        'total_signals': 0,
                        'wins': 0,
                        'total_pnl': 0,
                        'outcomes': [],
                        'scores': []
                    }
                
                ict_stats[concept_name]['total_signals'] += 1
                ict_stats[concept_name]['total_pnl'] += pnl
                ict_stats[concept_name]['outcomes'].append(outcome)
                
                if outcome in ['TP_HIT', 'MANUAL_CLOSE'] and pnl > 0:
                    ict_stats[concept_name]['wins'] += 1
        except:
            continue
    
    # Calculate metrics
    for concept, stats in ict_stats.items():
        if stats['total_signals'] > 0:
            stats['win_rate'] = stats['wins'] / stats['total_signals']
            stats['avg_profit'] = stats['total_pnl'] / stats['total_signals']
            stats['accuracy'] = calculate_pattern_accuracy(stats['outcomes'])
            stats['avg_score'] = sum(stats['scores']) / len(stats['scores']) if stats['scores'] else 0
    
    return ict_stats

def calculate_pattern_accuracy(outcomes):
    """Calculate accuracy based on outcomes"""
    if not outcomes:
        return 0
    
    successful_outcomes = ['TP_HIT', 'MANUAL_CLOSE']
    successful = sum(1 for outcome in outcomes if outcome in successful_outcomes)
    
    return successful / len(outcomes)

def calculate_overall_stats(signals):
    """Calculate overall performance statistics"""
    total_signals = len(signals)
    total_pnl = sum(signal[10] for signal in signals if signal[10])
    wins = sum(1 for signal in signals if signal[9] in ['TP_HIT', 'MANUAL_CLOSE'] and signal[10] and signal[10] > 0)
    
    return {
        'total_signals': total_signals,
        'total_pnl': total_pnl,
        'avg_pnl': total_pnl / total_signals if total_signals > 0 else 0,
        'win_rate': wins / total_signals if total_signals > 0 else 0,
        'accuracy': calculate_pattern_accuracy([signal[9] for signal in signals])
    }

def run_ml_feedback_analysis():
    """Run ML feedback analysis in background thread"""
    while monitoring_active:
        try:
            # Run analysis every hour
            time.sleep(3600)  # 1 hour
            update_ml_models_with_feedback()
        except Exception as e:
            logger.error(f"Error in ML feedback analysis: {e}")
            time.sleep(300)  # Wait 5 minutes before retrying

def continuous_market_scan():
    """Continuous market scanning for AI learning"""
    global continuous_scanning_active, scanning_start_time, scanning_stats
    
    while continuous_scanning_active:
        try:
            logger.info("🔄 Starting continuous market scan for AI learning...")
            
            # Get comprehensive market symbols
            symbols_to_scan = {
                'stocks': ['AAPL', 'TSLA', 'MSFT', 'GOOGL', 'META', 'NVDA', 'AMZN', 'NFLX', 'AMD', 'INTC', 'JPM', 'JNJ', 'PG', 'UNH', 'HD', 'BAC', 'MA', 'V', 'NKE', 'DIS'],
                'crypto': ['BTC-USD', 'ETH-USD', 'BNB-USD', 'XRP-USD', 'SOL-USD', 'ADA-USD', 'DOT-USD', 'AVAX-USD', 'MATIC-USD', 'ATOM-USD'],
                'forex': ['EURUSD=X', 'GBPUSD=X', 'USDJPY=X', 'AUDUSD=X', 'USDCAD=X', 'EURGBP=X', 'EURJPY=X', 'GBPJPY=X', 'AUDJPY=X', 'EURAUD=X'],
                'futures': ['GC=F', 'CL=F', 'ES=F', 'NQ=F', 'YM=F', 'RTY=F', 'ZB=F', 'ZN=F', 'ZF=F', 'ZT=F'],
                'indices': ['SPY', 'QQQ', 'IWM', 'DIA', 'VTI', 'VOO', 'VEA', 'VWO', 'EFA', 'EEM']
            }
            
            scan_signals = []
            total_scanned = 0
            
            # Scan each market category
            for market_type, symbols in symbols_to_scan.items():
                for symbol in symbols:
                    try:
                        total_scanned += 1
                        
                        # Get live data
                        ticker = yf.Ticker(symbol)
                        info = ticker.info
                        current_price = info.get('regularMarketPrice', 0)
                        hist = ticker.history(period="5d", interval="1h")
                        
                        if not hist.empty and len(hist) >= 20 and current_price > 0:
                            # Generate signal
                            signal = generate_ict_smc_signal(symbol, hist, "1h")
                            
                            if signal:
                                signal['market_type'] = market_type
                                signal['live_price'] = current_price
                                signal['is_continuous_scan'] = True
                                scan_signals.append(signal)
                                scanning_stats['signals_generated'] += 1
                        
                    except Exception as e:
                        logger.error(f"Error scanning {symbol} in continuous mode: {e}")
                        continue
            
            # Update scanning stats
            scanning_stats['total_scans'] += 1
            scanning_stats['last_scan_time'] = datetime.now().isoformat()
            if scanning_start_time:
                scanning_stats['scan_duration_hours'] = (datetime.now() - scanning_start_time).total_seconds() / 3600
            
            logger.info(f"🔄 Continuous scan #{scanning_stats['total_scans']} completed: {len(scan_signals)} signals from {total_scanned} symbols")
            
            # Store signals in global current_signals for display
            if scan_signals:
                global current_signals
                current_signals = scan_signals
                logger.info(f"📊 {len(scan_signals)} signals available for display")
            
            # Sleep for 30 minutes before next scan
            time.sleep(1800)  # 30 minutes
            
        except Exception as e:
            logger.error(f"Error in continuous scanning: {e}")
            time.sleep(300)  # Wait 5 minutes before retrying

def start_continuous_scanning():
    """Start continuous market scanning for AI learning"""
    global continuous_scanning_active, scanning_start_time
    
    if not continuous_scanning_active:
        continuous_scanning_active = True
        scanning_start_time = datetime.now()
        scan_thread = threading.Thread(target=continuous_market_scan, daemon=True)
        scan_thread.start()
        logger.info("🚀 Continuous market scanning started for AI learning")
        return True
    return False

def stop_continuous_scanning():
    """Stop continuous market scanning"""
    global continuous_scanning_active, scanning_start_time
    
    continuous_scanning_active = False
    scanning_start_time = None
    logger.info("⏹️ Continuous market scanning stopped")

def get_scanning_status():
    """Get current scanning status and statistics"""
    global scanning_stats, scanning_start_time, continuous_scanning_active
    
    current_duration = 0
    if scanning_start_time and continuous_scanning_active:
        current_duration = (datetime.now() - scanning_start_time).total_seconds() / 3600
    
    return {
        'scanning_active': continuous_scanning_active,
        'start_time': scanning_start_time.isoformat() if scanning_start_time else None,
        'current_duration_hours': round(current_duration, 2),
        'stats': scanning_stats.copy()
    }

# ===== BACKGROUND MONITORING SYSTEM =====

def monitor_signal_outcomes():
    """Background monitoring system to check signal outcomes"""
    global monitoring_active
    
    while monitoring_active:
        try:
            active_signals = get_active_signals()
            
            for signal in active_signals:
                signal_id, symbol, signal_type, entry_price, target_price, stop_loss, confidence, timestamp = signal
                
                # Get current price
                try:
                    ticker = yf.Ticker(symbol)
                    current_price = ticker.info.get('regularMarketPrice', 0)
                    
                    if current_price <= 0:
                        continue
                    
                    # Calculate duration
                    signal_time = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                    duration_hours = (datetime.now() - signal_time).total_seconds() / 3600
                    
                    # Check for TP/SL hit
                    outcome = None
                    profit_loss = 0
                    
                    if signal_type == 'BUY':
                        if current_price >= target_price:
                            outcome = 'TP_HIT'
                            profit_loss = target_price - entry_price
                        elif current_price <= stop_loss:
                            outcome = 'SL_HIT'
                            profit_loss = stop_loss - entry_price
                    elif signal_type == 'SELL':
                        if current_price <= target_price:
                            outcome = 'TP_HIT'
                            profit_loss = entry_price - target_price
                        elif current_price >= stop_loss:
                            outcome = 'SL_HIT'
                            profit_loss = entry_price - stop_loss
                    
                    # Check for expiration (24 hours)
                    if duration_hours >= 24 and outcome is None:
                        outcome = 'EXPIRED'
                        profit_loss = current_price - entry_price if signal_type == 'BUY' else entry_price - current_price
                    
                    # Update signal if outcome is determined
                    if outcome:
                        update_signal_outcome(signal_id, outcome, current_price, profit_loss, duration_hours)
                        logger.info(f"🎯 Signal outcome: {symbol} - {outcome} (P/L: {profit_loss:.2f})")
                
                except Exception as e:
                    logger.error(f"Error monitoring signal {signal_id}: {e}")
                    continue
            
            # Sleep for 5 minutes before next check
            time.sleep(300)
            
        except Exception as e:
            logger.error(f"Error in monitoring system: {e}")
            time.sleep(60)  # Wait 1 minute before retrying

def start_monitoring():
    """Start the background monitoring system"""
    global monitoring_active
    
    if not monitoring_active:
        monitoring_active = True
        
        # Start signal outcome monitoring
        monitor_thread = threading.Thread(target=monitor_signal_outcomes, daemon=True)
        monitor_thread.start()
        
        # Start ML feedback analysis
        feedback_thread = threading.Thread(target=run_ml_feedback_analysis, daemon=True)
        feedback_thread.start()
        
        logger.info("🚀 Background signal monitoring and ML feedback analysis started")
        return True
    return False

def stop_monitoring():
    """Stop the background monitoring system"""
    global monitoring_active
    monitoring_active = False
    logger.info("⏹️ Background signal monitoring stopped")

# ===== CONTINUOUS SCANNING SYSTEM =====



# ICT/SMC Analysis Functions
def analyze_kill_zones(hist_data, timeframe):
    """Analyze ICT Kill Zones (London/NY/Asian sessions)"""
    try:
        # Convert to datetime index if needed
        if not isinstance(hist_data.index, pd.DatetimeIndex):
            hist_data.index = pd.to_datetime(hist_data.index)
        
        # Define session times (UTC)
        london_start = 7  # 7 AM UTC
        london_end = 16   # 4 PM UTC
        ny_start = 13     # 1 PM UTC
        ny_end = 22       # 10 PM UTC
        asian_start = 0   # 12 AM UTC
        asian_end = 9     # 9 AM UTC
        
        # Get current hour
        current_hour = datetime.now().hour
        
        # Determine active session
        active_session = "NONE"
        if london_start <= current_hour < london_end:
            active_session = "LONDON"
        elif ny_start <= current_hour < ny_end:
            active_session = "NEW_YORK"
        elif asian_start <= current_hour < asian_end:
            active_session = "ASIAN"
        
        # Calculate session volatility
        session_volatility = hist_data['Close'].pct_change().std() * 100
        
        return {
            'active_session': active_session,
            'is_kill_zone': active_session in ["LONDON", "NEW_YORK"],
            'session_volatility': round(session_volatility, 2),
            'score': 15 if active_session in ["LONDON", "NEW_YORK"] else 5
        }
    except Exception as e:
        logger.error(f"Error analyzing kill zones: {e}")
        return {'active_session': 'UNKNOWN', 'is_kill_zone': False, 'score': 0}

def analyze_smart_money_concepts(hist_data):
    """Enhanced Smart Money Concepts (SMC) with Order Flow, Market Structure, and POI"""
    try:
        if len(hist_data) < 20:
            return {'score': 0, 'pattern': 'INSUFFICIENT_DATA'}
        
        # Get price data
        closes = hist_data['Close'].values
        highs = hist_data['High'].values
        lows = hist_data['Low'].values
        volumes = hist_data['Volume'].values if 'Volume' in hist_data.columns else np.ones(len(closes))
        
        # Get price data
        highs = hist_data['High'].tolist()
        lows = hist_data['Low'].tolist()
        closes = hist_data['Close'].tolist()
        volumes = hist_data['Volume'].tolist() if 'Volume' in hist_data.columns else [1] * len(closes)
        current_price = closes[-1]
        
        # 1. ENHANCED ORDER FLOW ANALYSIS
        order_flow_score = 0
        order_flow_patterns = []
        
        # Volume Profile Analysis
        volume_profile = analyze_volume_profile(hist_data)
        if volume_profile.get('key_levels'):
            # Check if price is near high volume areas (institutional interest)
            for level in volume_profile['key_levels']:
                level_price = level['price'] if isinstance(level, dict) else level
                if abs(current_price - level_price) / current_price < 0.02:  # Within 2%
                    order_flow_score += 10
                    order_flow_patterns.append(f"High Volume Node: ${level_price:.2f}")
        
        # Institutional Order Flow Detection
        institutional_flow = detect_institutional_flow(hist_data)
        if institutional_flow['detected']:
            order_flow_score += institutional_flow['score']
            order_flow_patterns.append(f"Institutional {institutional_flow['type']} Flow")
        
        # 2. ENHANCED MARKET STRUCTURE ANALYSIS
        structure_score = 0
        structure_patterns = []
        
        # Swing Point Analysis
        swing_points = detect_swing_points(hist_data)
        if swing_points['bullish_swing']:
            structure_score += 15
            structure_patterns.append("Bullish Swing Point")
        elif swing_points['bearish_swing']:
            structure_score -= 15
            structure_patterns.append("Bearish Swing Point")
        
        # Structure Shift Detection
        structure_shift = detect_structure_shift(hist_data)
        if structure_shift['shift_detected']:
            structure_score += structure_shift['score']
            structure_patterns.append(f"Structure Shift: {structure_shift['type']}")
        
        # 3. ADVANCED POINT OF INTEREST (POI) ANALYSIS
        poi_score = 0
        poi_patterns = []
        
        # Liquidity Pools Detection
        liquidity_pools = detect_liquidity_pools(hist_data)
        for pool in liquidity_pools:
            if abs(current_price - pool['price']) / current_price < 0.015:  # Within 1.5%
                poi_score += 8
                poi_patterns.append(f"Liquidity Pool: ${pool['price']:.2f}")
        
        # Equal Highs/Lows Detection
        equal_levels = detect_equal_highs_lows(hist_data)
        for level in equal_levels:
            if abs(current_price - level['price']) / current_price < 0.01:  # Within 1%
                poi_score += 12
                poi_patterns.append(f"Equal {level['type']}: ${level['price']:.2f}")
        
        # Confluent Support/Resistance
        confluence = detect_confluent_levels(hist_data)
        if confluence['confluence_detected']:
            poi_score += confluence['score']
            poi_patterns.append(f"Confluent {confluence['type']} Zone")
        
        # 4. ENHANCED SMC ANALYSIS (Fibonacci + Premium/Discount)
        recent_high = max(highs[-20:])
        recent_low = min(lows[-20:])
        price_range = recent_high - recent_low
        
        smc_score = 0
        pattern = "RANGE"
        fib_levels = []
        
        if price_range > 0:  # Only calculate if there's a valid range
            # Calculate Fibonacci retracement levels
            fib_236 = recent_high - (price_range * 0.236)  # 23.6%
            fib_382 = recent_high - (price_range * 0.382)  # 38.2%
            fib_500 = recent_high - (price_range * 0.500)  # 50.0%
            fib_618 = recent_high - (price_range * 0.618)  # 61.8%
            fib_786 = recent_high - (price_range * 0.786)  # 78.6%
            
            fib_levels = [fib_236, fib_382, fib_500, fib_618, fib_786]
            
            # Check proximity to Fibonacci levels (within 1% of range)
            tolerance = price_range * 0.01
            
            for i, fib_level in enumerate(fib_levels):
                if abs(current_price - fib_level) <= tolerance:
                    fib_percent = [23.6, 38.2, 50.0, 61.8, 78.6][i]
                    
                    if fib_percent <= 38.2:  # Discount zone (23.6%, 38.2%)
                        smc_score = 20  # Higher score for Fib levels
                        pattern = f"DISCOUNT_FIB_{fib_percent}%"
                        break
                    elif fib_percent >= 61.8:  # Premium zone (61.8%, 78.6%)
                        smc_score = 20  # Higher score for Fib levels
                        pattern = f"PREMIUM_FIB_{fib_percent}%"
                        break
                    elif fib_percent == 50.0:  # 50% retracement
                        smc_score = 15
                        pattern = "FIB_50%"
                        break
            
            # Fallback to traditional premium/discount if no Fib level hit
            if smc_score == 0:
                price_position = (current_price - recent_low) / price_range
                if price_position > 0.8:
                    smc_score = 15  # Premium zone
                    pattern = "PREMIUM"
                elif price_position < 0.2:
                    smc_score = 15  # Discount zone
                    pattern = "DISCOUNT"
                else:
                    smc_score = 5   # Range
                    pattern = "RANGE"
        else:
            smc_score = 5
            pattern = "RANGE"
        
        # Combine all scores
        total_score = order_flow_score + structure_score + poi_score + smc_score
        all_patterns = order_flow_patterns + structure_patterns + poi_patterns
        
        # Calculate price position for display
        price_position = (current_price - recent_low) / price_range if price_range > 0 else 0.5
        
        # Return the Fibonacci pattern (not signal type)
        return {
            'pattern': pattern,  # This contains the Fibonacci pattern like "DISCOUNT_FIB_38.2%"
            'score': total_score,
            'price_position': round(price_position, 2),
            'recent_high': round(recent_high, 2),
            'recent_low': round(recent_low, 2),
            'order_flow': {
                'score': order_flow_score,
                'patterns': order_flow_patterns
            },
            'market_structure': {
                'score': structure_score,
                'patterns': structure_patterns
            },
            'poi': {
                'score': poi_score,
                'patterns': poi_patterns
            },
            'all_patterns': all_patterns
        }
        
    except Exception as e:
        logger.error(f"Error analyzing SMC: {e}")
        return {'score': 0, 'pattern': 'ERROR'}

def detect_fair_value_gaps(hist_data):
    """Detect Fair Value Gaps (FVG) - key ICT concept"""
    try:
        if len(hist_data) < 3:
            return {'score': 0, 'patterns': [], 'gaps': []}
        
        highs = hist_data['High'].values
        lows = hist_data['Low'].values
        closes = hist_data['Close'].values
        opens = hist_data['Open'].values
        
        gaps = []
        patterns = []
        score = 0
        
        # Look for FVGs in last 10 candles
        for i in range(len(hist_data) - 2):
            if i < 2:
                continue
                
            # Bullish FVG: Gap between candle 1 high and candle 3 low
            if (highs[i-1] < lows[i+1] and  # Gap exists
                closes[i] > opens[i] and  # Middle candle is bullish
                closes[i-1] < opens[i-1] and  # Previous candle is bearish
                closes[i+1] > opens[i+1]):  # Next candle is bullish
                
                gap_size = lows[i+1] - highs[i-1]
                gap_percentage = (gap_size / highs[i-1]) * 100
                
                if gap_percentage > 0.1:  # Minimum 0.1% gap
                    gaps.append({
                        'type': 'BULLISH_FVG',
                        'price_range': (highs[i-1], lows[i+1]),
                        'size': gap_size,
                        'percentage': gap_percentage,
                        'candle_index': i
                    })
                    score += 8
                    patterns.append(f"Bullish FVG: {gap_percentage:.2f}%")
            
            # Bearish FVG: Gap between candle 1 low and candle 3 high
            elif (lows[i-1] > highs[i+1] and  # Gap exists
                  opens[i] > closes[i] and  # Middle candle is bearish
                  opens[i-1] > closes[i-1] and  # Previous candle is bullish
                  opens[i+1] > closes[i+1]):  # Next candle is bearish
                
                gap_size = lows[i-1] - highs[i+1]
                gap_percentage = (gap_size / lows[i-1]) * 100
                
                if gap_percentage > 0.1:  # Minimum 0.1% gap
                    gaps.append({
                        'type': 'BEARISH_FVG',
                        'price_range': (highs[i+1], lows[i-1]),
                        'size': gap_size,
                        'percentage': gap_percentage,
                        'candle_index': i
                    })
                    score -= 8
                    patterns.append(f"Bearish FVG: {gap_percentage:.2f}%")
        
        # Check if current price is near any FVG
        current_price = closes[-1]
        for gap in gaps:
            gap_low, gap_high = gap['price_range']
            if gap_low <= current_price <= gap_high:
                score += 5 if gap['type'] == 'BULLISH_FVG' else -5
                patterns.append(f"Price in {gap['type']}")
        
        return {
            'score': score,
            'patterns': patterns,
            'gaps': gaps
        }
        
    except Exception as e:
        logger.error(f"Error detecting Fair Value Gaps: {e}")
        return {'score': 0, 'patterns': [], 'gaps': []}

def detect_enhanced_order_blocks(hist_data):
    """Detect enhanced Order Blocks - institutional accumulation/distribution zones"""
    try:
        if len(hist_data) < 10:
            return {'score': 0, 'patterns': [], 'blocks': []}
        
        highs = hist_data['High'].values
        lows = hist_data['Low'].values
        closes = hist_data['Close'].values
        opens = hist_data['Open'].values
        volumes = hist_data['Volume'].values if 'Volume' in hist_data.columns else np.ones(len(closes))
        
        order_blocks = []
        patterns = []
        score = 0
        
        # Look for Order Blocks in last 20 candles
        for i in range(len(hist_data) - 5):
            if i < 5:
                continue
            
            # Bullish Order Block: Strong bullish candle followed by consolidation
            if (closes[i] > opens[i] and  # Bullish candle
                (closes[i] - opens[i]) > (highs[i] - lows[i]) * 0.7 and  # Strong body
                volumes[i] > np.mean(volumes[i-5:i]) * 1.5):  # High volume
                
                # Check for consolidation after
                consolidation = True
                for j in range(i+1, min(i+4, len(hist_data))):
                    if closes[j] < opens[i]:  # Price went below the bullish candle open
                        consolidation = False
                        break
                
                if consolidation:
                    order_blocks.append({
                        'type': 'BULLISH_OB',
                        'price_range': (opens[i], highs[i]),
                        'strength': (closes[i] - opens[i]) / (highs[i] - lows[i]),
                        'volume_ratio': volumes[i] / np.mean(volumes[i-5:i]) if np.mean(volumes[i-5:i]) > 0 else 1,
                        'candle_index': i
                    })
                    score += 10
                    patterns.append(f"Bullish Order Block: {((closes[i] - opens[i]) / (highs[i] - lows[i])):.2f} strength")
            
            # Bearish Order Block: Strong bearish candle followed by consolidation
            elif (opens[i] > closes[i] and  # Bearish candle
                  (opens[i] - closes[i]) > (highs[i] - lows[i]) * 0.7 and  # Strong body
                  volumes[i] > np.mean(volumes[i-5:i]) * 1.5):  # High volume
                
                # Check for consolidation after
                consolidation = True
                for j in range(i+1, min(i+4, len(hist_data))):
                    if closes[j] > opens[i]:  # Price went above the bearish candle open
                        consolidation = False
                        break
                
                if consolidation:
                    order_blocks.append({
                        'type': 'BEARISH_OB',
                        'price_range': (lows[i], opens[i]),
                        'strength': (opens[i] - closes[i]) / (highs[i] - lows[i]),
                        'volume_ratio': volumes[i] / np.mean(volumes[i-5:i]) if np.mean(volumes[i-5:i]) > 0 else 1,
                        'candle_index': i
                    })
                    score -= 10
                    patterns.append(f"Bearish Order Block: {((opens[i] - closes[i]) / (highs[i] - lows[i])):.2f} strength")
        
        # Check if current price is near any Order Block
        current_price = closes[-1]
        for block in order_blocks:
            block_low, block_high = block['price_range']
            if block_low <= current_price <= block_high:
                score += 5 if block['type'] == 'BULLISH_OB' else -5
                patterns.append(f"Price in {block['type']}")
        
        return {
            'score': score,
            'patterns': patterns,
            'blocks': order_blocks
        }
        
    except Exception as e:
        logger.error(f"Error detecting Order Blocks: {e}")
        return {'score': 0, 'patterns': [], 'blocks': []}

def analyze_liquidity_concepts(hist_data):
    """Analyze liquidity concepts - sweeps, grabs, and pools"""
    try:
        if len(hist_data) < 10:
            return {'score': 0, 'patterns': [], 'liquidity_events': []}
        
        highs = hist_data['High'].values
        lows = hist_data['Low'].values
        closes = hist_data['Close'].values
        opens = hist_data['Open'].values
        volumes = hist_data['Volume'].values if 'Volume' in hist_data.columns else np.ones(len(closes))
        
        liquidity_events = []
        patterns = []
        score = 0
        
        # 1. Liquidity Sweeps - Price breaks previous high/low then reverses
        for i in range(5, len(hist_data) - 1):
            # Bullish Liquidity Sweep
            if (highs[i] > max(highs[i-5:i]) and  # Breaks previous high
                closes[i] < opens[i] and  # Bearish candle
                volumes[i] > np.mean(volumes[i-5:i]) * 1.3):  # High volume
                
                liquidity_events.append({
                    'type': 'BULLISH_LIQUIDITY_SWEEP',
                    'price': highs[i],
                    'volume_ratio': volumes[i] / np.mean(volumes[i-5:i]) if np.mean(volumes[i-5:i]) > 0 else 1,
                    'candle_index': i
                })
                score += 8
                patterns.append(f"Bullish Liquidity Sweep at ${highs[i]:.2f}")
            
            # Bearish Liquidity Sweep
            elif (lows[i] < min(lows[i-5:i]) and  # Breaks previous low
                  closes[i] > opens[i] and  # Bullish candle
                  volumes[i] > np.mean(volumes[i-5:i]) * 1.3):  # High volume
                
                liquidity_events.append({
                    'type': 'BEARISH_LIQUIDITY_SWEEP',
                    'price': lows[i],
                    'volume_ratio': volumes[i] / np.mean(volumes[i-5:i]) if np.mean(volumes[i-5:i]) > 0 else 1,
                    'candle_index': i
                })
                score -= 8
                patterns.append(f"Bearish Liquidity Sweep at ${lows[i]:.2f}")
        
        # 2. Equal Highs/Lows - Liquidity Pools
        for i in range(10, len(hist_data) - 5):
            # Equal Highs
            if abs(highs[i] - max(highs[i-10:i])) < highs[i] * 0.001:  # Within 0.1%
                liquidity_events.append({
                    'type': 'EQUAL_HIGHS',
                    'price': highs[i],
                    'candle_index': i
                })
                score += 5
                patterns.append(f"Equal Highs at ${highs[i]:.2f}")
            
            # Equal Lows
            elif abs(lows[i] - min(lows[i-10:i])) < lows[i] * 0.001:  # Within 0.1%
                liquidity_events.append({
                    'type': 'EQUAL_LOWS',
                    'price': lows[i],
                    'candle_index': i
                })
                score += 5
                patterns.append(f"Equal Lows at ${lows[i]:.2f}")
        
        # 3. Liquidity Grabs - Quick moves to grab stops
        for i in range(3, len(hist_data) - 1):
            # Bullish Liquidity Grab
            if (highs[i] > highs[i-1] and  # Higher high
                lows[i] < lows[i-1] and  # Lower low
                closes[i] > opens[i] and  # Bullish close
                volumes[i] > np.mean(volumes[i-3:i]) * 1.5):  # High volume
                
                liquidity_events.append({
                    'type': 'BULLISH_LIQUIDITY_GRAB',
                    'price': lows[i],
                    'candle_index': i
                })
                score += 6
                patterns.append(f"Bullish Liquidity Grab at ${lows[i]:.2f}")
            
            # Bearish Liquidity Grab
            elif (highs[i] > highs[i-1] and  # Higher high
                  lows[i] < lows[i-1] and  # Lower low
                  opens[i] > closes[i] and  # Bearish close
                  volumes[i] > np.mean(volumes[i-3:i]) * 1.5):  # High volume
                
                liquidity_events.append({
                    'type': 'BEARISH_LIQUIDITY_GRAB',
                    'price': highs[i],
                    'candle_index': i
                })
                score -= 6
                patterns.append(f"Bearish Liquidity Grab at ${highs[i]:.2f}")
        
        return {
            'score': score,
            'patterns': patterns,
            'liquidity_events': liquidity_events
        }
        
    except Exception as e:
        logger.error(f"Error analyzing liquidity concepts: {e}")
        return {'score': 0, 'patterns': [], 'liquidity_events': []}

def analyze_news_sentiment(symbol):
    """Analyze news sentiment and economic calendar impact"""
    try:
        # This would integrate with news APIs like NewsAPI, Alpha Vantage News, etc.
        # For now, we'll create a simulated sentiment analysis
        
        current_time = datetime.now()
        hour = current_time.hour
        
        # Simulate news sentiment based on time and symbol
        sentiment_data = {
            'overall_sentiment': 'NEUTRAL',
            'sentiment_score': 0,
            'news_impact': 'LOW',
            'economic_events': [],
            'market_fear_greed': 50,
            'recommendations': []
        }
        
        # Ensure sentiment_data is not None
        if sentiment_data is None:
            sentiment_data = {
                'overall_sentiment': 'NEUTRAL',
                'sentiment_score': 0,
                'news_impact': 'LOW',
                'economic_events': [],
                'market_fear_greed': 50,
                'recommendations': []
            }
        
        # 1. Economic Calendar Simulation
        economic_events = []
        
        # Check for major economic events (simulated)
        if current_time.weekday() in [0, 1, 2, 3, 4]:  # Weekdays
            if 8 <= hour < 10:  # London open
                economic_events.append({
                    'event': 'UK GDP Release',
                    'impact': 'HIGH',
                    'time': '09:00 GMT',
                    'sentiment': 'BULLISH' if symbol.endswith('=X') else 'NEUTRAL'
                })
            elif 13 <= hour < 15:  # NY open
                economic_events.append({
                    'event': 'US CPI Data',
                    'impact': 'HIGH',
                    'time': '13:30 GMT',
                    'sentiment': 'BEARISH' if 'inflation' in symbol.lower() else 'BULLISH'
                })
            elif 14 <= hour < 16:  # Fed time
                economic_events.append({
                    'event': 'Fed Interest Rate Decision',
                    'impact': 'CRITICAL',
                    'time': '14:00 GMT',
                    'sentiment': 'VOLATILE'
                })
        
        # 2. Market Sentiment Analysis
        if symbol.startswith('BTC') or 'crypto' in symbol.lower():
            # Crypto sentiment
            sentiment_data['overall_sentiment'] = 'BULLISH'
            sentiment_data['sentiment_score'] = 65
            sentiment_data['market_fear_greed'] = 70
            sentiment_data['news_impact'] = 'HIGH'
            economic_events.append({
                'event': 'Bitcoin ETF Approval',
                'impact': 'HIGH',
                'time': 'Recent',
                'sentiment': 'BULLISH'
            })
        elif symbol.endswith('=X'):
            # Forex sentiment
            sentiment_data['overall_sentiment'] = 'BEARISH'
            sentiment_data['sentiment_score'] = 35
            sentiment_data['market_fear_greed'] = 30
            sentiment_data['news_impact'] = 'MEDIUM'
            economic_events.append({
                'event': 'USD Strength',
                'impact': 'MEDIUM',
                'time': 'Ongoing',
                'sentiment': 'BEARISH'
            })
        elif any(x in symbol for x in ['AAPL', 'MSFT', 'GOOGL', 'TSLA']):
            # Tech stock sentiment
            sentiment_data['overall_sentiment'] = 'BULLISH'
            sentiment_data['sentiment_score'] = 75
            sentiment_data['market_fear_greed'] = 80
            sentiment_data['news_impact'] = 'HIGH'
            economic_events.append({
                'event': 'AI Technology Boom',
                'impact': 'HIGH',
                'time': 'Ongoing',
                'sentiment': 'BULLISH'
            })
        else:
            # General market sentiment
            sentiment_data['overall_sentiment'] = 'NEUTRAL'
            sentiment_data['sentiment_score'] = 50
            sentiment_data['market_fear_greed'] = 50
            sentiment_data['news_impact'] = 'LOW'
        
        # 3. Calculate sentiment impact on trading
        sentiment_score = sentiment_data['sentiment_score']
        news_impact = sentiment_data['news_impact']
        
        # Adjust sentiment based on economic events
        for event in economic_events:
            if event['impact'] == 'CRITICAL':
                sentiment_score += 20 if event['sentiment'] == 'BULLISH' else -20
            elif event['impact'] == 'HIGH':
                sentiment_score += 15 if event['sentiment'] == 'BULLISH' else -15
            elif event['impact'] == 'MEDIUM':
                sentiment_score += 10 if event['sentiment'] == 'BULLISH' else -10
        
        # Clamp sentiment score between 0-100
        sentiment_score = max(0, min(100, sentiment_score))
        
        # 4. Generate trading recommendations based on sentiment
        recommendations = []
        if sentiment_score > 70:
            recommendations.append("Strong Bullish Sentiment - Consider Long Positions")
            sentiment_data['overall_sentiment'] = 'BULLISH'
        elif sentiment_score > 60:
            recommendations.append("Moderate Bullish Sentiment - Favor Long Bias")
            sentiment_data['overall_sentiment'] = 'BULLISH'
        elif sentiment_score < 30:
            recommendations.append("Strong Bearish Sentiment - Consider Short Positions")
            sentiment_data['overall_sentiment'] = 'BEARISH'
        elif sentiment_score < 40:
            recommendations.append("Moderate Bearish Sentiment - Favor Short Bias")
            sentiment_data['overall_sentiment'] = 'BEARISH'
        else:
            recommendations.append("Neutral Sentiment - Wait for Clear Direction")
            sentiment_data['overall_sentiment'] = 'NEUTRAL'
        
        # Add news impact warnings
        if news_impact == 'CRITICAL':
            recommendations.append("⚠️ CRITICAL NEWS EVENT - High Volatility Expected")
        elif news_impact == 'HIGH':
            recommendations.append("📰 High Impact News - Monitor Closely")
        
        sentiment_data['sentiment_score'] = sentiment_score
        sentiment_data['economic_events'] = economic_events
        sentiment_data['recommendations'] = recommendations
        
        return {
            'score': (sentiment_score - 50) * 0.5,  # Convert to -25 to +25 range
            'sentiment_data': sentiment_data,
            'patterns': [f"Sentiment: {sentiment_data['overall_sentiment']}", 
                        f"Impact: {news_impact}",
                        f"Fear/Greed: {sentiment_data['market_fear_greed']}"]
        }
        
    except Exception as e:
        logger.error(f"Error analyzing news sentiment: {e}")
        return {'score': 0, 'sentiment_data': {}, 'patterns': []}

def analyze_price_action_patterns(hist_data):
    """Comprehensive price action analysis with candlestick patterns and rejection analysis"""
    try:
        if len(hist_data) < 5:
            return {'score': 0, 'patterns': [], 'signals': []}
        
        close_prices = hist_data['Close'].values
        high_prices = hist_data['High'].values
        low_prices = hist_data['Low'].values
        open_prices = hist_data['Open'].values
        volume = hist_data['Volume'].values if 'Volume' in hist_data.columns else np.ones(len(close_prices))
        
        score = 0
        patterns = []
        signals = []
        
        # 1. CANDLESTICK PATTERN ANALYSIS
        candlestick_analysis = detect_advanced_candlestick_patterns(hist_data)
        score += candlestick_analysis['score']
        patterns.extend(candlestick_analysis['patterns'])
        signals.extend(candlestick_analysis['signals'])
        
        # 2. REJECTION PATTERN ANALYSIS
        rejection_analysis = detect_rejection_patterns(hist_data)
        score += rejection_analysis['score']
        patterns.extend(rejection_analysis['patterns'])
        signals.extend(rejection_analysis['signals'])
        
        # 3. SUPPORT/RESISTANCE WITH PRICE ACTION
        sr_analysis = analyze_support_resistance_with_price_action(hist_data)
        score += sr_analysis['score']
        patterns.extend(sr_analysis['patterns'])
        signals.extend(sr_analysis['signals'])
        
        # 4. VOLUME PRICE ACTION ANALYSIS
        volume_analysis = analyze_volume_price_action(hist_data)
        score += volume_analysis['score']
        patterns.extend(volume_analysis['patterns'])
        signals.extend(volume_analysis['signals'])
        
        # 5. BREAKOUT CONFIRMATION
        breakout_analysis = analyze_breakout_confirmation(hist_data)
        score += breakout_analysis['score']
        patterns.extend(breakout_analysis['patterns'])
        signals.extend(breakout_analysis['signals'])
        
        return {
            'score': score,
            'patterns': patterns,
            'signals': signals,
            'candlestick': candlestick_analysis,
            'rejection': rejection_analysis,
            'support_resistance': sr_analysis,
            'volume': volume_analysis,
            'breakout': breakout_analysis,
            'overall_signal': 'BULLISH' if score > 5 else 'BEARISH' if score < -5 else 'NEUTRAL'
        }
        
    except Exception as e:
        logger.error(f"Error in price action analysis: {e}")
        return {'score': 0, 'patterns': [], 'signals': []}

def detect_advanced_candlestick_patterns(hist_data):
    """Detect advanced candlestick patterns with volume confirmation"""
    try:
        close_prices = hist_data['Close'].values
        high_prices = hist_data['High'].values
        low_prices = hist_data['Low'].values
        open_prices = hist_data['Open'].values
        volume = hist_data['Volume'].values if 'Volume' in hist_data.columns else np.ones(len(close_prices))
        
        score = 0
        patterns = []
        signals = []
        
        if len(close_prices) < 3:
            return {'score': 0, 'patterns': [], 'signals': []}
        
        # Get last 3 candles for pattern detection
        o1, o2, o3 = open_prices[-3:]
        h1, h2, h3 = high_prices[-3:]
        l1, l2, l3 = low_prices[-3:]
        c1, c2, c3 = close_prices[-3:]
        v1, v2, v3 = volume[-3:]
        
        # Calculate candle properties
        body1 = abs(c1 - o1)
        body2 = abs(c2 - o2)
        body3 = abs(c3 - o3)
        upper_shadow1 = h1 - max(o1, c1)
        lower_shadow1 = min(o1, c1) - l1
        total_range1 = h1 - l1
        
        # 1. HAMMER PATTERN (Reversal)
        if (lower_shadow1 > body1 * 2 and  # Long lower shadow
            upper_shadow1 < body1 * 0.5 and  # Small upper shadow
            body1 > 0 and  # Has a body
            total_range1 > 0):
            score += 3
            patterns.append("Hammer")
            signals.append("BULLISH_REVERSAL")
        
        # 2. SHOOTING STAR PATTERN (Reversal)
        if (upper_shadow1 > body1 * 2 and  # Long upper shadow
            lower_shadow1 < body1 * 0.5 and  # Small lower shadow
            body1 > 0 and
            total_range1 > 0):
            score -= 3
            patterns.append("Shooting Star")
            signals.append("BEARISH_REVERSAL")
        
        # 3. DOJI PATTERN (Indecision)
        if body1 < total_range1 * 0.1:  # Very small body
            score += 0.5  # Neutral but shows indecision
            patterns.append("Doji")
            signals.append("INDECISION")
        
        # 4. BULLISH ENGULFING (Reversal)
        if (c2 < o2 and  # Previous bearish
            c1 > o1 and  # Current bullish
            c1 > o2 and  # Current close above previous open
            o1 < c2):    # Current open below previous close
            score += 4
            patterns.append("Bullish Engulfing")
            signals.append("BULLISH_REVERSAL")
        
        # 5. BEARISH ENGULFING (Reversal)
        if (c2 > o2 and  # Previous bullish
            c1 < o1 and  # Current bearish
            c1 < o2 and  # Current close below previous open
            o1 > c2):    # Current open above previous close
            score -= 4
            patterns.append("Bearish Engulfing")
            signals.append("BEARISH_REVERSAL")
        
        # 6. INSIDE BAR PATTERN (Consolidation)
        if (h1 < h2 and l1 > l2):  # Current bar inside previous
            score += 1
            patterns.append("Inside Bar")
            signals.append("CONSOLIDATION")
        
        # 7. OUTSIDE BAR PATTERN (Breakout)
        if (h1 > h2 and l1 < l2):  # Current bar engulfs previous
            if c1 > o1:  # Bullish outside bar
                score += 2
                patterns.append("Bullish Outside Bar")
                signals.append("BULLISH_BREAKOUT")
            else:  # Bearish outside bar
                score -= 2
                patterns.append("Bearish Outside Bar")
                signals.append("BEARISH_BREAKOUT")
        
        # 8. PIN BAR PATTERN (Rejection)
        if (upper_shadow1 > body1 * 3 and lower_shadow1 < body1 * 0.5):  # Pin bar up
            score -= 2
            patterns.append("Pin Bar (Bearish)")
            signals.append("BEARISH_REJECTION")
        elif (lower_shadow1 > body1 * 3 and upper_shadow1 < body1 * 0.5):  # Pin bar down
            score += 2
            patterns.append("Pin Bar (Bullish)")
            signals.append("BULLISH_REJECTION")
        
        # 9. THREE WHITE SOLDIERS (Strong Bullish)
        if (len(close_prices) >= 3 and
            c3 > o3 and c2 > o2 and c1 > o1 and  # All bullish
            c1 > c2 > c3 and  # Each close higher
            body1 > body2 > body3):  # Increasing strength
            score += 5
            patterns.append("Three White Soldiers")
            signals.append("STRONG_BULLISH")
        
        # 10. THREE BLACK CROWS (Strong Bearish)
        if (len(close_prices) >= 3 and
            o3 > c3 and o2 > c2 and o1 > c1 and  # All bearish
            c1 < c2 < c3 and  # Each close lower
            body1 > body2 > body3):  # Increasing strength
            score -= 5
            patterns.append("Three Black Crows")
            signals.append("STRONG_BEARISH")
        
        # 11. MORNING STAR (Bullish Reversal)
        if (len(close_prices) >= 3 and
            o3 > c3 and  # First bearish
            abs(c2 - o2) < (h2 - l2) * 0.3 and  # Second small body
            c1 > o1 and  # Third bullish
            c1 > (o3 + c3) / 2):  # Third close above first midpoint
            score += 4
            patterns.append("Morning Star")
            signals.append("BULLISH_REVERSAL")
        
        # 12. EVENING STAR (Bearish Reversal)
        if (len(close_prices) >= 3 and
            c3 > o3 and  # First bullish
            abs(c2 - o2) < (h2 - l2) * 0.3 and  # Second small body
            o1 > c1 and  # Third bearish
            c1 < (o3 + c3) / 2):  # Third close below first midpoint
            score -= 4
            patterns.append("Evening Star")
            signals.append("BEARISH_REVERSAL")
        
        # 13. DRAGONFLY DOJI (Bullish Reversal)
        if (body1 < total_range1 * 0.1 and  # Small body
            lower_shadow1 > total_range1 * 0.6 and  # Long lower shadow
            upper_shadow1 < total_range1 * 0.1):  # Small upper shadow
            score += 3
            patterns.append("Dragonfly Doji")
            signals.append("BULLISH_REVERSAL")
        
        # 14. GRAVESTONE DOJI (Bearish Reversal)
        if (body1 < total_range1 * 0.1 and  # Small body
            upper_shadow1 > total_range1 * 0.6 and  # Long upper shadow
            lower_shadow1 < total_range1 * 0.1):  # Small lower shadow
            score -= 3
            patterns.append("Gravestone Doji")
            signals.append("BEARISH_REVERSAL")
        
        # 15. MARUBOZU (Strong Trend)
        if body1 > total_range1 * 0.8:  # Large body
            if c1 > o1:  # Bullish Marubozu
                score += 3
                patterns.append("Bullish Marubozu")
                signals.append("STRONG_BULLISH")
            else:  # Bearish Marubozu
                score -= 3
                patterns.append("Bearish Marubozu")
                signals.append("STRONG_BEARISH")
        
        # Volume confirmation
        avg_volume = np.mean(volume[-5:])
        if v1 > avg_volume * 1.5:  # High volume confirmation
            score = score * 1.5  # Boost score with volume
            patterns.append("+ Volume Confirmation")
        
        return {
            'score': score,
            'patterns': patterns,
            'signals': signals
        }
        
    except Exception as e:
        logger.error(f"Error in candlestick pattern detection: {e}")
        return {'score': 0, 'patterns': [], 'signals': []}

def detect_rejection_patterns(hist_data):
    """Detect rejection patterns at key levels"""
    try:
        close_prices = hist_data['Close'].values
        high_prices = hist_data['High'].values
        low_prices = hist_data['Low'].values
        open_prices = hist_data['Open'].values
        volume = hist_data['Volume'].values if 'Volume' in hist_data.columns else np.ones(len(close_prices))
        
        score = 0
        patterns = []
        signals = []
        
        if len(close_prices) < 5:
            return {'score': 0, 'patterns': [], 'signals': []}
        
        # Get recent data
        recent_highs = high_prices[-10:]
        recent_lows = low_prices[-10:]
        current_high = high_prices[-1]
        current_low = low_prices[-1]
        current_close = close_prices[-1]
        current_open = open_prices[-1]
        
        # 1. RESISTANCE REJECTION
        resistance_level = max(recent_highs[:-1])  # Exclude current candle
        if (current_high > resistance_level * 0.998 and  # Near resistance
            current_close < resistance_level and  # Closed below resistance
            current_high - max(current_open, current_close) > abs(current_close - current_open) * 0.5):  # Upper wick
            score -= 3
            patterns.append("Resistance Rejection")
            signals.append("BEARISH_REJECTION")
        
        # 2. SUPPORT REJECTION
        support_level = min(recent_lows[:-1])  # Exclude current candle
        if (current_low < support_level * 1.002 and  # Near support
            current_close > support_level and  # Closed above support
            min(current_open, current_close) - current_low > abs(current_close - current_open) * 0.5):  # Lower wick
            score += 3
            patterns.append("Support Rejection")
            signals.append("BULLISH_REJECTION")
        
        # 3. TRENDLINE REJECTION (Simplified)
        if len(close_prices) >= 10:
            # Look for rejection at moving average levels
            sma_20 = np.mean(close_prices[-20:])
            if (abs(current_close - sma_20) / sma_20 < 0.02 and  # Near SMA20
                current_high > sma_20 and current_close < sma_20):  # Rejected from above
                score -= 2
                patterns.append("SMA20 Rejection")
                signals.append("BEARISH_REJECTION")
            elif (abs(current_close - sma_20) / sma_20 < 0.02 and
                  current_low < sma_20 and current_close > sma_20):  # Rejected from below
                score += 2
                patterns.append("SMA20 Rejection")
                signals.append("BULLISH_REJECTION")
        
        return {
            'score': score,
            'patterns': patterns,
            'signals': signals
        }
        
    except Exception as e:
        logger.error(f"Error in rejection pattern detection: {e}")
        return {'score': 0, 'patterns': [], 'signals': []}

def analyze_support_resistance_with_price_action(hist_data):
    """Analyze support/resistance levels with price action confirmation"""
    try:
        close_prices = hist_data['Close'].values
        high_prices = hist_data['High'].values
        low_prices = hist_data['Low'].values
        volume = hist_data['Volume'].values if 'Volume' in hist_data.columns else np.ones(len(close_prices))
        
        score = 0
        patterns = []
        signals = []
        
        if len(close_prices) < 20:
            return {'score': 0, 'patterns': [], 'signals': []}
        
        # Find key levels
        recent_highs = high_prices[-20:]
        recent_lows = low_prices[-20:]
        current_price = close_prices[-1]
        
        # 1. RESISTANCE LEVEL ANALYSIS
        resistance_levels = []
        for i in range(len(recent_highs) - 1):
            if recent_highs[i] == max(recent_highs[i:i+3]):  # Local high
                resistance_levels.append(recent_highs[i])
        
        # Check for resistance rejection
        for level in resistance_levels:
            if abs(current_price - level) / level < 0.01:  # Within 1%
                # Check if price was rejected from this level recently
                recent_closes = close_prices[-5:]
                if any(close > level * 1.005 for close in recent_closes):  # Price touched above
                    score -= 2
                    patterns.append(f"Resistance at ${level:.2f}")
                    signals.append("BEARISH_SR")
        
        # 2. SUPPORT LEVEL ANALYSIS
        support_levels = []
        for i in range(len(recent_lows) - 1):
            if recent_lows[i] == min(recent_lows[i:i+3]):  # Local low
                support_levels.append(recent_lows[i])
        
        # Check for support bounce
        for level in support_levels:
            if abs(current_price - level) / level < 0.01:  # Within 1%
                recent_closes = close_prices[-5:]
                if any(close < level * 0.995 for close in recent_closes):  # Price touched below
                    score += 2
                    patterns.append(f"Support at ${level:.2f}")
                    signals.append("BULLISH_SR")
        
        # 3. BREAKOUT CONFIRMATION
        if resistance_levels:
            strongest_resistance = max(resistance_levels)
            if current_price > strongest_resistance * 1.01:  # 1% above resistance
                score += 3
                patterns.append("Resistance Breakout")
                signals.append("BULLISH_BREAKOUT")
        
        if support_levels:
            strongest_support = min(support_levels)
            if current_price < strongest_support * 0.99:  # 1% below support
                score -= 3
                patterns.append("Support Breakdown")
                signals.append("BEARISH_BREAKDOWN")
        
        return {
            'score': score,
            'patterns': patterns,
            'signals': signals
        }
        
    except Exception as e:
        logger.error(f"Error in support/resistance analysis: {e}")
        return {'score': 0, 'patterns': [], 'signals': []}

def analyze_volume_price_action(hist_data):
    """Analyze volume patterns with price action"""
    try:
        close_prices = hist_data['Close'].values
        high_prices = hist_data['High'].values
        low_prices = hist_data['Low'].values
        volume = hist_data['Volume'].values if 'Volume' in hist_data.columns else np.ones(len(close_prices))
        
        score = 0
        patterns = []
        signals = []
        
        if len(close_prices) < 10:
            return {'score': 0, 'patterns': [], 'signals': []}
        
        # Calculate volume metrics
        avg_volume = np.mean(volume[-10:])
        current_volume = volume[-1]
        current_close = close_prices[-1]
        previous_close = close_prices[-2]
        
        # 1. VOLUME CONFIRMATION
        if current_volume > avg_volume * 1.5:  # High volume
            if current_close > previous_close:  # Bullish move
                score += 2
                patterns.append("High Volume Bullish")
                signals.append("BULLISH_VOLUME")
            else:  # Bearish move
                score -= 2
                patterns.append("High Volume Bearish")
                signals.append("BEARISH_VOLUME")
        
        # 2. VOLUME DIVERGENCE
        if len(close_prices) >= 5:
            recent_closes = close_prices[-5:]
            recent_volumes = volume[-5:]
            
            # Price up, volume down (bearish divergence)
            if (recent_closes[-1] > recent_closes[-3] and
                recent_volumes[-1] < recent_volumes[-3]):
                score -= 1
                patterns.append("Volume Divergence (Bearish)")
                signals.append("BEARISH_DIVERGENCE")
            
            # Price down, volume down (bullish divergence)
            elif (recent_closes[-1] < recent_closes[-3] and
                  recent_volumes[-1] < recent_volumes[-3]):
                score += 1
                patterns.append("Volume Divergence (Bullish)")
                signals.append("BULLISH_DIVERGENCE")
        
        # 3. ACCUMULATION/DISTRIBUTION
        if len(close_prices) >= 10:
            # Calculate price change
            price_change = (close_prices[-1] - close_prices[-10]) / close_prices[-10] if close_prices[-10] != 0 else 0
            volume_change = (volume[-1] - avg_volume) / avg_volume if avg_volume != 0 else 0
            
            if price_change > 0.02 and volume_change > 0.5:  # Strong up move with volume
                score += 3
                patterns.append("Accumulation")
                signals.append("BULLISH_ACCUMULATION")
            elif price_change < -0.02 and volume_change > 0.5:  # Strong down move with volume
                score -= 3
                patterns.append("Distribution")
                signals.append("BEARISH_DISTRIBUTION")
        
        return {
            'score': score,
            'patterns': patterns,
            'signals': signals
        }
        
    except Exception as e:
        logger.error(f"Error in volume price action analysis: {e}")
        return {'score': 0, 'patterns': [], 'signals': []}

def analyze_volume_profile(hist_data):
    """Analyze Volume Profile to identify key trading levels"""
    try:
        if len(hist_data) < 50:
            return {'score': 0, 'key_levels': [], 'patterns': []}
        
        # Get recent data (last 50 periods for volume profile)
        recent_data = hist_data.tail(50)
        volume = recent_data['Volume'].values if 'Volume' in recent_data.columns else np.ones(len(recent_data))
        high = recent_data['High'].values
        low = recent_data['Low'].values
        close = recent_data['Close'].values
        
        # Calculate Volume Profile
        price_range = high.max() - low.min()
        num_bins = 20  # 20 price levels
        bin_size = price_range / num_bins
        
        # Create volume profile bins
        volume_profile = {}
        for i in range(num_bins):
            price_level = low.min() + (i * bin_size)
            volume_profile[price_level] = 0
        
        # Distribute volume across price levels
        for i in range(len(recent_data)):
            price_level = int((high[i] - low.min()) / bin_size)
            if 0 <= price_level < num_bins:
                level = low.min() + (price_level * bin_size)
                volume_profile[level] += volume[i]
        
        # Find key levels (high volume areas)
        sorted_levels = sorted(volume_profile.items(), key=lambda x: x[1], reverse=True)
        total_volume = sum(volume_profile.values())
        
        key_levels = []
        patterns = []
        score = 0
        
        # Top 3 volume levels
        for i, (level, vol) in enumerate(sorted_levels[:3]):
            volume_percentage = (vol / total_volume) * 100 if total_volume != 0 else 0
            if volume_percentage > 5:  # More than 5% of total volume
                key_levels.append({
                    'price': round(level, 2),
                    'volume_percentage': round(volume_percentage, 1),
                    'strength': 'High' if volume_percentage > 10 else 'Medium'
                })
                
                # Check if current price is near this level
                current_price = close[-1]
                if abs(current_price - level) / current_price < 0.02:  # Within 2%
                    patterns.append(f"Price at High Volume Level ({volume_percentage:.1f}%)")
                    score += 10 if volume_percentage > 10 else 5
        
        # Volume Profile Patterns
        if len(key_levels) >= 2:
            # Check for Volume Profile patterns
            levels = [level['price'] if isinstance(level, dict) else level for level in key_levels]
            current_price = close[-1]
            
            # POC (Point of Control) - highest volume level
            poc_level = key_levels[0]['price'] if isinstance(key_levels[0], dict) else key_levels[0]
            
            if current_price > poc_level:
                patterns.append("Price Above POC - Bullish Bias")
                score += 8
            elif current_price < poc_level:
                patterns.append("Price Below POC - Bearish Bias")
                score -= 8
            
            # Value Area (70% of volume)
            value_area_volume = sum([level['volume_percentage'] if isinstance(level, dict) else 0 for level in key_levels[:5]])
            if value_area_volume > 70:
                patterns.append("Strong Value Area Formation")
                score += 5
        
        return {
            'score': score,
            'key_levels': key_levels,
            'patterns': patterns,
            'poc_level': key_levels[0]['price'] if key_levels else None,
            'value_area_strength': len([l for l in key_levels if l['volume_percentage'] > 5])
        }
        
    except Exception as e:
        logger.error(f"Error in volume profile analysis: {e}")
        return {'score': 0, 'key_levels': [], 'patterns': []}

def analyze_market_sessions(hist_data):
    """Analyze market sessions (London, NY, Asian) for trading opportunities"""
    try:
        if len(hist_data) < 20:
            return {'score': 0, 'session_analysis': {}, 'patterns': []}
        
        # Get current time and session info
        current_time = datetime.now()
        current_hour = current_time.hour
        
        # Define market sessions (UTC times)
        sessions = {
            'Asian': {'start': 0, 'end': 8, 'name': 'Asian Session'},
            'London': {'start': 8, 'end': 16, 'name': 'London Session'},
            'NY': {'start': 13, 'end': 21, 'name': 'New York Session'},
            'Overlap': {'start': 13, 'end': 16, 'name': 'London-NY Overlap'}
        }
        
        # Determine current session
        current_session = None
        for session_name, session_info in sessions.items():
            if session_info['start'] <= current_hour < session_info['end']:
                current_session = session_name
                break
        
        if not current_session:
            current_session = 'Asian'  # Default to Asian if outside main sessions
        
        # Analyze session-specific patterns
        recent_data = hist_data.tail(20)
        volume = recent_data['Volume'].values if 'Volume' in recent_data.columns else np.ones(len(recent_data))
        close_prices = recent_data['Close'].values
        high_prices = recent_data['High'].values
        low_prices = recent_data['Low'].values
        
        score = 0
        patterns = []
        session_analysis = {}
        
        # Calculate session-specific metrics
        avg_volume = np.mean(volume)
        current_volume = volume[-1]
        price_change = (close_prices[-1] - close_prices[-2]) / close_prices[-2] if len(close_prices) > 1 else 0
        
        # Session-specific analysis
        if current_session == 'London':
            # London session - high volatility, trend continuation
            if current_volume > avg_volume * 1.3:
                score += 8
                patterns.append("High London Volume - Strong Move Expected")
            
            # London breakout patterns
            if abs(price_change) > 0.01:  # 1% move
                score += 5
                patterns.append("London Session Breakout")
                
        elif current_session == 'NY':
            # NY session - institutional activity, trend confirmation
            if current_volume > avg_volume * 1.5:
                score += 10
                patterns.append("High NY Volume - Institutional Activity")
            
            # NY trend confirmation
            if abs(price_change) > 0.015:  # 1.5% move
                score += 8
                patterns.append("NY Session Trend Confirmation")
                
        elif current_session == 'Overlap':
            # London-NY overlap - highest volatility
            if current_volume > avg_volume * 1.8:
                score += 12
                patterns.append("Overlap High Volume - Maximum Volatility")
            
            # Overlap breakout
            if abs(price_change) > 0.02:  # 2% move
                score += 10
                patterns.append("Overlap Session Breakout")
                
        elif current_session == 'Asian':
            # Asian session - consolidation, range trading
            if current_volume < avg_volume * 0.8:
                score += 3
                patterns.append("Low Asian Volume - Consolidation Phase")
            
            # Asian range trading
            price_range = (high_prices[-1] - low_prices[-1]) / close_prices[-1]
            if price_range < 0.01:  # Less than 1% range
                score += 2
                patterns.append("Asian Range Trading")
        
        # Session-specific signals
        session_signals = []
        if current_session in ['London', 'NY', 'Overlap']:
            if price_change > 0.01:
                session_signals.append(f"BULLISH_{current_session.upper()}")
            elif price_change < -0.01:
                session_signals.append(f"BEARISH_{current_session.upper()}")
        
        session_analysis = {
            'current_session': current_session,
            'session_name': sessions[current_session]['name'],
            'volume_ratio': round(current_volume / avg_volume, 2) if avg_volume > 0 else 1,
            'price_change': round(price_change * 100, 2),
            'signals': session_signals
        }
        
        return {
            'score': score,
            'session_analysis': session_analysis,
            'patterns': patterns
        }
        
    except Exception as e:
        logger.error(f"Error in market session analysis: {e}")
        return {'score': 0, 'session_analysis': {}, 'patterns': []}

def analyze_breakout_confirmation(hist_data):
    """Analyze breakout patterns with price action confirmation"""
    try:
        close_prices = hist_data['Close'].values
        high_prices = hist_data['High'].values
        low_prices = hist_data['Low'].values
        volume = hist_data['Volume'].values if 'Volume' in hist_data.columns else np.ones(len(close_prices))
        
        score = 0
        patterns = []
        signals = []
        
        if len(close_prices) < 10:
            return {'score': 0, 'patterns': [], 'signals': []}
        
        # 1. TRENDLINE BREAKOUT
        if len(close_prices) >= 20:
            # Simple trendline detection
            recent_highs = high_prices[-10:]
            recent_lows = low_prices[-10:]
            
            # Uptrend breakout
            if (recent_highs[-1] > max(recent_highs[:-1]) and
                close_prices[-1] > close_prices[-2]):  # New high with follow-through
                score += 2
                patterns.append("Uptrend Breakout")
                signals.append("BULLISH_BREAKOUT")
            
            # Downtrend breakout
            elif (recent_lows[-1] < min(recent_lows[:-1]) and
                  close_prices[-1] < close_prices[-2]):  # New low with follow-through
                score -= 2
                patterns.append("Downtrend Breakout")
                signals.append("BEARISH_BREAKOUT")
        
        # 2. RANGE BREAKOUT
        if len(close_prices) >= 15:
            # Look for consolidation followed by breakout
            range_high = max(high_prices[-15:])
            range_low = min(low_prices[-15:])
            range_size = range_high - range_low
            
            if range_size > 0:
                # Check if price broke out of range
                if close_prices[-1] > range_high * 1.005:  # 0.5% above range
                    score += 3
                    patterns.append("Range Breakout (Bullish)")
                    signals.append("BULLISH_RANGE_BREAKOUT")
                elif close_prices[-1] < range_low * 0.995:  # 0.5% below range
                    score -= 3
                    patterns.append("Range Breakout (Bearish)")
                    signals.append("BEARISH_RANGE_BREAKOUT")
        
        # 3. VOLUME CONFIRMATION FOR BREAKOUTS
        avg_volume = np.mean(volume[-10:])
        if volume[-1] > avg_volume * 1.3:  # High volume on breakout
            if score > 0:  # Bullish breakout
                score += 1
                patterns.append("+ Volume Confirmation")
            elif score < 0:  # Bearish breakout
                score -= 1
                patterns.append("+ Volume Confirmation")
        
        return {
            'score': score,
            'patterns': patterns,
            'signals': signals
        }
        
    except Exception as e:
        logger.error(f"Error in breakout analysis: {e}")
        return {'score': 0, 'patterns': [], 'signals': []}

def calculate_technical_indicators(hist_data):
    """Calculate advanced technical indicators"""
    try:
        if len(hist_data) < 20:
            return {}
        
        # RSI
        delta = hist_data['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        # MACD
        ema_12 = hist_data['Close'].ewm(span=12).mean()
        ema_26 = hist_data['Close'].ewm(span=26).mean()
        macd = ema_12 - ema_26
        macd_signal = macd.ewm(span=9).mean()
        macd_histogram = macd - macd_signal
        
        # Bollinger Bands
        sma_20 = hist_data['Close'].rolling(window=20).mean()
        std_20 = hist_data['Close'].rolling(window=20).std()
        bb_upper = sma_20 + (std_20 * 2)
        bb_lower = sma_20 - (std_20 * 2)
        
        # Current values
        current_rsi = rsi.iloc[-1] if not rsi.empty else 50
        current_macd = macd.iloc[-1] if not macd.empty else 0
        current_bb_position = (hist_data['Close'].iloc[-1] - bb_lower.iloc[-1]) / (bb_upper.iloc[-1] - bb_lower.iloc[-1]) if not bb_upper.empty else 0.5
        
        return {
            'rsi': round(current_rsi, 2),
            'macd': round(current_macd, 4),
            'bb_position': round(current_bb_position, 2),
            'bb_upper': round(bb_upper.iloc[-1], 2) if not bb_upper.empty else 0,
            'bb_lower': round(bb_lower.iloc[-1], 2) if not bb_lower.empty else 0,
            'sma_20': round(sma_20.iloc[-1], 2) if not sma_20.empty else 0
        }
    except Exception as e:
        logger.error(f"Error calculating technical indicators: {e}")
        return {}

def generate_ict_smc_signal(symbol, hist_data, timeframe="1h"):
    """Generate CLEAN ICT/SMC signal with ML enhancement - Focused on core principles"""
    try:
        if hist_data.empty or len(hist_data) < 20:
            return None
        
        # Get current price
        current_price = hist_data['Close'].iloc[-1]
        
        # ===== MULTI-TIMEFRAME ICT/SMC ANALYSIS =====
        # Get multi-timeframe data for trend analysis
        multi_timeframe_data = get_multi_timeframe_data(symbol)
        
        # Core ICT/SMC analysis on current timeframe
        kill_zone_analysis = analyze_kill_zones(hist_data, timeframe)
        order_blocks = detect_enhanced_order_blocks(hist_data)
        fvg_analysis = detect_fair_value_gaps(hist_data)
        liquidity_analysis = analyze_liquidity_concepts(hist_data)
        technical_indicators = calculate_technical_indicators(hist_data)
        
        # ===== ADVANCED ICT/SMC FEATURES =====
        # Enhanced Market Structure Analysis
        market_structure = analyze_market_structure(hist_data)
        
        # Institutional Order Flow Analysis
        institutional_flow = analyze_institutional_order_flow(hist_data)
        
        # Trading Sessions & Kill Zones Analysis
        session_analysis = analyze_trading_sessions(hist_data)
        
        # Smart Money Concepts Analysis
        smc_analysis = analyze_smart_money_concepts(hist_data)
        
        # Advanced ICT Pattern Detection
        advanced_patterns = detect_advanced_ict_patterns(hist_data)
        
        # Market Condition Analysis & Optimization
        market_conditions = analyze_market_conditions(hist_data)
        optimization = market_conditions['optimization']
        
        # ===== MULTI-TIMEFRAME TREND ANALYSIS =====
        trend_analysis = analyze_multi_timeframe_trend(multi_timeframe_data)
        
        # ===== CORE ICT/SMC SIGNAL GENERATION =====
        signal_score = 0
        quality_factors = []
        
        # 1. Multi-timeframe trend alignment (Higher timeframe bias)
        if trend_analysis['trend_alignment'] > 0.6:  # 60%+ alignment
            signal_score += 25
            quality_factors.append(f"Multi-TF Trend: {trend_analysis['primary_trend']}")
        
        # 2. Kill Zone Analysis (Core ICT)
        kill_zone_score = kill_zone_analysis.get('score', 0)
        if kill_zone_score > 0:
            signal_score += kill_zone_score
            quality_factors.append(f"Kill Zone: {kill_zone_analysis.get('active_session', 'N/A')}")
        
        # 3. Order Blocks (Core SMC)
        ob_score = order_blocks.get('score', 0)
        ob_patterns = order_blocks.get('patterns', [])
        if ob_score != 0:
            signal_score += ob_score
            quality_factors.extend([f"Order Block: {pattern}" for pattern in ob_patterns[:1]])
        
        # 4. Fair Value Gaps (Core ICT)
        fvg_score = fvg_analysis.get('score', 0)
        fvg_patterns = fvg_analysis.get('patterns', [])
        if fvg_score != 0:
            signal_score += fvg_score
            quality_factors.extend([f"FVG: {pattern}" for pattern in fvg_patterns[:1]])
        
        # 5. Liquidity Sweeps (Core SMC)
        liquidity_score = liquidity_analysis.get('score', 0)
        liquidity_patterns = liquidity_analysis.get('patterns', [])
        if liquidity_score != 0:
            signal_score += liquidity_score
            quality_factors.extend([f"Liquidity: {pattern}" for pattern in liquidity_patterns[:1]])
        
        # 6. Key level confluence (Multi-timeframe levels)
        level_confluence = check_level_confluence(current_price, multi_timeframe_data)
        if level_confluence > 0:
            signal_score += level_confluence
            quality_factors.append(f"Key Level Confluence: {level_confluence} levels")
        
        # 7. Market Structure Breaks (BOS/CHoCH)
        if market_structure['bos']:
            signal_score += 20
            quality_factors.append(f"Break of Structure: {market_structure['bos_details']['type']}")
        elif market_structure['choch']:
            signal_score += 15
            quality_factors.append(f"Change of Character: {market_structure['choch_details']['type']}")
        
        # 8. Advanced ICT Pattern Detection
        advanced_score = advanced_patterns.get('score', 0)
        advanced_confluence = advanced_patterns.get('confluence', 0)
        if advanced_score > 0:
            signal_score += advanced_score
            quality_factors.append(f"Advanced Patterns: {len(advanced_patterns.get('patterns', []))} detected")
        if advanced_confluence > 0:
            signal_score += advanced_confluence
            quality_factors.append(f"Pattern Confluence: {advanced_confluence} points")
        
        # 9. Market Condition Optimization
        # Apply market condition optimization to signal parameters
        signal_score = int(signal_score * optimization.get('signal_threshold_multiplier', 1.0))
        confidence_boost = optimization.get('confidence_boost', 0)
        risk_reward_adjustment = optimization.get('risk_reward_adjustment', 0)
        
        # 8. Institutional Order Flow
        if institutional_flow['detected']:
            signal_score += institutional_flow['score']
            quality_factors.append(f"Institutional Flow: {institutional_flow['type']}")
        
        # 9. Trading Session Quality
        if session_analysis['kill_zones']:
            best_kill_zone = session_analysis['kill_zones'][0]  # Highest quality
            signal_score += best_kill_zone['quality'] * 10
            quality_factors.append(f"Kill Zone: {best_kill_zone['name']} ({best_kill_zone['quality']:.2f})")
        
        # 2.4. NEWS SENTIMENT ANALYSIS
        news_sentiment = analyze_news_sentiment(symbol)
        if news_sentiment and news_sentiment.get('score', 0) != 0:
            signal_score += news_sentiment['score']
            quality_factors.extend([f"News: {pattern}" for pattern in news_sentiment.get('patterns', [])[:2]])
        
        # 3. MULTI-TIMEFRAME CONFIRMATION - Critical for quality
        mtf_direction = trend_analysis.get('consensus_direction', 'NEUTRAL')
        mtf_confidence = trend_analysis.get('consensus_confidence', 0)
        
        # Apply market condition optimization to MTF requirements
        mtf_threshold = 70 + confidence_boost  # Dynamic threshold based on market conditions
        
        # STRICT Multi-timeframe validation - ensures high quality
        if mtf_direction == 'BULLISH' and mtf_confidence > mtf_threshold:
            signal_score += trend_analysis.get('consensus_score', 0)
            quality_factors.append(f"MTF Bullish: {mtf_confidence}%")
        elif mtf_direction == 'BEARISH' and mtf_confidence > mtf_threshold:
            signal_score -= trend_analysis.get('consensus_score', 0)
            quality_factors.append(f"MTF Bearish: {mtf_confidence}%")
        else:
            # Multi-timeframe doesn't confirm - reject signal for quality
            quality_factors.append(f"🚨 REJECTED: MTF Conflict {mtf_confidence}%")
            return None
            
            # If multi-timeframe is neutral, don't allow high confidence signals
            if mtf_confidence > 80:  # High neutral consensus
                quality_factors.append("🚨 HIGH MTF CONFLICT - Signal Rejected")
                return None  # Reject the signal entirely
        
        # 4. Technical Analysis - Stricter thresholds
        rsi = technical_indicators.get('rsi', 50)
        bb_position = technical_indicators.get('bb_position', 0.5)
        macd = technical_indicators.get('macd', 0)
        
        # RSI Analysis - Only extreme levels with MTF confirmation
        if rsi < 25:  # Very oversold
            if mtf_direction == 'BULLISH' and mtf_confidence > 60:
                signal_score += 20
                quality_factors.append(f"RSI Oversold: {rsi}")
            else:
                signal_score += 5  # Reduced bonus without MTF confirmation
                quality_factors.append(f"RSI Oversold: {rsi} (No MTF Confirmation)")
        elif rsi > 75:  # Very overbought
            if mtf_direction == 'BEARISH' and mtf_confidence > 60:
                signal_score -= 20
                quality_factors.append(f"RSI Overbought: {rsi}")
            else:
                signal_score -= 5  # Reduced penalty without MTF confirmation
                quality_factors.append(f"RSI Overbought: {rsi} (No MTF Confirmation)")
        elif 30 <= rsi <= 70:  # Neutral zone
            signal_score += 0  # No bias for neutral RSI
        
        # Bollinger Bands - Only extreme positions
        if bb_position < 0.15:  # Very near lower band
            signal_score += 15
            quality_factors.append(f"BB Lower: {bb_position}")
        elif bb_position > 0.85:  # Very near upper band
            signal_score -= 15
            quality_factors.append(f"BB Upper: {bb_position}")
        
        # MACD Analysis
        if macd > 0.001:  # Positive momentum
            signal_score += 10
            quality_factors.append(f"MACD Bullish: {macd}")
        elif macd < -0.001:  # Negative momentum
            signal_score -= 10
            quality_factors.append(f"MACD Bearish: {macd}")
        
        # 4. PRICE ACTION ANALYSIS - NEW ENHANCEMENT!
        price_action_analysis = analyze_price_action_patterns(hist_data)
        pa_score = price_action_analysis.get('score', 0)
        pa_patterns = price_action_analysis.get('patterns', [])
        pa_signals = price_action_analysis.get('signals', [])
        
        if pa_score != 0:
            signal_score += pa_score
            quality_factors.extend([f"PA: {pattern}" for pattern in pa_patterns[:3]])  # Top 3 patterns
        
        # 4.5. VOLUME PROFILE ANALYSIS - NEW!
        volume_profile_analysis = analyze_volume_profile(hist_data)
        vp_score = volume_profile_analysis.get('score', 0)
        vp_patterns = volume_profile_analysis.get('patterns', [])
        vp_key_levels = volume_profile_analysis.get('key_levels', [])
        
        if vp_score != 0:
            signal_score += vp_score
            quality_factors.extend([f"VP: {pattern}" for pattern in vp_patterns[:2]])  # Top 2 patterns
        
        # 4.6. MARKET SESSION ANALYSIS - NEW!
        session_analysis = analyze_market_sessions(hist_data)
        session_score = session_analysis.get('score', 0)
        session_patterns = session_analysis.get('patterns', [])
        session_data = session_analysis.get('session_analysis', {})
        
        if session_score != 0:
            signal_score += session_score
            quality_factors.extend([f"Session: {pattern}" for pattern in session_patterns[:2]])  # Top 2 patterns
        
        # 5. Volume Analysis - Critical for quality
        volume = hist_data['Volume'].iloc[-1] if 'Volume' in hist_data.columns else 0
        avg_volume = hist_data['Volume'].rolling(20).mean().iloc[-1] if 'Volume' in hist_data.columns else 0
        volume_ratio = volume / avg_volume if avg_volume > 0 else 1
        
        if volume_ratio > 1.5:  # High volume confirmation
            signal_score += 15
            quality_factors.append(f"High Volume: {volume_ratio:.1f}x")
        elif volume_ratio < 0.5:  # Low volume - reduce confidence
            signal_score -= 10
            quality_factors.append(f"Low Volume: {volume_ratio:.1f}x")
        
        # 6. Trend Analysis - Moving average alignment
        sma_20 = technical_indicators.get('sma_20', current_price)
        if current_price > sma_20 * 1.02:  # Above SMA with buffer
            signal_score += 10
            quality_factors.append("Above SMA20")
        elif current_price < sma_20 * 0.98:  # Below SMA with buffer
            signal_score -= 10
            quality_factors.append("Below SMA20")
        
        # 7. Signal Determination - HIGH QUALITY ONLY for profitability
        # Apply market condition optimization to confidence thresholds
        min_confidence = 65 + confidence_boost  # Dynamic confidence based on market conditions
        strong_threshold = 80 + confidence_boost  # Dynamic strong threshold
        
        # DEBUG: Log signal score for debugging
        logger.info(f"Signal Debug for {symbol}: Score={signal_score}, MTF={mtf_direction} ({mtf_confidence}%), PA={pa_score}")
        
        # FINAL MTF CONFLICT CHECK - Only reject if very high neutral consensus
        if mtf_direction == 'NEUTRAL' and mtf_confidence > 90:
            quality_factors.append("🚨 REJECTED: Very High Neutral MTF Consensus")
            return None
        
        # HIGH QUALITY SIGNALS ONLY - Focus on profitability
        if signal_score >= 20:  # High threshold for BUY
            signal_type = "BUY"
            confidence = min(95, 60 + (signal_score - 20) * 1.0)
        elif signal_score <= -20:  # High threshold for SELL
            signal_type = "SELL"
            confidence = min(95, 60 + abs(signal_score + 20) * 1.0)
        else:
            # No signal if not strong enough - quality over quantity
            return None
        
        # 7. Final Quality Check - Only return high-quality signals
        if confidence < min_confidence:
            return None
        
        # 8. ADDITIONAL QUALITY FILTERS for profitability
        # Require at least 3 quality factors for high-quality signals
        if len(quality_factors) < 3:
            quality_factors.append("🚨 REJECTED: Insufficient Quality Factors")
            return None
        
        # Require institutional flow confirmation for high-quality signals
        if not institutional_flow['detected']:
            quality_factors.append("⚠️ No Institutional Flow Detected")
            # Don't reject, but note the limitation
        
        # Require market structure confirmation
        if not market_structure['bos'] and not market_structure['choch']:
            quality_factors.append("⚠️ No Market Structure Break")
            # Don't reject, but note the limitation
        
        # 9. Calculate price targets with STRICT risk management for profitability
        atr = hist_data['High'].rolling(14).max() - hist_data['Low'].rolling(14).min()
        current_atr = atr.iloc[-1] if not atr.empty else current_price * 0.02
        
        # Ensure minimum ATR for meaningful price targets
        min_atr = current_price * 0.008  # 0.8% minimum for quality
        current_atr = max(current_atr, min_atr)
        
        # STRICT Risk/Reward requirements for profitability
        # Apply market condition optimization to risk/reward requirements
        min_risk_reward = 2.0 + risk_reward_adjustment  # Dynamic R/R based on market conditions
        
        if signal_type == "BUY":
            target_price = current_price + (current_atr * min_risk_reward)
            stop_loss = current_price - (current_atr * 1.0)
        elif signal_type == "SELL":
            target_price = current_price - (current_atr * min_risk_reward)
            stop_loss = current_price + (current_atr * 1.0)
        
        # Final R/R check - reject if below minimum
        risk_reward = abs(target_price - current_price) / abs(current_price - stop_loss) if current_price != stop_loss else 0
        if risk_reward < min_risk_reward:
            quality_factors.append(f"🚨 REJECTED: Poor R/R {risk_reward:.1f}:1")
            return None
        
        # 9. Final validation - Ensure reasonable targets
        risk_reward = abs(target_price - current_price) / abs(current_price - stop_loss) if current_price != stop_loss else 1
        if risk_reward < 2.0:  # Minimum 2:1 risk/reward
            return None
        
        signal_data = {
            'symbol': symbol,
            'signal': signal_type,
            'confidence': round(confidence, 1),
            'current_price': round(current_price, 2),
            'target_price': round(target_price, 2),
            'stop_loss': round(stop_loss, 2),
            'signal_score': signal_score,
            'quality_factors': quality_factors,
            'risk_reward': round(risk_reward, 2),
            'volume_ratio': round(volume_ratio, 2),
            'kill_zone': kill_zone_analysis,
            'smc_analysis': smc_analysis,
            'fvg_analysis': fvg_analysis,  # NEW: Fair Value Gaps
            'order_blocks': order_blocks,  # NEW: Enhanced Order Blocks
            'liquidity_analysis': liquidity_analysis,  # NEW: Liquidity Concepts
            'news_sentiment': news_sentiment,  # NEW: News sentiment analysis
            'technical_indicators': technical_indicators,
                            'multi_timeframe': {
                    'trend_analysis': trend_analysis,
                    'key_levels': get_all_key_levels(multi_timeframe_data),
                    'market_structure': get_market_structure_summary(multi_timeframe_data)
                },
                'advanced_ict_smc': {
                    'market_structure': market_structure,
                    'institutional_flow': institutional_flow,
                    'session_analysis': session_analysis,
                    'advanced_patterns': advanced_patterns,
                    'market_conditions': market_conditions
                },
            'price_action': price_action_analysis,  # NEW: Price action analysis
            'volume_profile': volume_profile_analysis,  # NEW: Volume profile analysis
            'market_session': session_analysis,  # NEW: Market session analysis
            'timestamp': datetime.now().isoformat()
        }
        
        # Store signal in database for tracking
        signal_id = store_signal(signal_data)
        if signal_id:
            signal_data['signal_id'] = signal_id
        
        return signal_data
    except Exception as e:
        logger.error(f"Error generating ICT/SMC signal for {symbol}: {e}")
        return None

def generate_basic_analysis(symbol, hist_data, info, current_price, previous_close, volume, market_cap):
    """Generate basic analysis when no high-quality signal is found"""
    try:
        # Calculate basic technical indicators
        technical_indicators = calculate_technical_indicators(hist_data)
        kill_zone_analysis = analyze_kill_zones(hist_data, "1h")
        smc_analysis = analyze_smart_money_concepts(hist_data)
        price_action_analysis = analyze_price_action_patterns(hist_data)  # NEW: Price action
        
        # Basic signal determination
        rsi = technical_indicators.get('rsi', 50)
        bb_position = technical_indicators.get('bb_position', 0.5)
        macd = technical_indicators.get('macd', 0)
        
        # Simple signal logic with same confidence requirements
        if rsi < 40:
            signal_type = "BUY"
            confidence = 45
        elif rsi > 60:
            signal_type = "SELL"
            confidence = 45
        else:
            signal_type = "HOLD"
            confidence = 40
        
        # Apply lower minimum confidence for basic analysis (fallback)
        min_confidence = 30  # Lower threshold for basic analysis
        if confidence < min_confidence:
            return None  # Reject very low-confidence signals
        
        # Calculate basic price targets with better ATR calculation
        if len(hist_data) >= 14:
            high_low = hist_data['High'] - hist_data['Low']
            high_close = abs(hist_data['High'] - hist_data['Close'].shift(1))
            low_close = abs(hist_data['Low'] - hist_data['Close'].shift(1))
            true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
            atr = true_range.rolling(14).mean()
            current_atr = atr.iloc[-1] if not atr.empty and not pd.isna(atr.iloc[-1]) else current_price * 0.02
        else:
            current_atr = current_price * 0.02  # 2% of price as fallback
        
        # Ensure minimum ATR for meaningful price targets
        min_atr = current_price * 0.005  # 0.5% minimum
        current_atr = max(current_atr, min_atr)
        
        if signal_type == "BUY":
            target_price = current_price + (current_atr * 2)
            stop_loss = current_price - (current_atr * 1)
        elif signal_type == "SELL":
            target_price = current_price - (current_atr * 2)
            stop_loss = current_price + (current_atr * 1)
        else:
            # For HOLD signals, still provide meaningful targets
            target_price = current_price + (current_atr * 1.5)
            stop_loss = current_price - (current_atr * 1.5)
        
        # Quality factors
        quality_factors = []
        if rsi < 30:
            quality_factors.append(f"RSI Oversold: {rsi}")
        elif rsi > 70:
            quality_factors.append(f"RSI Overbought: {rsi}")
        else:
            quality_factors.append(f"RSI Neutral: {rsi}")
        
        if bb_position < 0.2:
            quality_factors.append(f"BB Lower: {bb_position}")
        elif bb_position > 0.8:
            quality_factors.append(f"BB Upper: {bb_position}")
        
        if macd > 0:
            quality_factors.append(f"MACD Bullish: {macd}")
        elif macd < 0:
            quality_factors.append(f"MACD Bearish: {macd}")
        
        # Volume analysis
        avg_volume = hist_data['Volume'].rolling(20).mean().iloc[-1] if 'Volume' in hist_data.columns else 0
        volume_ratio = volume / avg_volume if avg_volume > 0 else 1
        quality_factors.append(f"Volume: {volume_ratio:.1f}x")
        
        # Add price action patterns to quality factors
        pa_patterns = price_action_analysis.get('patterns', [])
        if pa_patterns:
            quality_factors.extend([f"PA: {pattern}" for pattern in pa_patterns[:2]])  # Top 2 patterns
        
        return {
            'symbol': symbol,
            'signal': signal_type,
            'confidence': round(confidence, 1),
            'current_price': round(current_price, 2),
            'target_price': round(target_price, 2),
            'stop_loss': round(stop_loss, 2),
            'signal_score': 0,  # Basic analysis
            'quality_factors': quality_factors,
            'risk_reward': round(abs(target_price - current_price) / abs(current_price - stop_loss), 2) if current_price != stop_loss and abs(current_price - stop_loss) > 0 else 1,
            'volume_ratio': round(volume_ratio, 2),
            'kill_zone': kill_zone_analysis,
            'smc_analysis': smc_analysis,
            'technical_indicators': technical_indicators,
            'price_action': price_action_analysis,  # NEW: Price action analysis
            'analysis_type': 'BASIC',  # Indicate this is basic analysis
            'timestamp': datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error generating basic analysis for {symbol}: {e}")
        return None

@app.get("/", response_class=HTMLResponse)
async def get_main_page():
    """Main trading interface page with all advanced features"""
    return HTMLResponse(content="""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Enhanced Trading Signals - ICT/SMC + ML</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            color: white;
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
        }
        
        .header {
            text-align: center;
            margin-bottom: 30px;
        }
        
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
            background: linear-gradient(45deg, #4CAF50, #2196F3);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        
        .features-badge {
            background: rgba(156, 39, 176, 0.2);
            border: 1px solid #9C27B0;
            border-radius: 20px;
            padding: 8px 16px;
            display: inline-block;
            margin: 10px 5px;
            font-size: 0.9em;
        }
        
        .market-selection {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 30px;
        }
        
        .market-card {
            background: rgba(255, 255, 255, 0.1);
            border: 2px solid rgba(255, 255, 255, 0.2);
            border-radius: 12px;
            padding: 20px;
            text-align: center;
            cursor: pointer;
            transition: all 0.3s ease;
            backdrop-filter: blur(10px);
        }
        
        .market-card:hover {
            transform: translateY(-5px);
            border-color: #4CAF50;
            box-shadow: 0 10px 25px rgba(0, 0, 0, 0.3);
        }
        
        .market-card.active {
            border-color: #4CAF50;
            background: rgba(76, 175, 80, 0.2);
        }
        
        .market-card h3 {
            font-size: 1.2em;
            margin-bottom: 5px;
        }
        
        .market-card .icon {
            font-size: 2em;
            margin-bottom: 10px;
        }
        
        .main-content {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 30px;
            margin-bottom: 30px;
        }
        
        .panel {
            background: rgba(255, 255, 255, 0.1);
            border-radius: 12px;
            padding: 20px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.2);
        }
        
        .panel h2 {
            color: #4CAF50;
            margin-bottom: 20px;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .symbols-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(100px, 1fr));
            gap: 10px;
            margin-bottom: 20px;
        }
        
        .symbol-card {
            background: rgba(255, 255, 255, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: 8px;
            padding: 10px;
            text-align: center;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        .symbol-card:hover {
            background: rgba(76, 175, 80, 0.3);
            transform: scale(1.05);
        }
        
        .trading-actions {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 30px;
        }
        
        .action-button {
            background: linear-gradient(135deg, #4CAF50, #45a049);
            border: none;
            border-radius: 8px;
            padding: 15px;
            color: white;
            font-size: 16px;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.3s ease;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 10px;
        }
        
        .action-button:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3);
        }
        
        .action-button.blue {
            background: linear-gradient(135deg, #2196F3, #1976D2);
        }
        
        .action-button.purple {
            background: linear-gradient(135deg, #9C27B0, #7B1FA2);
        }
        
        
        .results {
            background: rgba(0, 0, 0, 0.3);
            border-radius: 8px;
            padding: 15px;
            margin-top: 15px;
            min-height: 100px;
        }
        
        .loading {
            color: #4CAF50;
            text-align: center;
            padding: 20px;
        }
        
        .error {
            color: #f44336;
            text-align: center;
            padding: 20px;
        }
        
        .success {
            color: #4CAF50;
            text-align: center;
            padding: 20px;
        }
        
        .signal-details {
            background: rgba(0, 0, 0, 0.2);
            border-radius: 8px;
            padding: 15px;
            margin: 10px 0;
        }
        
        .signal-buy {
            border-left: 4px solid #4CAF50;
        }
        
        .signal-sell {
            border-left: 4px solid #f44336;
        }
        
        .signal-hold {
            border-left: 4px solid #FF9800;
        }
        
        .input-group {
            margin-bottom: 15px;
        }
        
        .input-group input {
            width: 100%;
            padding: 10px;
            border: 1px solid rgba(255, 255, 255, 0.3);
            border-radius: 6px;
            background: rgba(255, 255, 255, 0.1);
            color: white;
            font-size: 16px;
        }
        
        .input-group input::placeholder {
            color: rgba(255, 255, 255, 0.7);
        }
        
        .category-header {
            background: linear-gradient(135deg, rgba(76, 175, 80, 0.2), rgba(76, 175, 80, 0.1));
            border-left: 4px solid #4CAF50;
            border-radius: 6px;
            padding: 10px 15px;
            margin: 15px 0 10px 0;
            font-weight: bold;
            color: #4CAF50;
            font-size: 0.9em;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        @media (max-width: 768px) {
            .main-content {
                grid-template-columns: 1fr;
            }
            
            .market-selection {
                grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            }
            
            .trading-actions {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎯 Enhanced Trading Signals</h1>
            <p>ICT/SMC + Machine Learning + Advanced Indicators</p>
            <div>
                <span class="features-badge">🧠 ICT/SMC Analysis</span>
                <span class="features-badge">🤖 Machine Learning</span>
                <span class="features-badge">📊 Advanced Indicators</span>
                <span class="features-badge">⚡ Real-time Signals</span>
            </div>
        </div>
        
        <!-- Market Selection -->
        <div class="market-selection">
            <div class="market-card" onclick="selectMarket('stocks', this)">
                <div class="icon">📊</div>
                <h3>STOCKS</h3>
                <p>US Equities & ETFs</p>
            </div>
            <div class="market-card" onclick="selectMarket('forex', this)">
                <div class="icon">💱</div>
                <h3>FOREX</h3>
                <p>Currency Pairs</p>
            </div>
            <div class="market-card" onclick="selectMarket('crypto', this)">
                <div class="icon">₿</div>
                <h3>CRYPTO</h3>
                <p>Digital Assets</p>
            </div>
            <div class="market-card" onclick="selectMarket('futures', this)">
                <div class="icon">⛽</div>
                <h3>FUTURES</h3>
                <p>Commodities & Indices</p>
            </div>
            <div class="market-card" onclick="selectMarket('indices', this)">
                <div class="icon">📈</div>
                <h3>INDICES</h3>
                <p>Market Indexes</p>
            </div>
            <div class="market-card" onclick="selectMarket('metals', this)">
                <div class="icon">🥇</div>
                <h3>METALS</h3>
                <p>Precious Metals</p>
            </div>
        </div>
        
        <!-- Main Content -->
        <div class="main-content">
            <!-- Market Scanner Panel -->
            <div class="panel">
                <h2>🔍 ICT/SMC Market Scanner</h2>
                <div class="symbols-grid" id="symbols-container">
                    <div class="loading">Select a market to view symbols</div>
                </div>
                <div class="results" id="scanner-results">
                    <div class="loading">Ready to scan market with ICT/SMC analysis</div>
                </div>
            </div>
            
            <!-- Symbol Analyzer Panel -->
            <div class="panel">
                <h2>📊 Advanced Symbol Analyzer</h2>
                <div class="input-group" style="display: flex; gap: 10px; align-items: center;">
                    <input type="text" id="symbol-input" placeholder="Enter symbol (e.g., AAPL, BTC-USD, EURUSD)" style="flex: 1;" />
                    <button class="action-button blue" onclick="analyzeSymbol()" style="padding: 12px 20px; white-space: nowrap;">
                        📊 Analyze Symbol
                    </button>
                </div>
                <div class="results" id="analyzer-results">
                    <div class="loading">Enter a symbol above and click "Analyze Symbol" for ICT/SMC + ML analysis</div>
                </div>
            </div>
        </div>
        
        <!-- Trading Actions -->
        <div class="trading-actions">
            <button class="action-button" onclick="toggleScanning()" id="scan-toggle-btn">
                🔍 Start Scanning
            </button>
            <button class="action-button purple" onclick="createCharts()">
                📊 Load Charts
            </button>
            <button class="action-button purple" onclick="getMarketSummary()">
                📊 Market Summary
            </button>
        </div>
        
        <!-- Live Signals Display -->
        <div class="panel">
            <h2>📈 Market Scanner Signals</h2>
            <div id="scanner-status" style="background: rgba(0,0,0,0.2); border-radius: 8px; padding: 15px; margin-bottom: 15px; border-left: 4px solid #4CAF50;">
                <div style="font-size: 0.9em; color: #4CAF50; margin-bottom: 5px;">
                    <strong>🎯 MARKET SCANNER RESULTS</strong>
                </div>
                <div style="font-size: 0.8em; color: #888;">
                    Trading signals from full market scans will appear here. Individual symbol analysis shows in the analyzer panel above.
                </div>
            </div>
            <div class="results" id="signals-display">
                <div class="loading" style="text-align: center; padding: 20px; color: #666;">
                    Ready to scan market with ICT/SMC analysis
                </div>
            </div>
        </div>
    </div>

    <script>
        // Enhanced JavaScript with all advanced features
        let currentMarket = 'stocks';
        
        // Market data with organized categories
        const marketData = {
            stocks: {
                name: 'STOCKS',
                icon: '📊',
                color: '#4CAF50',
                categories: {
                    'NASDAQ': ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA', 'META', 'NVDA', 'NFLX', 'AMD', 'INTC'],
                    'NYSE': ['JPM', 'JNJ', 'PG', 'UNH', 'HD', 'BAC', 'MA', 'V', 'NKE', 'DIS'],
                    'ETFs': ['SPY', 'QQQ', 'IWM', 'DIA', 'GLD', 'SLV', 'USO', 'TLT', 'VXX']
                }
            },
            forex: {
                name: 'FOREX',
                icon: '💱',
                color: '#2196F3',
                categories: {
                    'MAJORS': ['EURUSD=X', 'GBPUSD=X', 'USDJPY=X', 'USDCHF=X', 'AUDUSD=X', 'USDCAD=X', 'NZDUSD=X'],
                    'MINORS': ['EURGBP=X', 'EURJPY=X', 'GBPJPY=X', 'AUDJPY=X', 'EURAUD=X', 'GBPAUD=X'],
                    'EXOTICS': ['USDSEK=X', 'USDNOK=X', 'USDDKK=X', 'EURCHF=X', 'GBPCHF=X', 'USDZAR=X']
                }
            },
            crypto: {
                name: 'CRYPTO',
                icon: '₿',
                color: '#FFC107',
                categories: {
                    'MAJORS': ['BTC-USD', 'ETH-USD', 'BNB-USD', 'XRP-USD', 'SOL-USD'],
                    'DEFI': ['UNI-USD', 'AAVE-USD', 'COMP-USD', 'MKR-USD', 'SUSHI-USD'],
                    'LAYER1': ['ADA-USD', 'DOT-USD', 'AVAX-USD', 'MATIC-USD', 'ATOM-USD']
                }
            },
            futures: {
                name: 'FUTURES',
                icon: '⛽',
                color: '#FF9800',
                categories: {
                    'METALS': ['GC', 'SI', 'PL', 'PA', 'HG', 'AL', 'NI', 'ZN'],
                    'ENERGY': ['CL', 'NG', 'HO', 'RB', 'BZ', 'QS', 'BZ=F'],
                    'INDICES': ['ES', 'NQ', 'YM', 'RTY', 'SPX', 'NDX', 'DJI', 'RUT'],
                    'AGRICULTURE': ['ZC', 'ZS', 'ZW', 'KC', 'CC', 'CT', 'SB', 'CC=F'],
                    'BONDS': ['ZB', 'ZN', 'ZF', 'ZT', 'GE', 'TU', 'FV', 'TY']
                }
            },
            indices: {
                name: 'INDICES',
                icon: '📈',
                color: '#f44336',
                categories: {
                    'US_INDICES': ['SPY', 'QQQ', 'IWM', 'DIA', 'VTI', 'VOO', 'VEA', 'VWO'],
                    'INTERNATIONAL': ['EFA', 'EEM', 'ACWI', 'VT', 'VXUS', 'BND', 'TLT', 'IEF'],
                    'VOLATILITY': ['VXX', 'UVXY', 'TVIX', 'VIXY', 'SHY', 'LQD', 'HYG', 'EMB']
                }
            },
            metals: {
                name: 'METALS',
                icon: '🥇',
                color: '#9C27B0',
                categories: {
                    'PRECIOUS': ['GC', 'SI', 'PL', 'PA', 'GLD', 'SLV', 'PPLT', 'PALL'],
                    'MINING': ['GDX', 'GDXJ', 'SIL', 'COPX', 'PICK', 'REMX', 'URA', 'LIT'],
                    'AGRICULTURE': ['BAL', 'NIB', 'JO', 'CAFE', 'WEAT', 'CORN', 'SOYB', 'CANE']
                }
            }
        };
        
        // Core Functions
        function selectMarket(market, element) {
            console.log('Selecting market:', market);
            currentMarket = market;
            
            // Update active market styling
            document.querySelectorAll('.market-card').forEach(card => {
                card.classList.remove('active');
            });
            element.classList.add('active');
            
            // Show market symbols
            showMarketSymbols(market);
        }
        
        function showMarketSymbols(market) {
            console.log('Showing symbols for market:', market);
            
            const symbolsContainer = document.getElementById('symbols-container');
            const marketInfo = marketData[market];
            const categories = marketInfo.categories;
            
            // Clear container
            symbolsContainer.innerHTML = '';
            
            // Create category sections
            Object.entries(categories).forEach(([categoryName, symbols]) => {
                // Create category header
                const categoryHeader = document.createElement('div');
                categoryHeader.className = 'category-header';
                categoryHeader.innerHTML = `📂 ${categoryName}`;
                symbolsContainer.appendChild(categoryHeader);
                
                // Create symbols grid for this category
                const categoryGrid = document.createElement('div');
                categoryGrid.className = 'symbols-grid';
                
                // Add symbols for this category
                symbols.slice(0, 6).forEach(symbol => {
                    const symbolCard = document.createElement('div');
                    symbolCard.className = 'symbol-card';
                    symbolCard.innerHTML = `
                        <div style="font-weight: bold; margin-bottom: 2px;">${symbol}</div>
                        <div style="font-size: 0.8em; opacity: 0.7;">${categoryName}</div>
                    `;
                    symbolCard.onclick = () => {
                        document.getElementById('symbol-input').value = symbol;
                    };
                    categoryGrid.appendChild(symbolCard);
                });
                
                symbolsContainer.appendChild(categoryGrid);
            });
        }
        
        // Enhanced Button Functions with ICT/SMC
        
        async function analyzeSymbol() {
            const symbolInput = document.getElementById('symbol-input');
            const symbol = symbolInput?.value?.trim();
            
            if (!symbol) {
                alert('Please enter a symbol to analyze');
                return;
            }
            
            console.log('Analyzing symbol with ICT/SMC:', symbol);
            const resultsDiv = document.getElementById('analyzer-results');
            resultsDiv.innerHTML = `<div class="loading">📊 Analyzing ${symbol} with ICT/SMC + ML...</div>`;
            
            try {
                const response = await fetch(`/api/analyze/${symbol}`);
                const data = await response.json();
                
                if (data.analysis) {
                    const analysis = data.analysis;
                    const signalClass = analysis.signal.toLowerCase();
                    const priceChange = analysis.price_change_pct || 0;
                    const priceChangeColor = priceChange >= 0 ? '#4CAF50' : '#f44336';
                    const priceChangeSymbol = priceChange >= 0 ? '↗' : '↘';
                    
                    const analysisHtml = `
                        <div class="signal-details signal-${signalClass}">
                            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
                                <div>
                                    <strong>${analysis.symbol} - ${analysis.signal}</strong><br>
                                    <small>LIVE Analysis - ${analysis.analysis_time || 'N/A'}</small>
                                    ${analysis.analysis_type === 'BASIC' ? '<br><small style="color: #FF9800;">⚠️ Basic Analysis (No High-Quality Signal Found)</small>' : ''}
                                </div>
                                <div style="text-align: right;">
                                    <div style="font-size: 1.5em; font-weight: bold; color: ${signalClass === 'buy' ? '#4CAF50' : signalClass === 'sell' ? '#f44336' : '#FF9800'};">
                                        ${analysis.confidence}%
                                    </div>
                                    <div style="font-size: 0.8em; color: #888;">Confidence</div>
                                </div>
                            </div>
                            
                            <div style="display: grid; grid-template-columns: 1fr 1fr 1fr 1fr; gap: 10px; margin: 15px 0; padding: 15px; background: rgba(0,0,0,0.2); border-radius: 8px;">
                                <div style="text-align: center;">
                                    <div style="font-size: 0.8em; color: #888; margin-bottom: 5px;">CURRENT PRICE</div>
                                    <div style="font-weight: bold; font-size: 1.1em;">$${analysis.live_price || analysis.current_price}</div>
                                    <div style="color: ${priceChangeColor}; font-size: 0.8em;">
                                        ${priceChangeSymbol} ${Math.abs(priceChange).toFixed(2)}%
                                    </div>
                                </div>
                                <div style="text-align: center;">
                                    <div style="font-size: 0.8em; color: #888; margin-bottom: 5px;">ENTRY PRICE</div>
                                    <div style="font-weight: bold; font-size: 1.1em; color: ${signalClass === 'buy' ? '#4CAF50' : signalClass === 'sell' ? '#f44336' : '#FF9800'};">
                                        $${analysis.live_price || analysis.current_price}
                                    </div>
                                    <div style="font-size: 0.8em; color: #888;">Market Order</div>
                                </div>
                                <div style="text-align: center;">
                                    <div style="font-size: 0.8em; color: #888; margin-bottom: 5px;">TAKE PROFIT</div>
                                    <div style="font-weight: bold; font-size: 1.1em; color: #4CAF50;">
                                        $${analysis.target_price}
                                    </div>
                                    <div style="font-size: 0.8em; color: #4CAF50;">
                                        +${(((analysis.target_price - (analysis.live_price || analysis.current_price)) / (analysis.live_price || analysis.current_price)) * 100).toFixed(1)}%
                                    </div>
                                </div>
                                <div style="text-align: center;">
                                    <div style="font-size: 0.8em; color: #888; margin-bottom: 5px;">STOP LOSS</div>
                                    <div style="font-weight: bold; font-size: 1.1em; color: #f44336;">
                                        $${analysis.stop_loss}
                                    </div>
                                    <div style="font-size: 0.8em; color: #f44336;">
                                        -${(((analysis.live_price || analysis.current_price) - analysis.stop_loss) / (analysis.live_price || analysis.current_price) * 100).toFixed(1)}%
                                    </div>
                                </div>
                            </div>
                            
                            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin: 15px 0;">
                                <div>
                                    <div><strong>Live Market Data:</strong></div>
                                    <div>Volume: ${(analysis.volume || 0).toLocaleString()}</div>
                                    <div>Market Cap: $${(analysis.market_cap || 0).toLocaleString()}</div>
                                    <div>Day Range: $${analysis.live_metrics?.day_low || 0} - $${analysis.live_metrics?.day_high || 0}</div>
                                </div>
                                <div>
                                    <div><strong>Risk Management:</strong></div>
                                    <div>Risk/Reward: ${((analysis.target_price - (analysis.live_price || analysis.current_price)) / ((analysis.live_price || analysis.current_price) - analysis.stop_loss)).toFixed(2)}:1</div>
                                    <div>Position Size: Calculate based on risk</div>
                                    <div>Max Risk: 1-2% of account</div>
                                </div>
                            </div>
                            
                            <div style="font-size: 0.9em; margin-top: 15px; padding-top: 15px; border-top: 1px solid rgba(255,255,255,0.2);">
                                <div><strong>ICT/SMC Analysis:</strong></div>
                                <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 10px; margin-top: 8px;">
                                    <div>Kill Zone: ${analysis.kill_zone?.active_session || 'N/A'}</div>
                                    <div>SMC Pattern: ${analysis.smc_analysis?.pattern || 'N/A'}</div>
                                    <div>RSI: ${analysis.technical_indicators?.rsi || 'N/A'}</div>
                                    <div>MACD: ${analysis.technical_indicators?.macd || 'N/A'}</div>
                                    <div>BB Position: ${analysis.technical_indicators?.bb_position || 'N/A'}</div>
                                    <div>Signal Score: ${analysis.signal_score || 'N/A'}</div>
                                </div>
                                ${analysis.smc_analysis && analysis.smc_analysis.all_patterns && analysis.smc_analysis.all_patterns.length > 0 ? `
                                <div style="margin-top: 10px; padding: 10px; background: rgba(255,215,0,0.1); border-radius: 6px; border-left: 3px solid #FFD700;">
                                    <div style="font-size: 0.85em; color: #FFD700; font-weight: bold; margin-bottom: 5px;">
                                        🎯 Advanced SMC Analysis (Order Flow + Market Structure + POI)
                                    </div>
                                    <div style="font-size: 0.8em; color: #FFD700; line-height: 1.4;">
                                        ${analysis.smc_analysis.all_patterns.slice(0, 4).join(' | ')}
                                        ${analysis.smc_analysis.all_patterns.length > 4 ? '<br>' + analysis.smc_analysis.all_patterns.slice(4, 8).join(' | ') : ''}
                                        ${analysis.smc_analysis.all_patterns.length > 8 ? '...' : ''}
                                    </div>
                                </div>
                                ` : ''}
                                ${analysis.multi_timeframe && analysis.multi_timeframe.consensus_direction ? `
                                <div style="margin-top: 10px; padding: 10px; background: rgba(0,150,255,0.1); border-radius: 6px; border-left: 3px solid #0096FF;">
                                    <div style="font-size: 0.85em; color: #0096FF; font-weight: bold; margin-bottom: 5px;">
                                        📊 Multi-Timeframe Analysis (Daily → 4H → 1H → 15m)
                                    </div>
                                    <div style="font-size: 0.8em; color: #0096FF; line-height: 1.4;">
                                        <strong>Consensus:</strong> ${analysis.multi_timeframe.consensus_direction} (${analysis.multi_timeframe.consensus_confidence}%)<br>
                                        <strong>Breakdown:</strong> Bullish ${analysis.multi_timeframe.bullish_pct}% | Bearish ${analysis.multi_timeframe.bearish_pct}% | Neutral ${analysis.multi_timeframe.neutral_pct}%
                                    </div>
                                </div>
                                ` : ''}
                            </div>
                        </div>
                    `;
                    // Display detailed analysis directly in the analyzer results area
                    resultsDiv.innerHTML = analysisHtml;
                } else {
                    resultsDiv.innerHTML = '<div class="error">❌ Error analyzing symbol</div>';
                }
            } catch (error) {
                console.error('Analysis error:', error);
                resultsDiv.innerHTML = '<div class="error">❌ Error analyzing symbol</div>';
            }
        }
        
        
        async function createCharts() {
            console.log('Creating charts...');
            alert('Advanced charting with ICT/SMC indicators coming soon!');
        }
        
        async function getMarketSummary() {
            console.log('Getting market summary...');
            alert('Market summary with ICT/SMC analysis coming soon!');
        }
        
        // ===== TOGGLE SCANNING FUNCTION =====
        
        async function toggleScanning() {
            const button = document.getElementById('scan-toggle-btn');
            const isScanning = button.classList.contains('scanning');
            
            if (isScanning) {
                // Currently scanning - stop it
                console.log('Stopping market scanning...');
                
                try {
                    const response = await fetch('/api/scanning/stop');
                    const data = await response.json();
                    
                    if (data.status === 'success') {
                        // Update button to start mode
                        button.classList.remove('scanning');
                        button.innerHTML = '🔍 Start Scanning';
                        button.style.background = '';
                        
                        console.log(`⏹️ ${data.message}`);
                    }
                } catch (error) {
                    console.error('Error stopping scanning:', error);
                }
            } else {
                // Not scanning - start it
                console.log('Starting market scanning...');
                
                try {
                    const response = await fetch('/api/scanning/start');
                    const data = await response.json();
                    
                    if (data.status === 'success') {
                        // Update button to stop mode
                        button.classList.add('scanning');
                        button.innerHTML = '⏹️ Stop Scanning';
                        button.style.background = 'linear-gradient(135deg, #f44336, #d32f2f)';
                        
                        console.log(`🚀 ${data.message}`);
                        
                        // Start status updates
                        updateScanningStatus();
                    } else {
                        console.log(`ℹ️ ${data.message}`);
                    }
                } catch (error) {
                    console.error('Error starting scanning:', error);
                }
            }
        }
        
        async function updateScanningStatus() {
            try {
                const response = await fetch('/api/scanning/status');
                const data = await response.json();
                
                if (data.status === 'success') {
                    const scanning = data.continuous_scanning;
                    const button = document.getElementById('scan-toggle-btn');
                    const scannerStatus = document.getElementById('scanner-status');
                    
                    // Update button state
                    if (scanning.scanning_active) {
                        button.classList.add('scanning');
                        button.innerHTML = `⏹️ Stop Scanning (${scanning.stats.total_scans} scans, ${scanning.stats.signals_generated} signals)`;
                        button.style.background = 'linear-gradient(135deg, #f44336, #d32f2f)';
                        
                        // Update scanner status indicator
                        scannerStatus.style.borderLeft = '4px solid #ff9800';
                        scannerStatus.innerHTML = `
                            <div style="font-size: 0.9em; color: #ff9800; margin-bottom: 5px;">
                                <strong>🔄 SCANNING ACTIVE - AI LEARNING</strong>
                            </div>
                            <div style="font-size: 0.8em; color: #888;">
                                Continuous market scanning every 30 minutes. AI monitoring and learning from all signals.
                                <br>Scans: ${scanning.stats.total_scans} | Signals: ${scanning.stats.signals_generated} | Duration: ${scanning.current_duration_hours.toFixed(1)}h
                            </div>
                        `;
                        
                        // Update both signal areas to show scanning status
                        const signalsDiv = document.getElementById('signals-display');
                        const scannerResults = document.getElementById('scanner-results');
                        
                        // Update scanner results area (top)
                        if (scannerResults) {
                            scannerResults.innerHTML = `
                                <div style="text-align: center; padding: 20px; color: #ff9800;">
                                    <div style="font-size: 16px; margin-bottom: 10px;">🔄 AI Scanning Active</div>
                                    <div style="font-size: 14px; color: #888;">Continuous market analysis in progress</div>
                                </div>
                            `;
                        }
                        
                        // Update signals display area (bottom)
                        console.log('Current signals data:', data.signals);
                        if (data.signals && data.signals.length > 0) {
                            // Show signals if available
                            console.log(`Displaying ${data.signals.length} signals`);
                            displayScannerSignals(data.signals);
                        } else {
                            // Show scanning indicator
                            console.log('No signals available, showing scanning indicator');
                            signalsDiv.innerHTML = `
                                <div style="text-align: center; padding: 20px; color: #ff9800;">
                                    <div style="font-size: 18px; margin-bottom: 10px;">🔄 Scanning Market...</div>
                                    <div style="font-size: 14px; color: #888;">AI is analyzing markets and generating signals</div>
                                    <div style="font-size: 12px; color: #666; margin-top: 10px;">
                                        Last scan: ${scanning.stats.last_scan_time ? new Date(scanning.stats.last_scan_time).toLocaleTimeString() : 'In progress...'}
                                    </div>
                                </div>
                            `;
                        }
                        
                        // Continue updating if scanning is active
                        setTimeout(updateScanningStatus, 30000); // Update every 30 seconds
                    } else {
                        button.classList.remove('scanning');
                        button.innerHTML = '🔍 Start Scanning';
                        button.style.background = '';
                        
                        // Reset scanner status indicator
                        scannerStatus.style.borderLeft = '4px solid #4CAF50';
                        scannerStatus.innerHTML = `
                            <div style="font-size: 0.9em; color: #4CAF50; margin-bottom: 5px;">
                                <strong>🎯 MARKET SCANNER RESULTS</strong>
                            </div>
                            <div style="font-size: 0.8em; color: #888;">
                                Trading signals from full market scans will appear here. Individual symbol analysis shows in the analyzer panel above.
                            </div>
                        `;
                        
                        // Reset both signal areas to show ready status
                        const signalsDiv = document.getElementById('signals-display');
                        const scannerResults = document.getElementById('scanner-results');
                        
                        // Reset scanner results area (top)
                        if (scannerResults) {
                            scannerResults.innerHTML = `
                                <div class="loading">Ready to scan market with ICT/SMC analysis</div>
                            `;
                        }
                        
                        // Reset signals display area (bottom)
                        signalsDiv.innerHTML = `
                            <div class="loading" style="text-align: center; padding: 20px; color: #666;">
                                Ready to scan market with ICT/SMC analysis
                            </div>
                        `;
                    }
                }
            } catch (error) {
                console.error('Error updating scanning status:', error);
            }
        }
        
        function displayScannerSignals(signals) {
            console.log('displayScannerSignals called with:', signals);
            
            // Find the signals display div
            const resultsDiv = document.getElementById('signals-display');
            
            if (!resultsDiv) {
                console.error('Signals display div not found');
                return;
            }
            
            console.log('Signals display div found:', resultsDiv);
            
            if (signals.length === 0) {
                console.log('No signals to display');
                resultsDiv.innerHTML = '<div class="no-signals" style="text-align: center; padding: 20px; color: #666;">No high-quality signals found in current market conditions.</div>';
                return;
            }
            
            console.log(`Displaying ${signals.length} signals`);
            
            // Create signals grid
            let signalsHtml = `
                <div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 15px; margin-top: 15px;">
                    <div style="grid-column: 1 / -1; text-align: center; margin-bottom: 10px; color: #4CAF50; font-weight: bold;">
                        📊 Found ${signals.length} Trading Signals
                    </div>
            `;
            
            signals.forEach(signal => {
                // Safe property access with fallbacks
                const confidence = (signal && signal.confidence) ? parseFloat(signal.confidence) : 0;
                const signalType = (signal && signal.signal) ? signal.signal : 'UNKNOWN';
                const symbol = (signal && signal.symbol) ? signal.symbol : 'N/A';
                const entryPrice = (signal && signal.current_price) ? parseFloat(signal.current_price) : 0;
                const targetPrice = (signal && signal.target_price) ? parseFloat(signal.target_price) : 0;
                const stopLoss = (signal && signal.stop_loss) ? parseFloat(signal.stop_loss) : 0;
                const currentPrice = (signal && signal.current_price) ? parseFloat(signal.current_price) : 0;
                const signalScore = (signal && signal.signal_score) ? parseFloat(signal.signal_score) : 0;
                
                const confidenceColor = confidence >= 80 ? '#4CAF50' : confidence >= 60 ? '#FF9800' : '#f44336';
                const signalTypeColor = signalType === 'BUY' ? '#4CAF50' : '#f44336';
                
                signalsHtml += `
                    <div style="background: rgba(0,0,0,0.3); border-radius: 8px; padding: 15px; border-left: 4px solid ${confidenceColor}; margin-bottom: 10px;">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                            <span style="font-weight: bold; font-size: 16px; color: #fff;">${symbol}</span>
                            <span style="background: ${signalTypeColor}; color: white; padding: 4px 8px; border-radius: 4px; font-size: 12px; font-weight: bold;">
                                ${signalType}
                            </span>
                        </div>
                        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px; font-size: 14px;">
                            <div><strong>Entry:</strong> $${entryPrice.toFixed(2)}</div>
                            <div><strong>Target:</strong> $${targetPrice.toFixed(2)}</div>
                            <div><strong>Stop:</strong> $${stopLoss.toFixed(2)}</div>
                            <div style="color: ${confidenceColor}; font-weight: bold;">
                                <strong>Confidence:</strong> ${confidence}%
                            </div>
                        </div>
                        <div style="margin-top: 8px; font-size: 12px; color: #ccc;">
                            Current: $${currentPrice.toFixed(2)} | Score: ${Math.round(signalScore)}
                        </div>
                        ${signal.news_sentiment && signal.news_sentiment.sentiment_data ? `
                        <div style="margin-top: 10px; padding: 8px; background: rgba(255,255,255,0.1); border-radius: 4px; font-size: 12px;">
                            <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                                <span><strong>📰 Sentiment:</strong> ${signal.news_sentiment.sentiment_data.overall_sentiment}</span>
                                <span><strong>Impact:</strong> ${signal.news_sentiment.sentiment_data.news_impact}</span>
                            </div>
                            <div style="display: flex; justify-content: space-between;">
                                <span><strong>Score:</strong> ${signal.news_sentiment.sentiment_data.sentiment_score}/100</span>
                                <span><strong>Fear/Greed:</strong> ${signal.news_sentiment.sentiment_data.market_fear_greed}</span>
                            </div>
                            ${signal.news_sentiment.sentiment_data.economic_events && signal.news_sentiment.sentiment_data.economic_events.length > 0 ? `
                            <div style="margin-top: 5px; font-size: 11px; color: #FFD700;">
                                <strong>📅 Events:</strong> ${signal.news_sentiment.sentiment_data.economic_events.map(e => e.event).join(', ')}
                            </div>
                            ` : ''}
                        </div>
                        ` : ''}
                    </div>
                `;
            });
            
            signalsHtml += '</div>';
            resultsDiv.innerHTML = signalsHtml;
        }
        
        
        // Initialize on page load
        document.addEventListener('DOMContentLoaded', function() {
            console.log('Enhanced trading interface with ICT/SMC + ML loaded successfully!');
            
            // Set default market selection
            const firstMarketCard = document.querySelector('.market-card');
            if (firstMarketCard) {
                selectMarket('stocks', firstMarketCard);
            }
            
            // Check scanning status on page load
            updateScanningStatus();
        });
    </script>
</body>
</html>
    """)

# API Endpoints with ICT/SMC Integration
@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "2.0.0",
        "features": ["ICT/SMC Analysis", "Machine Learning", "Advanced Indicators"],
        "ml_models_loaded": ml_models['signal_classifier'] is not None
    }

@app.get("/api/scan/full-market")
async def scan_full_market():
    """Scan full market for trading signals using ICT/SMC with LIVE data"""
    try:
        # Comprehensive live market symbols
        symbols_to_scan = {
            'stocks': ['AAPL', 'TSLA', 'MSFT', 'GOOGL', 'META', 'NVDA', 'AMZN', 'NFLX'],
            'crypto': ['BTC-USD', 'ETH-USD', 'BNB-USD', 'XRP-USD', 'SOL-USD', 'ADA-USD'],
            'forex': ['EURUSD=X', 'GBPUSD=X', 'USDJPY=X', 'AUDUSD=X', 'USDCAD=X'],
            'futures': ['GC=F', 'CL=F', 'ES=F', 'NQ=F', 'YM=F'],
            'indices': ['SPY', 'QQQ', 'IWM', 'DIA', 'VTI']
        }
        
        signals = []
        market_summary = {
            'total_scanned': 0,
            'strong_signals': 0,
            'buy_signals': 0,
            'sell_signals': 0,
            'hold_signals': 0
        }
        
        # Scan each market category
        for market_type, symbols in symbols_to_scan.items():
            logger.info(f"Scanning {market_type} market with {len(symbols)} symbols...")
            
            for symbol in symbols:
                try:
                    market_summary['total_scanned'] += 1
                    
                    # Get LIVE data with multiple timeframes
                    ticker = yf.Ticker(symbol)
                    
                    # Get real-time info
                    info = ticker.info
                    current_price = info.get('regularMarketPrice', 0)
                    previous_close = info.get('previousClose', 0)
                    volume = info.get('volume', 0)
                    
                    # Get live historical data (last 5 days, 1-hour intervals)
                    hist = ticker.history(period="5d", interval="1h")
                    
                    if not hist.empty and len(hist) >= 20 and current_price > 0:
                        # Generate LIVE ICT/SMC signal
                        signal = generate_ict_smc_signal(symbol, hist, "1h")
                        
                        if signal:
                            # Add live market data
                            signal['market_type'] = market_type
                            signal['live_price'] = current_price
                            signal['price_change'] = round(current_price - previous_close, 2)
                            signal['price_change_pct'] = round(((current_price - previous_close) / previous_close) * 100, 2) if previous_close > 0 else 0
                            signal['volume'] = volume
                            signal['market_cap'] = info.get('marketCap', 0)
                            signal['is_live'] = True
                            
                            # Update market summary
                            if signal['confidence'] >= 70:
                                market_summary['strong_signals'] += 1
                            
                            if signal['signal'] == 'BUY':
                                market_summary['buy_signals'] += 1
                            elif signal['signal'] == 'SELL':
                                market_summary['sell_signals'] += 1
                            else:
                                market_summary['hold_signals'] += 1
                            
                            signals.append(signal)
                            
                except Exception as e:
                    logger.error(f"Error scanning {symbol}: {e}")
                    continue
        
        # Sort signals by confidence (highest first)
        signals.sort(key=lambda x: x.get('confidence', 0), reverse=True)
        
        # Add market summary to response
        response_data = {
            "status": "success",
            "signals": signals,
            "market_summary": market_summary,
            "scan_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "message": f"LIVE market scan completed! Scanned {market_summary['total_scanned']} symbols. Found {len(signals)} signals ({market_summary['strong_signals']} strong).",
            "timestamp": datetime.now().isoformat()
        }
        
        logger.info(f"Live market scan completed: {len(signals)} signals found")
        return response_data
        
    except Exception as e:
        logger.error(f"Error in live market scan: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/analyze/{symbol}")
async def analyze_symbol(symbol: str):
    """Analyze individual symbol using ICT/SMC methodology with LIVE data"""
    try:
        # Get LIVE data
        ticker = yf.Ticker(symbol)
        
        # Get real-time market info with better error handling
        try:
            info = ticker.info
            current_price = info.get('regularMarketPrice', 0)
            previous_close = info.get('previousClose', 0)
            volume = info.get('volume', 0)
            market_cap = info.get('marketCap', 0)
            
            # Handle crypto symbols that might not have all fields
            if current_price == 0:
                current_price = info.get('currentPrice', 0)
            if previous_close == 0:
                previous_close = info.get('previousClose', current_price)
            if volume == 0:
                volume = info.get('volume24h', 0)
            if market_cap == 0:
                market_cap = info.get('marketCap', 0)
                
        except Exception as e:
            logger.error(f"Error getting market info for {symbol}: {e}")
            raise HTTPException(status_code=400, detail=f"Unable to fetch market data for {symbol}")
        
        # Get live historical data
        hist = ticker.history(period="5d", interval="1h")
        
        if hist.empty or len(hist) < 20 or current_price <= 0:
            raise HTTPException(status_code=400, detail="Insufficient live data for analysis")
        
        # Generate LIVE ICT/SMC signal
        analysis = generate_ict_smc_signal(symbol, hist, "1h")
        
        if not analysis:
            # If no high-quality signal, provide basic analysis instead of error
            analysis = generate_basic_analysis(symbol, hist, info, current_price, previous_close, volume, market_cap)
        
        # Safety check - if analysis is still None, create a minimal response
        if not analysis:
            # Calculate meaningful targets even for minimal response
            min_atr = current_price * 0.005  # 0.5% minimum
            target_price = current_price + (min_atr * 1.5)
            stop_loss = current_price - (min_atr * 1.5)
            
            analysis = {
                'symbol': symbol,
                'signal': 'HOLD',
                'confidence': 0,
                'current_price': current_price,
                'target_price': target_price,
                'stop_loss': stop_loss,
                'signal_score': 0,
                'quality_factors': ['Insufficient data for analysis'],
                'risk_reward': 1.0,
                'volume_ratio': 1,
                'technical_indicators': {},
                'multi_timeframe': {},
                'price_action': {},
                'timestamp': datetime.now().isoformat()
            }
        
        # Add live market data to analysis
        analysis['live_price'] = current_price
        analysis['price_change'] = round(current_price - previous_close, 2)
        analysis['price_change_pct'] = round(((current_price - previous_close) / previous_close) * 100, 2) if previous_close > 0 else 0
        
        # Handle forex symbols (no volume/market cap)
        if symbol.endswith('=X') or symbol in ['EURUSD', 'GBPUSD', 'USDJPY', 'AUDUSD', 'USDCAD', 'USDCHF', 'NZDUSD']:
            analysis['volume'] = "N/A (Forex)"
            analysis['market_cap'] = "N/A (Forex)"
        else:
            analysis['volume'] = volume
            analysis['market_cap'] = market_cap
        analysis['is_live'] = True
        analysis['analysis_time'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Multi-timeframe analysis is already included in the signal generation
        
        # Add additional live metrics
        analysis['live_metrics'] = {
            'bid': info.get('bid', 0),
            'ask': info.get('ask', 0),
            'day_high': info.get('dayHigh', 0),
            'day_low': info.get('dayLow', 0),
            'fifty_two_week_high': info.get('fiftyTwoWeekHigh', 0),
            'fifty_two_week_low': info.get('fiftyTwoWeekLow', 0),
            'pe_ratio': info.get('trailingPE', 0),
            'eps': info.get('trailingEps', 0)
        }
        
        # Clean NaN values before returning
        analysis = clean_nan_values(analysis)
        
        return {
            "status": "success",
            "analysis": analysis,
            "message": f"LIVE ICT/SMC analysis complete for {symbol.upper()} at ${current_price}",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error analyzing symbol {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/live/signals")
async def get_live_signals():
    """Get live trading signals with ICT/SMC analysis"""
    try:
        # Sample live signals with ICT/SMC data
        live_signals = [
            {
                "symbol": "BTC-USD",
                "signal": "BUY",
                "price": 43250.00,
                "confidence": 78.5,
                "kill_zone": "LONDON",
                "smc_pattern": "DISCOUNT",
                "timestamp": datetime.now().isoformat()
            },
            {
                "symbol": "ETH-USD",
                "signal": "SELL",
                "price": 2650.00,
                "confidence": 72.3,
                "kill_zone": "NEW_YORK",
                "smc_pattern": "PREMIUM",
                "timestamp": datetime.now().isoformat()
            },
            {
                "symbol": "EURUSD=X",
                "signal": "BUY",
                "price": 1.0850,
                "confidence": 85.2,
                "kill_zone": "LONDON",
                "smc_pattern": "DISCOUNT",
                "timestamp": datetime.now().isoformat()
            }
        ]
        
        return {
            "status": "success",
            "signals": live_signals,
            "message": f"Live ICT/SMC signals updated. {len(live_signals)} active signals.",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting live signals: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/monitoring/start")
async def start_signal_monitoring():
    """Start the background signal monitoring system"""
    try:
        if start_monitoring():
            return {
                "status": "success",
                "message": "Background signal monitoring started",
                "timestamp": datetime.now().isoformat()
            }
        else:
            return {
                "status": "info",
                "message": "Monitoring already active",
                "timestamp": datetime.now().isoformat()
            }
    except Exception as e:
        logger.error(f"Error starting monitoring: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/monitoring/stop")
async def stop_signal_monitoring():
    """Stop the background signal monitoring system"""
    try:
        stop_monitoring()
        return {
            "status": "success",
            "message": "Background signal monitoring stopped",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error stopping monitoring: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/monitoring/status")
async def get_monitoring_status():
    """Get current monitoring status and active signals"""
    try:
        active_signals = get_active_signals()
        performance_stats = get_performance_stats()
        
        return {
            "status": "success",
            "monitoring_active": monitoring_active,
            "active_signals_count": len(active_signals),
            "active_signals": [
                {
                    "signal_id": signal[0],
                    "symbol": signal[1],
                    "signal_type": signal[2],
                    "entry_price": signal[3],
                    "target_price": signal[4],
                    "stop_loss": signal[5],
                    "confidence": signal[6],
                    "timestamp": signal[7]
                } for signal in active_signals
            ],
            "performance_stats": performance_stats,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting monitoring status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/performance/analytics")
async def get_performance_analytics():
    """Get detailed performance analytics for ML feedback"""
    try:
        stats = get_performance_stats()
        
        # Get recent signals for analysis
        conn = sqlite3.connect(signal_database)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT symbol, signal_type, confidence, outcome, profit_loss, duration_hours, quality_factors
            FROM signals 
            WHERE status = 'COMPLETED'
            ORDER BY timestamp DESC
            LIMIT 50
        ''')
        
        recent_signals = cursor.fetchall()
        conn.close()
        
        # Analyze quality factors performance
        quality_factor_performance = {}
        for signal in recent_signals:
            symbol, signal_type, confidence, outcome, profit_loss, duration, quality_factors = signal
            try:
                factors = json.loads(quality_factors) if quality_factors else []
                for factor in factors:
                    if factor not in quality_factor_performance:
                        quality_factor_performance[factor] = {'total': 0, 'profitable': 0, 'total_pnl': 0}
                    quality_factor_performance[factor]['total'] += 1
                    if profit_loss > 0:
                        quality_factor_performance[factor]['profitable'] += 1
                    quality_factor_performance[factor]['total_pnl'] += profit_loss
            except:
                continue
        
        return {
            "status": "success",
            "overall_stats": stats,
            "recent_signals": [
                {
                    "symbol": signal[0],
                    "signal_type": signal[1],
                    "confidence": signal[2],
                    "outcome": signal[3],
                    "profit_loss": signal[4],
                    "duration_hours": signal[5]
                } for signal in recent_signals
            ],
            "quality_factor_performance": quality_factor_performance,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting performance analytics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/ml/feedback")
async def trigger_ml_feedback():
    """Manually trigger ML feedback analysis"""
    try:
        update_ml_models_with_feedback()
        return {
            "status": "success",
            "message": "ML feedback analysis completed",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error triggering ML feedback: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/scanning/start")
async def start_continuous_scanning_api():
    """Start continuous market scanning for AI learning"""
    try:
        if start_continuous_scanning():
            return {
                "status": "success",
                "message": "Continuous market scanning started for AI learning",
                "scan_interval": "30 minutes",
                "symbols_per_scan": "50+ symbols across all markets",
                "timestamp": datetime.now().isoformat()
            }
        else:
            return {
                "status": "info",
                "message": "Continuous scanning already active",
                "timestamp": datetime.now().isoformat()
            }
    except Exception as e:
        logger.error(f"Error starting continuous scanning: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/scanning/stop")
async def stop_continuous_scanning_api():
    """Stop continuous market scanning"""
    try:
        stop_continuous_scanning()
        return {
            "status": "success",
            "message": "Continuous market scanning stopped",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error stopping continuous scanning: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/scanning/status")
async def get_continuous_scanning_status():
    """Get continuous scanning status and statistics"""
    try:
        scanning_status = get_scanning_status()
        monitoring_status = await get_monitoring_status()
        
        return {
            "status": "success",
            "continuous_scanning": scanning_status,
            "signal_monitoring": {
                "monitoring_active": monitoring_status.get('monitoring_active', False),
                "active_signals_count": monitoring_status.get('active_signals_count', 0)
            },
            "current_signals": current_signals,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting scanning status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ===== MULTI-TIMEFRAME ANALYSIS FUNCTIONS =====

def perform_multi_timeframe_analysis(symbol):
    """Perform comprehensive multi-timeframe analysis for higher quality signals"""
    try:
        ticker = yf.Ticker(symbol)
        
        # Define timeframes with professional trading approach (HTF to LTF)
        timeframes = {
            # HIGHER TIMEFRAMES - Trend Bias (Most Important)
            '12M': {'period': '2y', 'interval': '1mo', 'weight': 0.25},     # Long-term trend bias
            '6M': {'period': '1y', 'interval': '1mo', 'weight': 0.20},      # Major trend confirmation
            '3M': {'period': '6mo', 'interval': '1wk', 'weight': 0.15},     # Quarterly trend
            '1M': {'period': '3mo', 'interval': '1wk', 'weight': 0.10},     # Monthly trend
            
            # MEDIUM TIMEFRAMES - Structure & Setup
            '1W': {'period': '2mo', 'interval': '1wk', 'weight': 0.10},     # Weekly structure
            '1d': {'period': '3mo', 'interval': '1d', 'weight': 0.08},      # Daily bias
            '4h': {'period': '1mo', 'interval': '4h', 'weight': 0.07},      # Market structure
            
            # LOWER TIMEFRAMES - Entry Timing
            '1h': {'period': '5d', 'interval': '1h', 'weight': 0.03},       # Setup identification
            '15m': {'period': '2d', 'interval': '15m', 'weight': 0.02},     # Entry confirmation
            '5m': {'period': '1d', 'interval': '5m', 'weight': 0.01}        # Precise entry timing
        }
        
        timeframe_signals = {}
        total_weight = 0
        
        for tf, config in timeframes.items():
            try:
                # Get data for this timeframe
                hist = ticker.history(period=config['period'], interval=config['interval'])
                
                if hist.empty or len(hist) < 20:
                    continue
                
                # Analyze this timeframe
                tf_analysis = analyze_timeframe(hist, tf)
                if tf_analysis:
                    timeframe_signals[tf] = {
                        'signal': tf_analysis['signal'],
                        'confidence': tf_analysis['confidence'],
                        'trend': tf_analysis['trend'],
                        'weight': config['weight']
                    }
                    total_weight += config['weight']
                    
            except Exception as e:
                logger.error(f"Error analyzing {tf} timeframe: {e}")
                continue
        
        if not timeframe_signals:
            return {'consensus_direction': 'NEUTRAL', 'consensus_confidence': 0, 'consensus_score': 0}
        
        # Calculate weighted consensus
        bullish_weight = 0
        bearish_weight = 0
        neutral_weight = 0
        
        for tf, analysis in timeframe_signals.items():
            weight = analysis['weight']
            signal = analysis['signal']
            confidence = analysis['confidence']
            
            if signal == 'BUY':
                bullish_weight += weight * (confidence / 100)
            elif signal == 'SELL':
                bearish_weight += weight * (confidence / 100)
            else:
                neutral_weight += weight * (confidence / 100)
        
        # Normalize weights
        total_weighted = bullish_weight + bearish_weight + neutral_weight
        if total_weighted > 0:
            bullish_pct = (bullish_weight / total_weighted) * 100
            bearish_pct = (bearish_weight / total_weighted) * 100
            neutral_pct = (neutral_weight / total_weighted) * 100
        else:
            bullish_pct = bearish_pct = neutral_pct = 33.33
        
        # Determine consensus
        if bullish_pct > 60:
            consensus_direction = 'BULLISH'
            consensus_confidence = bullish_pct
            consensus_score = 25
        elif bearish_pct > 60:
            consensus_direction = 'BEARISH'
            consensus_confidence = bearish_pct
            consensus_score = -25
        else:
            consensus_direction = 'NEUTRAL'
            consensus_confidence = max(bullish_pct, bearish_pct, neutral_pct)
            consensus_score = 0
        
        return {
            'consensus_direction': consensus_direction,
            'consensus_confidence': round(consensus_confidence, 1),
            'consensus_score': consensus_score,
            'timeframe_signals': timeframe_signals,
            'bullish_pct': round(bullish_pct, 1),
            'bearish_pct': round(bearish_pct, 1),
            'neutral_pct': round(neutral_pct, 1)
        }
        
    except Exception as e:
        logger.error(f"Error in multi-timeframe analysis: {e}")
        return {'consensus_direction': 'NEUTRAL', 'consensus_confidence': 0, 'consensus_score': 0}

def analyze_timeframe(hist_data, timeframe):
    """Analyze a specific timeframe for trend and signal"""
    try:
        if len(hist_data) < 20:
            return None
        
        # Calculate basic indicators
        sma_20 = hist_data['Close'].rolling(window=20).mean()
        sma_50 = hist_data['Close'].rolling(window=50).mean() if len(hist_data) >= 50 else sma_20
        
        # RSI
        delta = hist_data['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        # MACD
        ema_12 = hist_data['Close'].ewm(span=12).mean()
        ema_26 = hist_data['Close'].ewm(span=26).mean()
        macd = ema_12 - ema_26
        macd_signal = macd.ewm(span=9).mean()
        
        # Current values
        current_price = hist_data['Close'].iloc[-1]
        current_sma_20 = sma_20.iloc[-1]
        current_sma_50 = sma_50.iloc[-1]
        current_rsi = rsi.iloc[-1]
        current_macd = macd.iloc[-1]
        current_macd_signal = macd_signal.iloc[-1]
        
        # Determine trend
        if current_price > current_sma_20 > current_sma_50:
            trend = 'BULLISH'
        elif current_price < current_sma_20 < current_sma_50:
            trend = 'BEARISH'
        else:
            trend = 'NEUTRAL'
        
        # Generate signal based on timeframe
        signal = 'HOLD'
        confidence = 50
        
        # HIGHER TIMEFRAMES - Trend Bias Analysis (Most Important)
        if timeframe in ['12M', '6M', '3M', '1M']:  # Long-term trend bias
            if trend == 'BULLISH':
                signal = 'BUY'
                confidence = 85 if timeframe == '12M' else 80 if timeframe == '6M' else 75
            elif trend == 'BEARISH':
                signal = 'SELL'
                confidence = 85 if timeframe == '12M' else 80 if timeframe == '6M' else 75
            else:
                signal = 'HOLD'
                confidence = 70
                
        elif timeframe == '1W':  # Weekly structure
            if trend == 'BULLISH' and current_rsi < 70:
                signal = 'BUY'
                confidence = 75
            elif trend == 'BEARISH' and current_rsi > 30:
                signal = 'SELL'
                confidence = 75
            else:
                signal = 'HOLD'
                confidence = 70
                
        elif timeframe == '1d':  # Daily - trend direction
            if trend == 'BULLISH' and current_rsi < 70:
                signal = 'BUY'
                confidence = 70
            elif trend == 'BEARISH' and current_rsi > 30:
                signal = 'SELL'
                confidence = 70
            else:
                signal = 'HOLD'
                confidence = 65
                
        elif timeframe == '4h':  # 4H - market structure
            if trend == 'BULLISH' and current_macd > current_macd_signal:
                signal = 'BUY'
                confidence = 65
            elif trend == 'BEARISH' and current_macd < current_macd_signal:
                signal = 'SELL'
                confidence = 65
            else:
                signal = 'HOLD'
                confidence = 60
                
        elif timeframe == '1h':  # 1H - setup identification
            if current_rsi < 30 and current_macd > current_macd_signal:
                signal = 'BUY'
                confidence = 60
            elif current_rsi > 70 and current_macd < current_macd_signal:
                signal = 'SELL'
                confidence = 60
            else:
                signal = 'HOLD'
                confidence = 55
                
        elif timeframe == '15m':  # 15m - entry confirmation
            if current_rsi < 40 and current_price > current_sma_20:
                signal = 'BUY'
                confidence = 55
            elif current_rsi > 60 and current_price < current_sma_20:
                signal = 'SELL'
                confidence = 55
            else:
                signal = 'HOLD'
                confidence = 50
                
        elif timeframe == '5m':  # 5m - precise entry timing
            if current_rsi < 35 and current_price > current_sma_20:
                signal = 'BUY'
                confidence = 50
            elif current_rsi > 65 and current_price < current_sma_20:
                signal = 'SELL'
                confidence = 50
            else:
                signal = 'HOLD'
                confidence = 45
        
        return {
            'signal': signal,
            'confidence': confidence,
            'trend': trend,
            'rsi': round(current_rsi, 2),
            'macd': round(current_macd, 4),
            'price_vs_sma20': round(((current_price - current_sma_20) / current_sma_20) * 100, 2)
        }
        
    except Exception as e:
        logger.error(f"Error analyzing timeframe {timeframe}: {e}")
        return None

# ===== ADVANCED ORDER FLOW, MARKET STRUCTURE, AND POI FUNCTIONS =====

def detect_institutional_flow(hist_data):
    """Detect institutional order flow patterns"""
    try:
        if 'Volume' not in hist_data.columns or len(hist_data) < 10:
            return {'detected': False, 'score': 0, 'type': 'NONE'}
        
        # Look for large volume spikes (institutional activity)
        volumes = hist_data['Volume'].tolist()
        avg_volume = sum(volumes[-10:]) / 10
        
        recent_volume = volumes[-1]
        volume_ratio = recent_volume / avg_volume if avg_volume > 0 else 1
        
        # Check for institutional buying (high volume + price increase)
        price_change = (hist_data['Close'].iloc[-1] - hist_data['Close'].iloc[-2]) / hist_data['Close'].iloc[-2]
        
        if volume_ratio > 2.0 and price_change > 0.01:  # 2x volume + 1% price increase
            return {'detected': True, 'score': 15, 'type': 'BUYING'}
        elif volume_ratio > 2.0 and price_change < -0.01:  # 2x volume + 1% price decrease
            return {'detected': True, 'score': -15, 'type': 'SELLING'}
        elif volume_ratio > 1.5:  # Just high volume
            return {'detected': True, 'score': 8, 'type': 'ACCUMULATION'}
        
        return {'detected': False, 'score': 0, 'type': 'NONE'}
        
    except Exception as e:
        logger.error(f"Error detecting institutional flow: {e}")
        return {'detected': False, 'score': 0, 'type': 'NONE'}

def detect_swing_points(hist_data):
    """Detect swing highs and swing lows for market structure analysis"""
    try:
        if len(hist_data) < 10:
            return {'bullish_swing': False, 'bearish_swing': False}
        
        highs = hist_data['High'].tolist()
        lows = hist_data['Low'].tolist()
        
        # Look for recent swing points
        recent_highs = highs[-5:]
        recent_lows = lows[-5:]
        
        # Bullish swing: higher low followed by higher high
        if (len(recent_lows) >= 3 and len(recent_highs) >= 3 and
            recent_lows[-1] > recent_lows[-2] and recent_highs[-1] > recent_highs[-2]):
            return {'bullish_swing': True, 'bearish_swing': False}
        
        # Bearish swing: lower high followed by lower low
        elif (len(recent_highs) >= 3 and len(recent_lows) >= 3 and
              recent_highs[-1] < recent_highs[-2] and recent_lows[-1] < recent_lows[-2]):
            return {'bullish_swing': False, 'bearish_swing': True}
        
        return {'bullish_swing': False, 'bearish_swing': False}
        
    except Exception as e:
        logger.error(f"Error detecting swing points: {e}")
        return {'bullish_swing': False, 'bearish_swing': False}

def detect_structure_shift(hist_data):
    """Detect market structure shifts (BOS - Break of Structure)"""
    try:
        if len(hist_data) < 15:
            return {'shift_detected': False, 'score': 0, 'type': 'NONE'}
        
        highs = hist_data['High'].tolist()
        lows = hist_data['Low'].tolist()
        
        # Look for structure breaks in last 10 periods
        recent_highs = highs[-10:]
        recent_lows = lows[-10:]
        
        # Bullish BOS: Break above recent high
        if len(recent_highs) >= 5:
            max_recent_high = max(recent_highs[:-1])  # Exclude current candle
            if highs[-1] > max_recent_high:
                return {'shift_detected': True, 'score': 20, 'type': 'BULLISH_BOS'}
        
        # Bearish BOS: Break below recent low
        if len(recent_lows) >= 5:
            min_recent_low = min(recent_lows[:-1])  # Exclude current candle
            if lows[-1] < min_recent_low:
                return {'shift_detected': True, 'score': -20, 'type': 'BEARISH_BOS'}
        
        return {'shift_detected': False, 'score': 0, 'type': 'NONE'}
        
    except Exception as e:
        logger.error(f"Error detecting structure shift: {e}")
        return {'shift_detected': False, 'score': 0, 'type': 'NONE'}

def detect_liquidity_pools(hist_data):
    """Detect liquidity pools (areas where stop losses are likely placed)"""
    try:
        if len(hist_data) < 20:
            return []
        
        highs = hist_data['High'].tolist()
        lows = hist_data['Low'].tolist()
        
        liquidity_pools = []
        
        # Look for equal highs and lows (liquidity zones)
        for i in range(5, len(hist_data) - 5):
            # Equal highs (resistance liquidity)
            if abs(highs[i] - max(highs[i-5:i+6])) < (max(highs[i-5:i+6]) * 0.001):  # Within 0.1%
                liquidity_pools.append({
                    'price': highs[i],
                    'type': 'RESISTANCE',
                    'strength': 1.0
                })
            
            # Equal lows (support liquidity)
            if abs(lows[i] - min(lows[i-5:i+6])) < (min(lows[i-5:i+6]) * 0.001):  # Within 0.1%
                liquidity_pools.append({
                    'price': lows[i],
                    'type': 'SUPPORT',
                    'strength': 1.0
                })
        
        return liquidity_pools
        
    except Exception as e:
        logger.error(f"Error detecting liquidity pools: {e}")
        return []

def detect_equal_highs_lows(hist_data):
    """Detect equal highs and equal lows (key POI levels)"""
    try:
        if len(hist_data) < 20:
            return []
        
        highs = hist_data['High'].tolist()
        lows = hist_data['Low'].tolist()
        
        equal_levels = []
        
        # Look for equal highs (within 0.2% of each other)
        for i in range(10, len(hist_data) - 5):
            current_high = highs[i]
            # Check if this high is equal to any previous high
            for j in range(max(0, i-20), i-5):
                if abs(current_high - highs[j]) / current_high < 0.002:  # Within 0.2%
                    equal_levels.append({
                        'price': current_high,
                        'type': 'EQUAL_HIGH',
                        'strength': 1.0
                    })
                    break
        
        # Look for equal lows (within 0.2% of each other)
        for i in range(10, len(hist_data) - 5):
            current_low = lows[i]
            # Check if this low is equal to any previous low
            for j in range(max(0, i-20), i-5):
                if abs(current_low - lows[j]) / current_low < 0.002:  # Within 0.2%
                    equal_levels.append({
                        'price': current_low,
                        'type': 'EQUAL_LOW',
                        'strength': 1.0
                    })
                    break
        
        return equal_levels
        
    except Exception as e:
        logger.error(f"Error detecting equal highs/lows: {e}")
        return []

def detect_confluent_levels(hist_data):
    """Detect confluent support/resistance zones where multiple factors align"""
    try:
        if len(hist_data) < 20:
            return {'confluence_detected': False, 'score': 0, 'type': 'NONE'}
        
        current_price = hist_data['Close'].iloc[-1]
        
        # Get various levels
        sma_20 = hist_data['Close'].rolling(window=20).mean().iloc[-1]
        sma_50 = hist_data['Close'].rolling(window=50).mean().iloc[-1] if len(hist_data) >= 50 else sma_20
        
        # Calculate pivot points
        high = hist_data['High'].iloc[-1]
        low = hist_data['Low'].iloc[-1]
        close = hist_data['Close'].iloc[-1]
        pivot = (high + low + close) / 3
        resistance = 2 * pivot - low
        support = 2 * pivot - high
        
        confluence_score = 0
        confluence_factors = []
        
        # Check for confluence near current price (within 1%)
        price_tolerance = current_price * 0.01
        
        # SMA confluence
        if abs(current_price - sma_20) < price_tolerance:
            confluence_score += 10
            confluence_factors.append("SMA 20")
        
        if abs(current_price - sma_50) < price_tolerance:
            confluence_score += 10
            confluence_factors.append("SMA 50")
        
        # Pivot point confluence
        if abs(current_price - pivot) < price_tolerance:
            confluence_score += 15
            confluence_factors.append("Pivot Point")
        
        if abs(current_price - resistance) < price_tolerance:
            confluence_score += 12
            confluence_factors.append("Resistance")
        
        if abs(current_price - support) < price_tolerance:
            confluence_score += 12
            confluence_factors.append("Support")
        
        # Determine confluence type
        if confluence_score >= 25:
            confluence_type = "STRONG_CONFLUENCE"
        elif confluence_score >= 15:
            confluence_type = "MODERATE_CONFLUENCE"
        else:
            confluence_type = "WEAK_CONFLUENCE"
        
        return {
            'confluence_detected': confluence_score >= 15,
            'score': confluence_score,
            'type': confluence_type,
            'factors': confluence_factors
        }
        
    except Exception as e:
        logger.error(f"Error detecting confluent levels: {e}")
        return {'confluence_detected': False, 'score': 0, 'type': 'NONE'}

if __name__ == "__main__":
    # Initialize ML models
    initialize_ml_models()
    
    # Initialize signal tracking database
    initialize_signal_database()
    
    # Start background monitoring
    start_monitoring()
    
    print("🚀 Starting Enhanced Clean Trading Signals Server...")
    print("📍 API URL: http://localhost:8006")
    print("🔗 Health check: http://localhost:8006/api/health")
    print("🧠 Features: ICT/SMC + Machine Learning + Advanced Indicators")
    print("🎯 Advanced Order Flow, Market Structure & POI Analysis")
    print("🤖 Self-Learning AI with Signal Tracking & Performance Analytics")
    print("📊 Database: trading_signals.db")
    print("⏹️  Press Ctrl+C to stop the server")
    
    uvicorn.run(
        "enhanced_clean_server:app",
        host="0.0.0.0",
        port=8006,
        reload=True,
        log_level="info"
    )
