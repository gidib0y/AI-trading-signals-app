from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import yfinance as yf
import pandas as pd
import numpy as np
import ta
from datetime import datetime, timedelta

from src.database import get_db, TechnicalIndicators

router = APIRouter()

@router.get("/{symbol}")
async def get_technical_analysis(
    symbol: str,
    period: str = Query("6mo", description="Data period for analysis"),
    db: Session = Depends(get_db)
):
    """Get comprehensive technical analysis for a symbol"""
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period=period)
        
        if hist.empty:
            raise HTTPException(status_code=404, detail=f"No data found for {symbol}")
        
        # Calculate technical indicators
        indicators = calculate_technical_indicators(hist)
        
        # Store in database
        tech_data = TechnicalIndicators(
            symbol=symbol,
            rsi=indicators['rsi'],
            macd=indicators['macd'],
            macd_signal=indicators['macd_signal'],
            macd_histogram=indicators['macd_histogram'],
            sma_20=indicators['sma_20'],
            sma_50=indicators['sma_50'],
            ema_12=indicators['ema_12'],
            ema_26=indicators['ema_26'],
            bollinger_upper=indicators['bollinger_upper'],
            bollinger_middle=indicators['bollinger_middle'],
            bollinger_lower=indicators['bollinger_lower'],
            atr=indicators['atr'],
            stochastic_k=indicators['stochastic_k'],
            stochastic_d=indicators['stochastic_d']
        )
        db.add(tech_data)
        db.commit()
        
        # Generate analysis summary
        analysis_summary = generate_analysis_summary(indicators, hist)
        
        return {
            "symbol": symbol,
            "period": period,
            "indicators": indicators,
            "analysis": analysis_summary,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error analyzing {symbol}: {str(e)}")

@router.get("/{symbol}/indicators")
async def get_indicators(
    symbol: str,
    indicator: str = Query(..., description="Indicator name (rsi, macd, bollinger, sma, ema, stochastic, atr)"),
    period: str = Query("6mo", description="Data period")
):
    """Get specific technical indicator data"""
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period=period)
        
        if hist.empty:
            raise HTTPException(status_code=404, detail=f"No data found for {symbol}")
        
        if indicator == "rsi":
            data = calculate_rsi(hist)
        elif indicator == "macd":
            data = calculate_macd(hist)
        elif indicator == "bollinger":
            data = calculate_bollinger_bands(hist)
        elif indicator == "sma":
            data = calculate_sma(hist)
        elif indicator == "ema":
            data = calculate_ema(hist)
        elif indicator == "stochastic":
            data = calculate_stochastic(hist)
        elif indicator == "atr":
            data = calculate_atr(hist)
        else:
            raise HTTPException(status_code=400, detail=f"Unknown indicator: {indicator}")
        
        return {
            "symbol": symbol,
            "indicator": indicator,
            "period": period,
            "data": data
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating {indicator} for {symbol}: {str(e)}")

def calculate_technical_indicators(hist: pd.DataFrame) -> dict:
    """Calculate all technical indicators"""
    close = hist['Close']
    high = hist['High']
    low = hist['Low']
    volume = hist['Volume']
    
    # RSI
    rsi = ta.momentum.RSIIndicator(close).rsi().iloc[-1]
    
    # MACD
    macd = ta.trend.MACD(close)
    macd_line = macd.macd().iloc[-1]
    macd_signal = macd.macd_signal().iloc[-1]
    macd_histogram = macd.macd_diff().iloc[-1]
    
    # Moving Averages
    sma_20 = ta.trend.SMAIndicator(close, window=20).sma_indicator().iloc[-1]
    sma_50 = ta.trend.SMAIndicator(close, window=50).sma_indicator().iloc[-1]
    ema_12 = ta.trend.EMAIndicator(close, window=12).ema_indicator().iloc[-1]
    ema_26 = ta.trend.EMAIndicator(close, window=26).ema_indicator().iloc[-1]
    
    # Bollinger Bands
    bb = ta.volatility.BollingerBands(close)
    bb_upper = bb.bollinger_hband().iloc[-1]
    bb_middle = bb.bollinger_mavg().iloc[-1]
    bb_lower = bb.bollinger_lband().iloc[-1]
    
    # ATR
    atr = ta.volatility.AverageTrueRange(high, low, close).average_true_range().iloc[-1]
    
    # Stochastic
    stoch = ta.momentum.StochasticOscillator(high, low, close)
    stoch_k = stoch.stoch().iloc[-1]
    stoch_d = stoch.stoch_signal().iloc[-1]
    
    return {
        "rsi": round(rsi, 2) if not pd.isna(rsi) else None,
        "macd": round(macd_line, 4) if not pd.isna(macd_line) else None,
        "macd_signal": round(macd_signal, 4) if not pd.isna(macd_signal) else None,
        "macd_histogram": round(macd_histogram, 4) if not pd.isna(macd_histogram) else None,
        "sma_20": round(sma_20, 2) if not pd.isna(sma_20) else None,
        "sma_50": round(sma_50, 2) if not pd.isna(sma_50) else None,
        "ema_12": round(ema_12, 2) if not pd.isna(ema_12) else None,
        "ema_26": round(ema_26, 2) if not pd.isna(ema_26) else None,
        "bollinger_upper": round(bb_upper, 2) if not pd.isna(bb_upper) else None,
        "bollinger_middle": round(bb_middle, 2) if not pd.isna(bb_middle) else None,
        "bollinger_lower": round(bb_lower, 2) if not pd.isna(bb_lower) else None,
        "atr": round(atr, 2) if not pd.isna(atr) else None,
        "stochastic_k": round(stoch_k, 2) if not pd.isna(stoch_k) else None,
        "stochastic_d": round(stoch_d, 2) if not pd.isna(stoch_d) else None
    }

def calculate_rsi(hist: pd.DataFrame) -> dict:
    """Calculate RSI with overbought/oversold levels"""
    close = hist['Close']
    rsi = ta.momentum.RSIIndicator(close).rsi()
    
    data = []
    for i, (timestamp, value) in enumerate(rsi.items()):
        if not pd.isna(value):
            data.append({
                "timestamp": timestamp.isoformat(),
                "rsi": round(value, 2),
                "overbought": value > 70,
                "oversold": value < 30
            })
    
    return {
        "current_rsi": round(rsi.iloc[-1], 2) if not pd.isna(rsi.iloc[-1]) else None,
        "overbought": rsi.iloc[-1] > 70 if not pd.isna(rsi.iloc[-1]) else False,
        "oversold": rsi.iloc[-1] < 30 if not pd.isna(rsi.iloc[-1]) else False,
        "data": data
    }

def calculate_macd(hist: pd.DataFrame) -> dict:
    """Calculate MACD with signal line and histogram"""
    close = hist['Close']
    macd = ta.trend.MACD(close)
    
    data = []
    for i, (timestamp, macd_val) in enumerate(macd.macd().items()):
        if not pd.isna(macd_val):
            signal_val = macd.macd_signal().iloc[i] if i < len(macd.macd_signal()) else None
            hist_val = macd.macd_diff().iloc[i] if i < len(macd.macd_diff()) else None
            
            data.append({
                "timestamp": timestamp.isoformat(),
                "macd": round(macd_val, 4) if not pd.isna(macd_val) else None,
                "signal": round(signal_val, 4) if not pd.isna(signal_val) else None,
                "histogram": round(hist_val, 4) if not pd.isna(hist_val) else None
            })
    
    return {
        "current_macd": round(macd.macd().iloc[-1], 4) if not pd.isna(macd.macd().iloc[-1]) else None,
        "current_signal": round(macd.macd_signal().iloc[-1], 4) if not pd.isna(macd.macd_signal().iloc[-1]) else None,
        "current_histogram": round(macd.macd_diff().iloc[-1], 4) if not pd.isna(macd.macd_diff().iloc[-1]) else None,
        "bullish_crossover": macd.macd().iloc[-1] > macd.macd_signal().iloc[-1] if not pd.isna(macd.macd().iloc[-1]) and not pd.isna(macd.macd_signal().iloc[-1]) else False,
        "data": data
    }

def calculate_bollinger_bands(hist: pd.DataFrame) -> dict:
    """Calculate Bollinger Bands with squeeze detection"""
    close = hist['Close']
    bb = ta.volatility.BollingerBands(close)
    
    data = []
    for i, (timestamp, upper) in enumerate(bb.bollinger_hband().items()):
        if not pd.isna(upper):
            middle = bb.bollinger_mavg().iloc[i] if i < len(bb.bollinger_mavg()) else None
            lower = bb.bollinger_lband().iloc[i] if i < len(bb.bollinger_lband()) else None
            close_val = close.iloc[i] if i < len(close) else None
            
            data.append({
                "timestamp": timestamp.isoformat(),
                "upper": round(upper, 2) if not pd.isna(upper) else None,
                "middle": round(middle, 2) if not pd.isna(middle) else None,
                "lower": round(lower, 2) if not pd.isna(lower) else None,
                "close": round(close_val, 2) if not pd.isna(close_val) else None,
                "squeeze": (upper - lower) / middle < 0.1 if not pd.isna(upper) and not pd.isna(lower) and not pd.isna(middle) else False
            })
    
    current_close = close.iloc[-1]
    current_upper = bb.bollinger_hband().iloc[-1]
    current_lower = bb.bollinger_lband().iloc[-1]
    
    return {
        "current_upper": round(current_upper, 2) if not pd.isna(current_upper) else None,
        "current_middle": round(bb.bollinger_mavg().iloc[-1], 2) if not pd.isna(bb.bollinger_mavg().iloc[-1]) else None,
        "current_lower": round(current_lower, 2) if not pd.isna(current_lower) else None,
        "squeeze": (current_upper - current_lower) / bb.bollinger_mavg().iloc[-1] < 0.1 if not pd.isna(current_upper) and not pd.isna(current_lower) and not pd.isna(bb.bollinger_mavg().iloc[-1]) else False,
        "above_upper": current_close > current_upper if not pd.isna(current_close) and not pd.isna(current_upper) else False,
        "below_lower": current_close < current_lower if not pd.isna(current_close) and not pd.isna(current_lower) else False,
        "data": data
    }

def calculate_sma(hist: pd.DataFrame) -> dict:
    """Calculate Simple Moving Averages"""
    close = hist['Close']
    
    sma_20 = ta.trend.SMAIndicator(close, window=20).sma_indicator()
    sma_50 = ta.trend.SMAIndicator(close, window=50).sma_indicator()
    
    data = []
    for i, (timestamp, sma20_val) in enumerate(sma_20.items()):
        if not pd.isna(sma20_val):
            sma50_val = sma_50.iloc[i] if i < len(sma_50) else None
            close_val = close.iloc[i] if i < len(close) else None
            
            data.append({
                "timestamp": timestamp.isoformat(),
                "sma_20": round(sma20_val, 2) if not pd.isna(sma20_val) else None,
                "sma_50": round(sma50_val, 2) if not pd.isna(sma50_val) else None,
                "close": round(close_val, 2) if not pd.isna(close_val) else None,
                "golden_cross": sma20_val > sma50_val if not pd.isna(sma20_val) and not pd.isna(sma50_val) else False
            })
    
    return {
        "current_sma_20": round(sma_20.iloc[-1], 2) if not pd.isna(sma_20.iloc[-1]) else None,
        "current_sma_50": round(sma_50.iloc[-1], 2) if not pd.isna(sma_50.iloc[-1]) else None,
        "golden_cross": sma_20.iloc[-1] > sma_50.iloc[-1] if not pd.isna(sma_20.iloc[-1]) and not pd.isna(sma_50.iloc[-1]) else False,
        "data": data
    }

def calculate_ema(hist: pd.DataFrame) -> dict:
    """Calculate Exponential Moving Averages"""
    close = hist['Close']
    
    ema_12 = ta.trend.EMAIndicator(close, window=12).ema_indicator()
    ema_26 = ta.trend.EMAIndicator(close, window=26).ema_indicator()
    
    data = []
    for i, (timestamp, ema12_val) in enumerate(ema_12.items()):
        if not pd.isna(ema12_val):
            ema26_val = ema_26.iloc[i] if i < len(ema_26) else None
            close_val = close.iloc[i] if i < len(close) else None
            
            data.append({
                "timestamp": timestamp.isoformat(),
                "ema_12": round(ema12_val, 2) if not pd.isna(ema12_val) else None,
                "ema_26": round(ema26_val, 2) if not pd.isna(ema26_val) else None,
                "close": round(close_val, 2) if not pd.isna(close_val) else None,
                "bullish": ema12_val > ema26_val if not pd.isna(ema12_val) and not pd.isna(ema26_val) else False
            })
    
    return {
        "current_ema_12": round(ema_12.iloc[-1], 2) if not pd.isna(ema_12.iloc[-1]) else None,
        "current_ema_26": round(ema_26.iloc[-1], 2) if not pd.isna(ema_26.iloc[-1]) else None,
        "bullish": ema_12.iloc[-1] > ema_26.iloc[-1] if not pd.isna(ema_12.iloc[-1]) and not pd.isna(ema_26.iloc[-1]) else False,
        "data": data
    }

def calculate_stochastic(hist: pd.DataFrame) -> dict:
    """Calculate Stochastic Oscillator"""
    high = hist['High']
    low = hist['Low']
    close = hist['Close']
    
    stoch = ta.momentum.StochasticOscillator(high, low, close)
    stoch_k = stoch.stoch()
    stoch_d = stoch.stoch_signal()
    
    data = []
    for i, (timestamp, k_val) in enumerate(stoch_k.items()):
        if not pd.isna(k_val):
            d_val = stoch_d.iloc[i] if i < len(stoch_d) else None
            
            data.append({
                "timestamp": timestamp.isoformat(),
                "k": round(k_val, 2) if not pd.isna(k_val) else None,
                "d": round(d_val, 2) if not pd.isna(d_val) else None,
                "overbought": k_val > 80 if not pd.isna(k_val) else False,
                "oversold": k_val < 20 if not pd.isna(k_val) else False
            })
    
    return {
        "current_k": round(stoch_k.iloc[-1], 2) if not pd.isna(stoch_k.iloc[-1]) else None,
        "current_d": round(stoch_d.iloc[-1], 2) if not pd.isna(stoch_d.iloc[-1]) else None,
        "overbought": stoch_k.iloc[-1] > 80 if not pd.isna(stoch_k.iloc[-1]) else False,
        "oversold": stoch_k.iloc[-1] < 20 if not pd.isna(stoch_k.iloc[-1]) else False,
        "data": data
    }

def calculate_atr(hist: pd.DataFrame) -> dict:
    """Calculate Average True Range"""
    high = hist['High']
    low = hist['Low']
    close = hist['Close']
    
    atr = ta.volatility.AverageTrueRange(high, low, close).average_true_range()
    
    data = []
    for timestamp, atr_val in atr.items():
        if not pd.isna(atr_val):
            data.append({
                "timestamp": timestamp.isoformat(),
                "atr": round(atr_val, 2)
            })
    
    return {
        "current_atr": round(atr.iloc[-1], 2) if not pd.isna(atr.iloc[-1]) else None,
        "data": data
    }

def generate_analysis_summary(indicators: dict, hist: pd.DataFrame) -> dict:
    """Generate trading analysis summary"""
    current_price = hist['Close'].iloc[-1]
    
    # RSI Analysis
    rsi_signal = "NEUTRAL"
    if indicators['rsi']:
        if indicators['rsi'] > 70:
            rsi_signal = "OVERBOUGHT"
        elif indicators['rsi'] < 30:
            rsi_signal = "OVERSOLD"
    
    # MACD Analysis
    macd_signal = "NEUTRAL"
    if indicators['macd'] and indicators['macd_signal']:
        if indicators['macd'] > indicators['macd_signal']:
            macd_signal = "BULLISH"
        else:
            macd_signal = "BEARISH"
    
    # Moving Average Analysis
    ma_signal = "NEUTRAL"
    if indicators['sma_20'] and indicators['sma_50']:
        if indicators['sma_20'] > indicators['sma_50']:
            ma_signal = "BULLISH"
        else:
            ma_signal = "BEARISH"
    
    # Bollinger Bands Analysis
    bb_signal = "NEUTRAL"
    if indicators['bollinger_upper'] and indicators['bollinger_lower']:
        if current_price > indicators['bollinger_upper']:
            bb_signal = "OVERBOUGHT"
        elif current_price < indicators['bollinger_lower']:
            bb_signal = "OVERSOLD"
    
    # Overall Signal
    bullish_count = sum([
        1 if rsi_signal == "OVERSOLD" else 0,
        1 if macd_signal == "BULLISH" else 0,
        1 if ma_signal == "BULLISH" else 0,
        1 if bb_signal == "OVERSOLD" else 0
    ])
    
    bearish_count = sum([
        1 if rsi_signal == "OVERBOUGHT" else 0,
        1 if macd_signal == "BEARISH" else 0,
        1 if ma_signal == "BEARISH" else 0,
        1 if bb_signal == "OVERBOUGHT" else 0
    ])
    
    if bullish_count > bearish_count:
        overall_signal = "BULLISH"
    elif bearish_count > bullish_count:
        overall_signal = "BEARISH"
    else:
        overall_signal = "NEUTRAL"
    
    return {
        "rsi_signal": rsi_signal,
        "macd_signal": macd_signal,
        "ma_signal": ma_signal,
        "bb_signal": bb_signal,
        "overall_signal": overall_signal,
        "confidence": min(max(bullish_count + bearish_count, 0), 100),
        "summary": f"Technical analysis shows {overall_signal.lower()} signals with {rsi_signal.lower()} RSI, {macd_signal.lower()} MACD, {ma_signal.lower()} moving averages, and {bb_signal.lower()} Bollinger Bands."
    }

