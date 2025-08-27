import yfinance as yf
import pandas as pd
import asyncio
from typing import Optional
import logging
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataFetcher:
    """Utility class for fetching market data from various sources"""
    
    def __init__(self):
        self.cache = {}
        self.cache_duration = timedelta(minutes=5)  # Cache data for 5 minutes
    
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



