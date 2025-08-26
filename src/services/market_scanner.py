import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import yfinance as yf
import pandas as pd
import numpy as np

from src.database import MarketData, TechnicalIndicators, SentimentData

logger = logging.getLogger(__name__)

class MarketScanner:
    """Service for scanning markets and identifying trading opportunities"""
    
    def __init__(self):
        self.monitored_symbols = [
            "AAPL", "GOOGL", "MSFT", "TSLA", "AMZN", "NVDA", "META", "NFLX", "AMD", "INTC",
            "SPY", "QQQ", "IWM", "VTI", "VOO", "VEA", "VWO", "BND", "GLD", "SLV",
            "BTC-USD", "ETH-USD", "ADA-USD", "DOT-USD", "LINK-USD"
        ]
        self.scan_interval = 300  # 5 minutes
        self.last_scan = None
        
    async def scan_markets(self) -> List[Dict]:
        """Scan all monitored markets for opportunities"""
        try:
            logger.info("Starting market scan...")
            opportunities = []
            
            for symbol in self.monitored_symbols:
                try:
                    opportunity = await self.scan_symbol(symbol)
                    if opportunity:
                        opportunities.append(opportunity)
                        
                    # Small delay to avoid overwhelming APIs
                    await asyncio.sleep(0.1)
                    
                except Exception as e:
                    logger.error(f"Error scanning {symbol}: {e}")
                    continue
            
            self.last_scan = datetime.now()
            logger.info(f"Market scan completed. Found {len(opportunities)} opportunities.")
            
            return opportunities
            
        except Exception as e:
            logger.error(f"Error in market scan: {e}")
            return []
    
    async def scan_symbol(self, symbol: str) -> Optional[Dict]:
        """Scan a specific symbol for trading opportunities"""
        try:
            # Get market data
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="1mo")
            
            if hist.empty:
                return None
            
            # Get current market info
            current_price = hist['Close'].iloc[-1]
            prev_price = hist['Close'].iloc[-2] if len(hist) > 1 else current_price
            volume = hist['Volume'].iloc[-1]
            
            # Calculate basic metrics
            price_change = current_price - prev_price
            price_change_pct = (price_change / prev_price) * 100
            
            # Get additional info
            info = ticker.info
            market_cap = info.get('marketCap', 0)
            
            # Calculate technical indicators
            technical_analysis = self.calculate_basic_indicators(hist)
            
            # Identify opportunities based on criteria
            opportunity = self.identify_opportunity(
                symbol, current_price, price_change_pct, volume, 
                market_cap, technical_analysis, hist
            )
            
            if opportunity:
                # Store market data
                await self.store_market_data(symbol, hist, market_cap)
                return opportunity
            
            return None
            
        except Exception as e:
            logger.error(f"Error scanning symbol {symbol}: {e}")
            return None
    
    def calculate_basic_indicators(self, hist: pd.DataFrame) -> Dict:
        """Calculate basic technical indicators"""
        try:
            close = hist['Close']
            high = hist['High']
            low = hist['Low']
            volume = hist['Volume']
            
            # RSI
            rsi = self.calculate_rsi(close)
            
            # Moving Averages
            sma_20 = close.rolling(window=20).mean().iloc[-1]
            sma_50 = close.rolling(window=50).mean().iloc[-1]
            
            # Bollinger Bands
            bb_upper, bb_middle, bb_lower = self.calculate_bollinger_bands(close)
            
            # Volume analysis
            avg_volume = volume.rolling(window=20).mean().iloc[-1]
            volume_ratio = volume.iloc[-1] / avg_volume if avg_volume > 0 else 1
            
            return {
                "rsi": rsi,
                "sma_20": sma_20,
                "sma_50": sma_50,
                "bb_upper": bb_upper,
                "bb_middle": bb_middle,
                "bb_lower": bb_lower,
                "volume_ratio": volume_ratio,
                "price_vs_sma20": (close.iloc[-1] / sma_20 - 1) * 100 if sma_20 > 0 else 0,
                "price_vs_sma50": (close.iloc[-1] / sma_50 - 1) * 100 if sma_50 > 0 else 0
            }
            
        except Exception as e:
            logger.error(f"Error calculating indicators: {e}")
            return {}
    
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
    
    def identify_opportunity(self, symbol: str, current_price: float, price_change_pct: float,
                           volume: float, market_cap: float, technical: Dict, hist: pd.DataFrame) -> Optional[Dict]:
        """Identify trading opportunities based on criteria"""
        try:
            opportunity_score = 0
            reasons = []
            
            # Price momentum
            if price_change_pct > 2:
                opportunity_score += 20
                reasons.append("Strong positive momentum")
            elif price_change_pct < -2:
                opportunity_score += 15
                reasons.append("Oversold conditions")
            
            # RSI analysis
            if technical.get('rsi'):
                rsi = technical['rsi']
                if rsi < 30:
                    opportunity_score += 25
                    reasons.append("RSI oversold (< 30)")
                elif rsi > 70:
                    opportunity_score += 20
                    reasons.append("RSI overbought (> 70)")
            
            # Moving average analysis
            if technical.get('sma_20') and technical.get('sma_50'):
                if technical['price_vs_sma20'] > 5:
                    opportunity_score += 15
                    reasons.append("Price above 20-day SMA")
                elif technical['price_vs_sma20'] < -5:
                    opportunity_score += 15
                    reasons.append("Price below 20-day SMA")
                
                if technical['sma_20'] > technical['sma_50']:
                    opportunity_score += 10
                    reasons.append("Golden cross (20 SMA > 50 SMA)")
                else:
                    opportunity_score += 5
                    reasons.append("Death cross (20 SMA < 50 SMA)")
            
            # Bollinger Bands analysis
            if technical.get('bb_upper') and technical.get('bb_lower'):
                if current_price > technical['bb_upper']:
                    opportunity_score += 15
                    reasons.append("Price above upper Bollinger Band")
                elif current_price < technical['bb_lower']:
                    opportunity_score += 20
                    reasons.append("Price below lower Bollinger Band")
            
            # Volume analysis
            if technical.get('volume_ratio'):
                if technical['volume_ratio'] > 1.5:
                    opportunity_score += 15
                    reasons.append("High volume (above average)")
                elif technical['volume_ratio'] < 0.5:
                    opportunity_score += 10
                    reasons.append("Low volume (below average)")
            
            # Market cap filter
            if market_cap > 10000000000:  # $10B
                opportunity_score += 5
                reasons.append("Large cap stock")
            elif market_cap > 1000000000:  # $1B
                opportunity_score += 10
                reasons.append("Mid cap stock")
            else:
                opportunity_score += 15
                reasons.append("Small cap stock")
            
            # Only return opportunities with sufficient score
            if opportunity_score >= 50:
                return {
                    "symbol": symbol,
                    "current_price": round(current_price, 2),
                    "price_change_pct": round(price_change_pct, 2),
                    "opportunity_score": opportunity_score,
                    "reasons": reasons,
                    "technical_summary": {
                        "rsi": round(technical.get('rsi', 0), 2),
                        "sma_20": round(technical.get('sma_20', 0), 2),
                        "sma_50": round(technical.get('sma_50', 0), 2),
                        "volume_ratio": round(technical.get('volume_ratio', 1), 2)
                    },
                    "timestamp": datetime.now().isoformat()
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error identifying opportunity for {symbol}: {e}")
            return None
    
    async def store_market_data(self, symbol: str, hist: pd.DataFrame, market_cap: float):
        """Store market data in database"""
        try:
            # This would typically be done through the database session
            # For now, we'll just log the action
            logger.debug(f"Storing market data for {symbol}")
            
        except Exception as e:
            logger.error(f"Error storing market data for {symbol}: {e}")
    
    async def get_market_overview(self) -> Dict:
        """Get market overview and summary"""
        try:
            # Get major indices
            indices = {
                "SPY": "S&P 500",
                "QQQ": "NASDAQ 100",
                "IWM": "Russell 2000",
                "DIA": "Dow Jones"
            }
            
            overview = {}
            for symbol, name in indices.items():
                try:
                    ticker = yf.Ticker(symbol)
                    hist = ticker.history(period="1d")
                    
                    if not hist.empty:
                        current_price = hist['Close'].iloc[-1]
                        prev_price = hist['Open'].iloc[0]
                        change_pct = ((current_price - prev_price) / prev_price) * 100
                        
                        overview[symbol] = {
                            "name": name,
                            "price": round(current_price, 2),
                            "change_pct": round(change_pct, 2),
                            "trend": "UP" if change_pct > 0 else "DOWN" if change_pct < 0 else "FLAT"
                        }
                        
                except Exception as e:
                    logger.error(f"Error getting {symbol} data: {e}")
                    continue
            
            return {
                "market_overview": overview,
                "scan_status": {
                    "last_scan": self.last_scan.isoformat() if self.last_scan else None,
                    "monitored_symbols": len(self.monitored_symbols),
                    "scan_interval_minutes": self.scan_interval // 60
                },
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting market overview: {e}")
            return {}
    
    def add_symbol_to_monitor(self, symbol: str):
        """Add a new symbol to monitor"""
        if symbol.upper() not in self.monitored_symbols:
            self.monitored_symbols.append(symbol.upper())
            logger.info(f"Added {symbol} to monitored symbols")
    
    def remove_symbol_from_monitor(self, symbol: str):
        """Remove a symbol from monitoring"""
        if symbol.upper() in self.monitored_symbols:
            self.monitored_symbols.remove(symbol.upper())
            logger.info(f"Removed {symbol} from monitored symbols")
    
    def get_monitored_symbols(self) -> List[str]:
        """Get list of currently monitored symbols"""
        return self.monitored_symbols.copy()

