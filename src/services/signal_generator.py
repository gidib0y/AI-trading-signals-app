import logging
from datetime import datetime, timedelta
from typing import Dict, Optional, List
import yfinance as yf
import pandas as pd
import numpy as np

from src.database import TechnicalIndicators, SentimentData, MarketData

logger = logging.getLogger(__name__)

class SignalGenerator:
    """Service for generating trading signals based on multiple factors"""
    
    def __init__(self):
        self.min_confidence_threshold = 70.0
        self.signal_types = ["BUY", "SELL", "HOLD"]
        
    async def generate_signals(self) -> List[Dict]:
        """Generate trading signals for all monitored symbols"""
        try:
            logger.info("Starting signal generation...")
            
            # This would typically get symbols from the database
            # For now, we'll use a predefined list
            symbols = ["AAPL", "GOOGL", "MSFT", "TSLA", "AMZN", "NVDA", "META"]
            
            generated_signals = []
            
            for symbol in symbols:
                try:
                    signal = await self.generate_signal_for_symbol(symbol)
                    if signal and signal['confidence_score'] >= self.min_confidence_threshold:
                        generated_signals.append(signal)
                        
                except Exception as e:
                    logger.error(f"Error generating signal for {symbol}: {e}")
                    continue
            
            logger.info(f"Signal generation completed. Generated {len(generated_signals)} signals.")
            return generated_signals
            
        except Exception as e:
            logger.error(f"Error in signal generation: {e}")
            return []
    
    async def generate_signal_for_symbol(self, symbol: str, db=None) -> Optional[Dict]:
        """Generate a trading signal for a specific symbol"""
        try:
            # Get market data
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="3mo")
            
            if hist.empty:
                return None
            
            # Calculate technical analysis score
            technical_score = await self.calculate_technical_score(symbol, hist)
            
            # Calculate sentiment score
            sentiment_score = await self.calculate_sentiment_score(symbol)
            
            # Calculate volume and momentum score
            volume_score = await self.calculate_volume_score(hist)
            
            # Combine scores to determine signal type and confidence
            signal_data = self.combine_scores(
                symbol, technical_score, sentiment_score, volume_score, hist
            )
            
            if signal_data:
                # Calculate price targets and stop loss
                signal_data.update(
                    self.calculate_price_targets(symbol, signal_data['signal_type'], hist)
                )
                
                # Generate reasoning
                signal_data['reasoning'] = self.generate_reasoning(
                    signal_data, technical_score, sentiment_score, volume_score
                )
                
                return signal_data
            
            return None
            
        except Exception as e:
            logger.error(f"Error generating signal for {symbol}: {e}")
            return None
    
    async def calculate_technical_score(self, symbol: str, hist: pd.DataFrame) -> Dict:
        """Calculate technical analysis score"""
        try:
            close = hist['Close']
            high = hist['High']
            low = hist['Low']
            volume = hist['Volume']
            
            score = 0
            signals = []
            
            # RSI Analysis
            rsi = self.calculate_rsi(close)
            if rsi < 30:
                score += 25
                signals.append("RSI oversold (< 30)")
            elif rsi > 70:
                score += 20
                signals.append("RSI overbought (> 70)")
            
            # Moving Averages
            sma_20 = close.rolling(window=20).mean().iloc[-1]
            sma_50 = close.rolling(window=50).mean().iloc[-1]
            ema_12 = close.ewm(span=12).mean().iloc[-1]
            ema_26 = close.ewm(span=26).mean().iloc[-1]
            
            current_price = close.iloc[-1]
            
            # Price vs Moving Averages
            if current_price > sma_20:
                score += 15
                signals.append("Price above 20-day SMA")
            else:
                score += 10
                signals.append("Price below 20-day SMA")
            
            if current_price > sma_50:
                score += 15
                signals.append("Price above 50-day SMA")
            else:
                score += 10
                signals.append("Price below 50-day SMA")
            
            # Golden/Death Cross
            if sma_20 > sma_50:
                score += 20
                signals.append("Golden cross (20 SMA > 50 SMA)")
            else:
                score += 15
                signals.append("Death cross (20 SMA < 50 SMA)")
            
            # EMA Analysis
            if ema_12 > ema_26:
                score += 15
                signals.append("EMA 12 > EMA 26 (bullish)")
            else:
                score += 10
                signals.append("EMA 12 < EMA 26 (bearish)")
            
            # Bollinger Bands
            bb_upper, bb_middle, bb_lower = self.calculate_bollinger_bands(close)
            
            if current_price > bb_upper:
                score += 20
                signals.append("Price above upper Bollinger Band")
            elif current_price < bb_lower:
                score += 25
                signals.append("Price below lower Bollinger Band")
            else:
                score += 15
                signals.append("Price within Bollinger Bands")
            
            # MACD
            macd, macd_signal, macd_histogram = self.calculate_macd(close)
            
            if macd > macd_signal:
                score += 20
                signals.append("MACD above signal line")
            else:
                score += 15
                signals.append("MACD below signal line")
            
            # Stochastic
            stoch_k, stoch_d = self.calculate_stochastic(high, low, close)
            
            if stoch_k < 20:
                score += 20
                signals.append("Stochastic oversold (< 20)")
            elif stoch_k > 80:
                score += 15
                signals.append("Stochastic overbought (> 80)")
            else:
                score += 10
                signals.append("Stochastic neutral")
            
            # ATR for volatility
            atr = self.calculate_atr(high, low, close)
            avg_atr = atr.rolling(window=14).mean().iloc[-1]
            
            if atr.iloc[-1] > avg_atr * 1.5:
                score += 15
                signals.append("High volatility (ATR > 1.5x average)")
            else:
                score += 10
                signals.append("Normal volatility")
            
            # Normalize score to 0-100
            normalized_score = min(max(score, 0), 100)
            
            return {
                "score": normalized_score,
                "signals": signals,
                "indicators": {
                    "rsi": round(rsi, 2),
                    "sma_20": round(sma_20, 2),
                    "sma_50": round(sma_50, 2),
                    "ema_12": round(ema_12, 2),
                    "ema_26": round(ema_26, 2),
                    "bb_upper": round(bb_upper, 2),
                    "bb_middle": round(bb_middle, 2),
                    "bb_lower": round(bb_lower, 2),
                    "macd": round(macd, 4),
                    "macd_signal": round(macd_signal, 4),
                    "stoch_k": round(stoch_k, 2),
                    "stoch_d": round(stoch_d, 2),
                    "atr": round(atr.iloc[-1], 2)
                }
            }
            
        except Exception as e:
            logger.error(f"Error calculating technical score for {symbol}: {e}")
            return {"score": 50, "signals": [], "indicators": {}}
    
    async def calculate_sentiment_score(self, symbol: str) -> Dict:
        """Calculate sentiment analysis score"""
        try:
            # In a real implementation, this would fetch from the database
            # For now, we'll simulate sentiment analysis
            
            # Simulate different sentiment scenarios
            import random
            random.seed(hash(symbol) % 1000)  # Consistent for each symbol
            
            news_sentiment = random.uniform(-0.5, 0.5)
            social_sentiment = random.uniform(-0.5, 0.5)
            fear_greed = random.randint(20, 80)
            
            # Calculate overall sentiment score (0-100)
            news_score = (news_sentiment + 1) * 50
            social_score = (social_sentiment + 1) * 50
            
            overall_score = (news_score * 0.4) + (social_score * 0.3) + (fear_greed * 0.3)
            
            # Categorize sentiment
            if overall_score >= 70:
                category = "VERY_BULLISH"
            elif overall_score >= 60:
                category = "BULLISH"
            elif overall_score >= 40:
                category = "NEUTRAL"
            elif overall_score >= 30:
                category = "BEARISH"
            else:
                category = "VERY_BEARISH"
            
            return {
                "score": round(overall_score, 1),
                "category": category,
                "components": {
                    "news": round(news_score, 1),
                    "social": round(social_score, 1),
                    "fear_greed": fear_greed
                }
            }
            
        except Exception as e:
            logger.error(f"Error calculating sentiment score for {symbol}: {e}")
            return {"score": 50, "category": "NEUTRAL", "components": {}}
    
    async def calculate_volume_score(self, hist: pd.DataFrame) -> Dict:
        """Calculate volume and momentum score"""
        try:
            volume = hist['Volume']
            close = hist['Close']
            
            score = 0
            signals = []
            
            # Volume analysis
            current_volume = volume.iloc[-1]
            avg_volume = volume.rolling(window=20).mean().iloc[-1]
            volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1
            
            if volume_ratio > 2.0:
                score += 25
                signals.append("Very high volume (> 2x average)")
            elif volume_ratio > 1.5:
                score += 20
                signals.append("High volume (> 1.5x average)")
            elif volume_ratio > 1.0:
                score += 15
                signals.append("Above average volume")
            else:
                score += 10
                signals.append("Below average volume")
            
            # Price momentum
            price_change_1d = ((close.iloc[-1] - close.iloc[-2]) / close.iloc[-2]) * 100 if len(close) > 1 else 0
            price_change_5d = ((close.iloc[-1] - close.iloc[-5]) / close.iloc[-5]) * 100 if len(close) > 5 else 0
            
            if price_change_1d > 3:
                score += 20
                signals.append("Strong 1-day momentum (> 3%)")
            elif price_change_1d > 1:
                score += 15
                signals.append("Positive 1-day momentum (> 1%)")
            elif price_change_1d < -3:
                score += 15
                signals.append("Strong 1-day decline (> 3%)")
            elif price_change_1d < -1:
                score += 10
                signals.append("Negative 1-day momentum (> 1%)")
            
            if price_change_5d > 10:
                score += 20
                signals.append("Strong 5-day momentum (> 10%)")
            elif price_change_5d > 5:
                score += 15
                signals.append("Positive 5-day momentum (> 5%)")
            elif price_change_5d < -10:
                score += 15
                signals.append("Strong 5-day decline (> 10%)")
            elif price_change_5d < -5:
                score += 10
                signals.append("Negative 5-day momentum (> 5%)")
            
            # Volume price trend
            if price_change_1d > 0 and volume_ratio > 1.2:
                score += 20
                signals.append("Price up with high volume (bullish)")
            elif price_change_1d < 0 and volume_ratio > 1.2:
                score += 15
                signals.append("Price down with high volume (bearish)")
            elif price_change_1d > 0 and volume_ratio < 0.8:
                score += 10
                signals.append("Price up with low volume (weak)")
            elif price_change_1d < 0 and volume_ratio < 0.8:
                score += 10
                signals.append("Price down with low volume (weak)")
            
            # Normalize score to 0-100
            normalized_score = min(max(score, 0), 100)
            
            return {
                "score": normalized_score,
                "signals": signals,
                "metrics": {
                    "volume_ratio": round(volume_ratio, 2),
                    "price_change_1d": round(price_change_1d, 2),
                    "price_change_5d": round(price_change_5d, 2)
                }
            }
            
        except Exception as e:
            logger.error(f"Error calculating volume score: {e}")
            return {"score": 50, "signals": [], "metrics": {}}
    
    def combine_scores(self, symbol: str, technical: Dict, sentiment: Dict, 
                      volume: Dict, hist: pd.DataFrame) -> Optional[Dict]:
        """Combine all scores to determine signal type and confidence"""
        try:
            technical_score = technical.get('score', 50)
            sentiment_score = sentiment.get('score', 50)
            volume_score = volume.get('score', 50)
            
            # Weighted average (technical: 50%, sentiment: 30%, volume: 20%)
            overall_score = (
                technical_score * 0.5 + 
                sentiment_score * 0.3 + 
                volume_score * 0.2
            )
            
            # Determine signal type based on overall score
            if overall_score >= 75:
                signal_type = "BUY"
            elif overall_score <= 25:
                signal_type = "SELL"
            else:
                signal_type = "HOLD"
            
            # Calculate confidence score
            confidence_score = min(max(overall_score, 0), 100)
            
            # Only generate signals with sufficient confidence
            if confidence_score >= self.min_confidence_threshold:
                return {
                    "symbol": symbol,
                    "signal_type": signal_type,
                    "confidence_score": round(confidence_score, 1),
                    "technical_score": round(technical_score, 1),
                    "sentiment_score": round(sentiment_score, 1),
                    "volume_score": round(volume_score, 1),
                    "overall_score": round(overall_score, 1),
                    "timestamp": datetime.now().isoformat()
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error combining scores for {symbol}: {e}")
            return None
    
    def calculate_price_targets(self, symbol: str, signal_type: str, hist: pd.DataFrame) -> Dict:
        """Calculate price targets and stop loss levels"""
        try:
            current_price = hist['Close'].iloc[-1]
            atr = self.calculate_atr(hist['High'], hist['Low'], hist['Close'])
            current_atr = atr.iloc[-1]
            
            if signal_type == "BUY":
                # Bullish targets
                price_target = current_price * 1.15  # 15% upside
                stop_loss = current_price - (current_atr * 2)  # 2 ATR below
            elif signal_type == "SELL":
                # Bearish targets
                price_target = current_price * 0.85  # 15% downside
                stop_loss = current_price + (current_atr * 2)  # 2 ATR above
            else:
                # HOLD signal
                price_target = current_price
                stop_loss = current_price
            
            return {
                "price_target": round(price_target, 2),
                "stop_loss": round(stop_loss, 2)
            }
            
        except Exception as e:
            logger.error(f"Error calculating price targets for {symbol}: {e}")
            return {
                "price_target": 0,
                "stop_loss": 0
            }
    
    def generate_reasoning(self, signal_data: Dict, technical: Dict, 
                          sentiment: Dict, volume: Dict) -> str:
        """Generate human-readable reasoning for the signal"""
        try:
            symbol = signal_data['symbol']
            signal_type = signal_data['signal_type']
            confidence = signal_data['confidence_score']
            
            reasoning_parts = [
                f"Signal: {signal_type} {symbol} with {confidence}% confidence."
            ]
            
            # Add technical reasoning
            if technical.get('signals'):
                tech_signals = technical['signals'][:3]  # Top 3 signals
                reasoning_parts.append(f"Technical: {', '.join(tech_signals)}.")
            
            # Add sentiment reasoning
            if sentiment.get('category'):
                reasoning_parts.append(f"Sentiment: {sentiment['category'].lower()}.")
            
            # Add volume reasoning
            if volume.get('signals'):
                vol_signals = volume['signals'][:2]  # Top 2 signals
                reasoning_parts.append(f"Volume: {', '.join(vol_signals)}.")
            
            # Add price targets
            if signal_data.get('price_target') and signal_data.get('stop_loss'):
                reasoning_parts.append(
                    f"Target: ${signal_data['price_target']}, Stop Loss: ${signal_data['stop_loss']}."
                )
            
            return " ".join(reasoning_parts)
            
        except Exception as e:
            logger.error(f"Error generating reasoning: {e}")
            return f"Generated {signal_data.get('signal_type', 'signal')} signal for {signal_data.get('symbol', 'symbol')}."
    
    # Helper methods for technical indicators
    def calculate_rsi(self, close: pd.Series, period: int = 14) -> float:
        """Calculate RSI indicator"""
        try:
            delta = close.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            return rsi.iloc[-1]
        except:
            return 50.0
    
    def calculate_bollinger_bands(self, close: pd.Series, period: int = 20, std_dev: int = 2) -> tuple:
        """Calculate Bollinger Bands"""
        try:
            sma = close.rolling(window=period).mean()
            std = close.rolling(window=period).std()
            upper = sma + (std * std_dev)
            lower = sma - (std * std_dev)
            return upper.iloc[-1], sma.iloc[-1], lower.iloc[-1]
        except:
            return close.iloc[-1], close.iloc[-1], close.iloc[-1]
    
    def calculate_macd(self, close: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> tuple:
        """Calculate MACD"""
        try:
            ema_fast = close.ewm(span=fast).mean()
            ema_slow = close.ewm(span=slow).mean()
            macd_line = ema_fast - ema_slow
            signal_line = macd_line.ewm(span=signal).mean()
            histogram = macd_line - signal_line
            return macd_line.iloc[-1], signal_line.iloc[-1], histogram.iloc[-1]
        except:
            return 0, 0, 0
    
    def calculate_stochastic(self, high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> tuple:
        """Calculate Stochastic Oscillator"""
        try:
            lowest_low = low.rolling(window=period).min()
            highest_high = high.rolling(window=period).max()
            k_percent = 100 * ((close - lowest_low) / (highest_high - lowest_low))
            d_percent = k_percent.rolling(window=3).mean()
            return k_percent.iloc[-1], d_percent.iloc[-1]
        except:
            return 50, 50
    
    def calculate_atr(self, high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> pd.Series:
        """Calculate Average True Range"""
        try:
            tr1 = high - low
            tr2 = abs(high - close.shift())
            tr3 = abs(low - close.shift())
            tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
            atr = tr.rolling(window=period).mean()
            return atr
        except:
            return pd.Series([0])

