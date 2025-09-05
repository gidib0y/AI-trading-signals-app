import asyncio
import pandas as pd
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import logging
from app.services.ict_smc_service import ICTSMCAnalyzer, LiveSignal
from app.utils.data_fetcher import DataFetcher

logger = logging.getLogger(__name__)

class LiveMarketMonitor:
    def __init__(self):
        self.ict_analyzer = ICTSMCAnalyzer()
        self.data_fetcher = DataFetcher()
        self.monitored_symbols = []
        self.live_signals = {}
        self.is_monitoring = False
        self.monitoring_task = None
        
    async def start_monitoring(self, symbols: List[str], timeframes: List[str] = ["1m", "5m", "15m"]):
        """Start live market monitoring"""
        if self.is_monitoring:
            logger.warning("Monitoring already active")
            return
            
        self.monitored_symbols = symbols
        self.is_monitoring = True
        
        logger.info(f"Starting live monitoring for {len(symbols)} symbols")
        
        # Start monitoring in background
        self.monitoring_task = asyncio.create_task(self._monitor_loop(timeframes))
        
    async def stop_monitoring(self):
        """Stop live market monitoring"""
        if not self.is_monitoring:
            return
            
        self.is_monitoring = False
        if self.monitoring_task:
            self.monitoring_task.cancel()
            try:
                await self.monitoring_task
            except asyncio.CancelledError:
                pass
        
        logger.info("Live monitoring stopped")
    
    async def _monitor_loop(self, timeframes: List[str]):
        """Main monitoring loop"""
        while self.is_monitoring:
            try:
                for symbol in self.monitored_symbols:
                    for timeframe in timeframes:
                        await self._analyze_symbol(symbol, timeframe)
                
                # Wait before next analysis cycle
                await asyncio.sleep(60)  # Check every minute
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(30)  # Wait before retry
    
    async def _analyze_symbol(self, symbol: str, timeframe: str):
        """Analyze a single symbol for live signals"""
        try:
            # Fetch recent data based on timeframe
            if timeframe == "1m":
                period = "1d"
                data_points = 1440  # 24 hours * 60 minutes
            elif timeframe == "5m":
                period = "5d"
                data_points = 1440  # 5 days * 288 5-minute bars
            elif timeframe == "15m":
                period = "15d"
                data_points = 1440  # 15 days * 96 15-minute bars
            else:
                period = "1d"
                data_points = 250
            
            # Fetch data - use appropriate method based on symbol type
            if symbol in ['XAU/USD', 'XAG/USD', 'XPT/USD', 'XPD/USD']:
                # Metals - use Alpha Vantage
                metal_code = symbol.split('/')[0]  # Extract XAU, XAG, etc.
                data = await self.data_fetcher.fetch_metal_data(metal_code, period)
                if data is not None:
                    data = self.data_fetcher._dataframe_to_list(data)
            elif '/' in symbol and symbol not in ['BTC/USD', 'ETH/USD']:
                # Forex pairs - use Alpha Vantage
                from_currency, to_currency = symbol.split('/')
                data = await self.data_fetcher.fetch_forex_data(from_currency, to_currency, period)
                if data is not None:
                    data = self.data_fetcher._dataframe_to_list(data)
            else:
                # Stocks and crypto - use yfinance
                data = await self.data_fetcher.fetch_data_async(symbol, period, data_points)
            
            if data is None or len(data) < 100:
                return
            
            # Convert to DataFrame
            df = pd.DataFrame(data)
            df['Date'] = pd.to_datetime(df['Date'])
            df.set_index('Date', inplace=True)
            
            # Generate live signals
            signals = self.ict_analyzer.generate_live_signals(df, symbol, timeframe)
            
            if signals:
                # Store signals with timestamp
                key = f"{symbol}_{timeframe}"
                self.live_signals[key] = {
                    "signals": signals,
                    "last_updated": datetime.now(),
                    "data": df.tail(100).to_dict('records')  # Keep last 100 bars
                }
                
                logger.info(f"Generated {len(signals)} live signals for {symbol} ({timeframe})")
                
        except Exception as e:
            logger.error(f"Error analyzing {symbol} ({timeframe}): {e}")
    
    def get_live_signals(self, symbol: Optional[str] = None, timeframe: Optional[str] = None) -> Dict:
        """Get current live signals"""
        if symbol and timeframe:
            key = f"{symbol}_{timeframe}"
            return self.live_signals.get(key, {})
        elif symbol:
            # Return all timeframes for a symbol
            result = {}
            for key, value in self.live_signals.items():
                if key.startswith(f"{symbol}_"):
                    result[key] = value
            return result
        else:
            return self.live_signals
    
    def get_signal_summary(self) -> Dict:
        """Get summary of all live signals"""
        total_signals = 0
        buy_signals = 0
        sell_signals = 0
        symbols_with_signals = set()
        
        for key, data in self.live_signals.items():
            if "signals" in data:
                signals = data["signals"]
                total_signals += len(signals)
                
                for signal in signals:
                    if signal.signal_type.value == "BUY":
                        buy_signals += 1
                    elif signal.signal_type.value == "SELL":
                        sell_signals += 1
                
                symbol = key.split("_")[0]
                symbols_with_signals.add(symbol)
        
        return {
            "total_signals": total_signals,
            "buy_signals": buy_signals,
            "sell_signals": sell_signals,
            "symbols_with_signals": list(symbols_with_signals),
            "monitored_symbols": self.monitored_symbols,
            "is_monitoring": self.is_monitoring,
            "last_updated": datetime.now()
        }
    
    def add_symbol(self, symbol: str):
        """Add a new symbol to monitoring"""
        if symbol not in self.monitored_symbols:
            self.monitored_symbols.append(symbol)
            logger.info(f"Added {symbol} to monitoring")
    
    def remove_symbol(self, symbol: str):
        """Remove a symbol from monitoring"""
        if symbol in self.monitored_symbols:
            self.monitored_symbols.remove(symbol)
            # Remove related signals
            keys_to_remove = [key for key in self.live_signals.keys() if key.startswith(f"{symbol}_")]
            for key in keys_to_remove:
                del self.live_signals[key]
            logger.info(f"Removed {symbol} from monitoring")
    
    async def force_analysis(self, symbol: str, timeframe: str = "5m"):
        """Force immediate analysis of a symbol"""
        await self._analyze_symbol(symbol, timeframe)
        return self.get_live_signals(symbol, timeframe)
