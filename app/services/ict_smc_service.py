import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum

class SignalType(Enum):
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"

@dataclass
class ICTPattern:
    pattern_type: str
    start_price: float
    end_price: float
    start_time: pd.Timestamp
    end_time: pd.Timestamp
    strength: float
    direction: str

@dataclass
class LiveSignal:
    symbol: str
    signal_type: SignalType
    entry_price: float
    stop_loss: float
    take_profit: float
    confidence: float
    pattern: str
    timestamp: pd.Timestamp
    timeframe: str
    risk_reward: float

class ICTSMCAnalyzer:
    def __init__(self):
        self.min_gap_size = 0.001  # Minimum gap size for FVG
        self.min_block_size = 0.005  # Minimum order block size
        
    def detect_fair_value_gaps(self, df: pd.DataFrame) -> List[ICTPattern]:
        """Detect Fair Value Gaps (FVG) - institutional order blocks"""
        fvgs = []
        
        for i in range(1, len(df) - 1):
            high = df.iloc[i]['High']
            low = df.iloc[i]['Low']
            prev_low = df.iloc[i-1]['Low']
            next_high = df.iloc[i+1]['High']
            
            # Bullish FVG: gap between current high and previous low
            if high > prev_low and (high - prev_low) > self.min_gap_size:
                fvgs.append(ICTPattern(
                    pattern_type="Bullish_FVG",
                    start_price=prev_low,
                    end_price=high,
                    start_time=df.iloc[i-1].name,
                    end_time=df.iloc[i].name,
                    strength=(high - prev_low) / prev_low,
                    direction="BULLISH"
                ))
            
            # Bearish FVG: gap between current low and previous high
            if low < prev_low and (prev_low - low) > self.min_gap_size:
                fvgs.append(ICTPattern(
                    pattern_type="Bearish_FVG",
                    start_price=low,
                    end_price=prev_low,
                    start_time=df.iloc[i-1].name,
                    end_time=df.iloc[i].name,
                    strength=(prev_low - low) / low,
                    direction="BEARISH"
                ))
        
        return fvgs
    
    def detect_order_blocks(self, df: pd.DataFrame) -> List[ICTPattern]:
        """Detect Order Blocks - major institutional entry/exit areas"""
        order_blocks = []
        
        for i in range(1, len(df) - 1):
            current_candle = df.iloc[i]
            prev_candle = df.iloc[i-1]
            
            # Bullish Order Block: strong up move after down move
            if (current_candle['Close'] > current_candle['Open'] and 
                prev_candle['Close'] < prev_candle['Open'] and
                (current_candle['Close'] - current_candle['Open']) > self.min_block_size):
                
                order_blocks.append(ICTPattern(
                    pattern_type="Bullish_OrderBlock",
                    start_price=prev_candle['Low'],
                    end_price=current_candle['High'],
                    start_time=prev_candle.name,
                    end_time=current_candle.name,
                    strength=(current_candle['Close'] - current_candle['Open']) / current_candle['Open'],
                    direction="BULLISH"
                ))
            
            # Bearish Order Block: strong down move after up move
            elif (current_candle['Close'] < current_candle['Open'] and 
                  prev_candle['Close'] > prev_candle['Open'] and
                  (prev_candle['Close'] - prev_candle['Open']) > self.min_block_size):
                
                order_blocks.append(ICTPattern(
                    pattern_type="Bearish_OrderBlock",
                    start_price=current_candle['Low'],
                    end_price=prev_candle['High'],
                    start_time=prev_candle.name,
                    end_time=current_candle.name,
                    strength=(prev_candle['Close'] - prev_candle['Open']) / prev_candle['Open'],
                    direction="BEARISH"
                ))
        
        return order_blocks
    
    def detect_liquidity_sweeps(self, df: pd.DataFrame) -> List[ICTPattern]:
        """Detect Liquidity Sweeps - stop loss hunting zones"""
        sweeps = []
        
        for i in range(1, len(df) - 1):
            current_candle = df.iloc[i]
            prev_candle = df.iloc[i-1]
            
            # Bullish sweep: price goes below previous low then recovers
            if (current_candle['Low'] < prev_candle['Low'] and 
                current_candle['Close'] > prev_candle['Low']):
                
                sweeps.append(ICTPattern(
                    pattern_type="Bullish_LiquiditySweep",
                    start_price=current_candle['Low'],
                    end_price=current_candle['Close'],
                    start_time=current_candle.name,
                    end_time=current_candle.name,
                    strength=(current_candle['Close'] - current_candle['Low']) / current_candle['Low'],
                    direction="BULLISH"
                ))
            
            # Bearish sweep: price goes above previous high then drops
            elif (current_candle['High'] > prev_candle['High'] and 
                  current_candle['Close'] < prev_candle['High']):
                
                sweeps.append(ICTPattern(
                    pattern_type="Bearish_LiquiditySweep",
                    start_price=current_candle['High'],
                    end_price=current_candle['Close'],
                    start_time=current_candle.name,
                    end_time=current_candle.name,
                    strength=(current_candle['High'] - current_candle['Close']) / current_candle['Close'],
                    direction="BEARISH"
                ))
        
        return sweeps
    
    def analyze_market_structure(self, df: pd.DataFrame) -> Dict:
        """Analyze market structure for SMC concepts"""
        highs = df['High'].rolling(window=5, center=True).max()
        lows = df['Low'].rolling(window=5, center=True).min()
        
        # Detect higher highs and lower lows
        higher_highs = []
        lower_lows = []
        
        for i in range(5, len(df)):
            if highs.iloc[i] > highs.iloc[i-1]:
                higher_highs.append(i)
            if lows.iloc[i] < lows.iloc[i-1]:
                lower_lows.append(i)
        
        # Market structure
        if len(higher_highs) > len(lower_lows):
            structure = "BULLISH"
        elif len(lower_lows) > len(higher_highs):
            structure = "BEARISH"
        else:
            structure = "NEUTRAL"
        
        return {
            "structure": structure,
            "higher_highs_count": len(higher_highs),
            "lower_lows_count": len(lower_lows),
            "momentum": len(higher_highs) - len(lower_lows)
        }
    
    def generate_live_signals(self, df: pd.DataFrame, symbol: str, timeframe: str) -> List[LiveSignal]:
        """Generate live trading signals based on ICT/SMC analysis"""
        signals = []
        
        # Get latest patterns
        fvgs = self.detect_fair_value_gaps(df)
        order_blocks = self.detect_order_blocks(df)
        liquidity_sweeps = self.detect_liquidity_sweeps(df)
        market_structure = self.analyze_market_structure(df)
        
        current_price = df.iloc[-1]['Close']
        
        # Generate signals based on STRICT pattern confluence (only high-quality setups)
        signals_generated = 0
        max_signals_per_symbol = 1  # Only 1 signal per symbol
        
        # Only check the STRONGEST FVG (not last 3)
        if fvgs and fvgs[-1].strength > 0.7:  # Must be strong FVG
            fvg = fvgs[-1]
            
            if fvg.direction == "BULLISH" and market_structure["structure"] == "BULLISH":
                # Look for STRONG bullish order block support
                for ob in order_blocks[-3:]:  # Only last 3 order blocks
                    if (ob.direction == "BULLISH" and 
                        ob.start_price <= current_price <= ob.end_price and
                        ob.strength > 0.6):  # Must be strong order block
                        
                        # For BUY signals: SL below entry, TP above entry
                        stop_loss = ob.start_price * 0.99
                        take_profit = current_price + (current_price - stop_loss) * 2.0  # Better R:R
                        risk_reward = (take_profit - current_price) / (current_price - stop_loss)
                        
                        # STRICT validation - only high-quality setups
                        if (stop_loss < current_price < take_profit and 
                            risk_reward >= 2.0 and  # Minimum 2:1 R:R
                            signals_generated < max_signals_per_symbol):
                            
                            signals.append(LiveSignal(
                                symbol=symbol,
                                signal_type=SignalType.BUY,
                                entry_price=current_price,
                                stop_loss=stop_loss,
                                take_profit=take_profit,
                                confidence=min(0.85, fvg.strength * 8),  # Lower confidence
                                pattern=f"Strong FVG + OrderBlock",
                                timestamp=df.index[-1],
                                timeframe=timeframe,
                                risk_reward=risk_reward
                            ))
                            signals_generated += 1
                            break  # Only one signal per symbol
            
            elif fvg.direction == "BEARISH" and market_structure["structure"] == "BEARISH":
                # Look for STRONG bearish order block resistance
                for ob in order_blocks[-3:]:
                    if (ob.direction == "BEARISH" and 
                        ob.start_price <= current_price <= ob.end_price and
                        ob.strength > 0.6):
                        
                        # For SELL signals: SL above entry, TP below entry
                        stop_loss = ob.end_price * 1.01
                        take_profit = current_price - (stop_loss - current_price) * 2.0
                        risk_reward = (current_price - take_profit) / (stop_loss - current_price)
                        
                        # STRICT validation
                        if (take_profit < current_price < stop_loss and 
                            risk_reward >= 2.0 and
                            signals_generated < max_signals_per_symbol):
                            
                            signals.append(LiveSignal(
                                symbol=symbol,
                                signal_type=SignalType.SELL,
                                entry_price=current_price,
                                stop_loss=stop_loss,
                                take_profit=take_profit,
                                confidence=min(0.85, fvg.strength * 8),
                                pattern=f"Strong FVG + OrderBlock",
                                timestamp=df.index[-1],
                                timeframe=timeframe,
                                risk_reward=risk_reward
                            ))
                            signals_generated += 1
                            break
        
        # Only add liquidity sweep signals if NO other signals were generated
        if signals_generated == 0 and liquidity_sweeps:
            sweep = liquidity_sweeps[-1]  # Only check the strongest sweep
            if sweep.strength > 0.8:  # Must be very strong
                stop_loss = sweep.start_price * 0.98
                take_profit = current_price + (current_price - stop_loss) * 2.5
                risk_reward = (take_profit - current_price) / (current_price - stop_loss)
                
                if risk_reward >= 2.5:  # High R:R requirement
                    signals.append(LiveSignal(
                        symbol=symbol,
                        signal_type=SignalType.BUY,
                        entry_price=current_price,
                        stop_loss=stop_loss,
                        take_profit=take_profit,
                        confidence=min(0.75, sweep.strength * 15),
                        pattern="Strong LiquiditySweep",
                        timestamp=df.index[-1],
                        timeframe=timeframe,
                        risk_reward=risk_reward
                    ))
        
        return signals
    
    def get_pattern_summary(self, df: pd.DataFrame) -> Dict:
        """Get summary of all detected patterns"""
        fvgs = self.detect_fair_value_gaps(df)
        order_blocks = self.detect_order_blocks(df)
        liquidity_sweeps = self.detect_liquidity_sweeps(df)
        market_structure = self.analyze_market_structure(df)
        
        return {
            "fair_value_gaps": len(fvgs),
            "order_blocks": len(order_blocks),
            "liquidity_sweeps": len(liquidity_sweeps),
            "market_structure": market_structure,
            "total_patterns": len(fvgs) + len(order_blocks) + len(liquidity_sweeps),
            "last_updated": df.index[-1]
        }
