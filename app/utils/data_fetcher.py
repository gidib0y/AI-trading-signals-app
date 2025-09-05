import yfinance as yf
import pandas as pd
import asyncio
from typing import Optional
import logging
from datetime import datetime, timedelta
from app.services.alpha_vantage_service import AlphaVantageService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataFetcher:
    """Utility class for fetching market data from various sources"""
    
    def __init__(self):
        self.cache = {}
        self.cache_duration = timedelta(minutes=5)  # Cache data for 5 minutes
        self.alpha_vantage = AlphaVantageService()
    
    async def fetch_data(self, symbol: str, period: str = "1y") -> pd.DataFrame:
        """Fetch historical market data for a given symbol"""
        try:
            # Check cache first
            cache_key = f"{symbol}_{period}"
            if self._is_cache_valid(cache_key):
                logger.info(f"Using cached data for {symbol}")
                return self.cache[cache_key]['data']
            
            logger.info(f"Fetching data for {symbol} for period {period}")
            
            # Fetch data using yfinance
            ticker = yf.Ticker(symbol)
            data = ticker.history(period=period)
            
            if data.empty:
                logger.warning(f"No data found for {symbol}")
                return pd.DataFrame()
            
            # Clean and validate data
            data = self._clean_data(data)
            
            # Cache the data
            self._cache_data(cache_key, data)
            
            logger.info(f"Successfully fetched {len(data)} data points for {symbol}")
            return data
            
        except Exception as e:
            logger.error(f"Error fetching data for {symbol}: {e}")
            return pd.DataFrame()
    
    async def fetch_data_async(self, symbol: str, period: str = "1d", data_points: int = 250) -> Optional[list]:
        """Fetch data asynchronously and return as list for live monitoring"""
        try:
            # Check cache first
            cache_key = f"{symbol}_{period}_{data_points}"
            if self._is_cache_valid(cache_key):
                logger.info(f"Using cached data for {symbol}")
                cached_data = self.cache[cache_key]['data']
                return self._dataframe_to_list(cached_data)
            
            logger.info(f"Fetching data for {symbol} for period {period}")
            
            # Fetch data using yfinance
            ticker = yf.Ticker(symbol)
            data = ticker.history(period=period, interval="1m" if period == "1d" else "5m")
            
            if data.empty:
                logger.warning(f"No data found for {symbol}")
                return None
            
            # Clean and validate data
            data = self._clean_data(data)
            
            # Limit to requested data points
            if len(data) > data_points:
                data = data.tail(data_points)
            
            # Cache the data
            self._cache_data(cache_key, data)
            
            logger.info(f"Successfully fetched {len(data)} data points for {symbol}")
            return self._dataframe_to_list(data)
            
        except Exception as e:
            logger.error(f"Error fetching data for {symbol}: {e}")
            return None
    
    def _dataframe_to_list(self, df: pd.DataFrame) -> list:
        """Convert DataFrame to list of dictionaries for JSON serialization"""
        df_copy = df.reset_index()
        df_copy['Date'] = df_copy.index.astype(str)
        return df_copy.to_dict('records')
    
    def _clean_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """Clean and validate the fetched data"""
        # Remove rows with missing values
        data = data.dropna()
        
        # Ensure we have the required columns
        required_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
        missing_columns = [col for col in required_columns if col not in data.columns]
        
        if missing_columns:
            logger.warning(f"Missing columns: {missing_columns}")
            return pd.DataFrame()
        
        # Convert to numeric types
        for col in required_columns:
            data[col] = pd.to_numeric(data[col], errors='coerce')
        
        # Remove rows with invalid data
        data = data.dropna()
        
        # Sort by date
        data = data.sort_index()
        
        return data
    
    def _is_cache_valid(self, cache_key: str) -> bool:
        """Check if cached data is still valid"""
        if cache_key not in self.cache:
            return False
        
        cache_time = self.cache[cache_key]['timestamp']
        return datetime.now() - cache_time < self.cache_duration
    
    def _cache_data(self, cache_key: str, data: pd.DataFrame):
        """Cache the fetched data"""
        self.cache[cache_key] = {
            'data': data,
            'timestamp': datetime.now()
        }
        
        # Limit cache size
        if len(self.cache) > 100:
            # Remove oldest entries
            oldest_key = min(self.cache.keys(), key=lambda k: self.cache[k]['timestamp'])
            del self.cache[oldest_key]
    
    def get_symbol_info(self, symbol: str) -> dict:
        """Get basic information about a symbol"""
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            return {
                'symbol': symbol,
                'name': info.get('longName', symbol),
                'sector': info.get('sector', 'Unknown'),
                'industry': info.get('industry', 'Unknown'),
                'market_cap': info.get('marketCap', 0),
                'currency': info.get('currency', 'USD'),
                'exchange': info.get('exchange', 'Unknown')
            }
            
        except Exception as e:
            logger.error(f"Error getting info for {symbol}: {e}")
            return {
                'symbol': symbol,
                'name': symbol,
                'sector': 'Unknown',
                'industry': 'Unknown',
                'market_cap': 0,
                'currency': 'USD',
                'exchange': 'Unknown'
            }
    
    def get_multiple_symbols(self, symbols: list, period: str = "1y") -> dict:
        """Fetch data for multiple symbols concurrently"""
        async def fetch_all():
            tasks = [self.fetch_data(symbol, period) for symbol in symbols]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            data_dict = {}
            for symbol, result in zip(symbols, results):
                if isinstance(result, Exception):
                    logger.error(f"Error fetching {symbol}: {result}")
                    data_dict[symbol] = pd.DataFrame()
                else:
                    data_dict[symbol] = result
            
            return data_dict
        
        # Run the async function
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(fetch_all())
        finally:
            loop.close()
    
    def clear_cache(self):
        """Clear all cached data"""
        self.cache.clear()
        logger.info("Cache cleared")
    
    def get_cache_stats(self) -> dict:
        """Get cache statistics"""
        return {
            'cache_size': len(self.cache),
            'cache_keys': list(self.cache.keys()),
            'oldest_entry': min([entry['timestamp'] for entry in self.cache.values()]) if self.cache else None,
            'newest_entry': max([entry['timestamp'] for entry in self.cache.values()]) if self.cache else None
        }
    
    async def fetch_forex_data(self, from_currency: str, to_currency: str = 'USD', 
                               period: str = "1d") -> Optional[pd.DataFrame]:
        """Fetch forex data using Alpha Vantage"""
        try:
            # Check cache first
            cache_key = f"forex_{from_currency}_{to_currency}_{period}"
            if self._is_cache_valid(cache_key):
                logger.info(f"Using cached forex data for {from_currency}/{to_currency}")
                return self.cache[cache_key]['data']
            
            logger.info(f"Fetching forex data for {from_currency}/{to_currency}")
            
            # Try Alpha Vantage first
            if from_currency in ['XAU', 'XAG', 'XPT', 'XPD']:  # Metals
                quote = self.alpha_vantage.get_metal_quote(from_currency)
                if quote:
                    # Create a simple DataFrame for metals
                    data = pd.DataFrame({
                        'Open': [float(quote.get('5. Exchange Rate', 0))],
                        'High': [float(quote.get('5. Exchange Rate', 0))],
                        'Low': [float(quote.get('5. Exchange Rate', 0))],
                        'Close': [float(quote.get('5. Exchange Rate', 0))],
                        'Volume': [0]
                    }, index=[pd.Timestamp.now()])
                    
                    self._cache_data(cache_key, data)
                    return data
            
            # For regular forex pairs
            data = self.alpha_vantage.get_forex_intraday(from_currency, to_currency)
            if data is not None and not data.empty:
                self._cache_data(cache_key, data)
                return data
            
            # Fallback to yfinance if Alpha Vantage fails
            logger.info(f"Alpha Vantage failed, trying yfinance for {from_currency}/{to_currency}")
            return await self.fetch_data(f"{from_currency}{to_currency}=X", period)
            
        except Exception as e:
            logger.error(f"Error fetching forex data for {from_currency}/{to_currency}: {e}")
            return None
    
    async def fetch_metal_data(self, metal: str, period: str = "1d") -> Optional[pd.DataFrame]:
        """Fetch metal data using Alpha Vantage"""
        return await self.fetch_forex_data(metal, 'USD', period)
    
    def get_available_markets(self) -> dict:
        """Get list of available markets and their status"""
        return {
            'stocks': ['AAPL', 'TSLA', 'GOOGL', 'MSFT', 'NVDA', 'AMZN', 'META', 'NFLX'],
            'forex': ['EUR/USD', 'GBP/USD', 'USD/JPY', 'AUD/USD', 'USD/CHF', 'USD/CAD'],
            'metals': ['XAU/USD', 'XAG/USD', 'XPT/USD', 'XPD/USD'],
            'crypto': ['BTC/USD', 'ETH/USD', 'ADA/USD'],
            'alpha_vantage_status': self.alpha_vantage.get_market_status()
        }




