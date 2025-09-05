import requests
import pandas as pd
from typing import Optional, Dict, Any
import os
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class AlphaVantageService:
    def __init__(self):
        # Get API key from environment variable
        self.api_key = os.getenv('ALPHA_VANTAGE_API_KEY', 'demo')
        self.base_url = 'https://www.alphavantage.co/query'
        
        # Free tier limits
        self.max_requests_per_minute = 5
        self.max_requests_per_day = 500
        
    def _make_request(self, params: Dict[str, Any]) -> Optional[Dict]:
        """Make API request to Alpha Vantage"""
        try:
            params['apikey'] = self.api_key
            response = requests.get(self.base_url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check for API errors
                if 'Error Message' in data:
                    logger.error(f"Alpha Vantage API Error: {data['Error Message']}")
                    return None
                    
                if 'Note' in data:
                    logger.warning(f"Alpha Vantage API Note: {data['Note']}")
                    return None
                    
                return data
            else:
                logger.error(f"Alpha Vantage API request failed: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error making Alpha Vantage request: {e}")
            return None
    
    def get_forex_quote(self, from_currency: str, to_currency: str = 'USD') -> Optional[Dict]:
        """Get real-time forex quote"""
        try:
            params = {
                'function': 'CURRENCY_EXCHANGE_RATE',
                'from_currency': from_currency,
                'to_currency': to_currency
            }
            
            data = self._make_request(params)
            if data and 'Realtime Currency Exchange Rate' in data:
                return data['Realtime Currency Exchange Rate']
            return None
            
        except Exception as e:
            logger.error(f"Error getting forex quote for {from_currency}/{to_currency}: {e}")
            return None
    
    def get_forex_intraday(self, from_currency: str, to_currency: str = 'USD', 
                           interval: str = '5min', output_size: str = 'compact') -> Optional[pd.DataFrame]:
        """Get intraday forex data"""
        try:
            params = {
                'function': 'FX_INTRADAY',
                'from_symbol': from_currency,
                'to_symbol': to_currency,
                'interval': interval,
                'outputsize': output_size
            }
            
            data = self._make_request(params)
            if data and 'Time Series FX (5min)' in data:
                time_series = data['Time Series FX (5min)']
                
                # Convert to DataFrame
                df = pd.DataFrame.from_dict(time_series, orient='index')
                df.index = pd.to_datetime(df.index)
                
                # Rename columns to match our standard format
                df.columns = ['Open', 'High', 'Low', 'Close']
                df = df.astype(float)
                
                return df
            return None
            
        except Exception as e:
            logger.error(f"Error getting forex intraday for {from_currency}/{to_currency}: {e}")
            return None
    
    def get_metal_quote(self, metal: str = 'XAU') -> Optional[Dict]:
        """Get real-time metal quote (gold, silver, etc.)"""
        try:
            # For metals, we use the forex endpoint with metal codes
            metal_codes = {
                'XAU': 'XAU',  # Gold
                'XAG': 'XAG',  # Silver
                'XPT': 'XPT',  # Platinum
                'XPD': 'XPD'   # Palladium
            }
            
            if metal not in metal_codes:
                logger.error(f"Unsupported metal: {metal}")
                return None
            
            return self.get_forex_quote(metal_codes[metal], 'USD')
            
        except Exception as e:
            logger.error(f"Error getting metal quote for {metal}: {e}")
            return None
    
    def get_crypto_quote(self, crypto: str, market: str = 'USD') -> Optional[Dict]:
        """Get real-time cryptocurrency quote"""
        try:
            params = {
                'function': 'CURRENCY_EXCHANGE_RATE',
                'from_currency': crypto,
                'to_currency': market
            }
            
            data = self._make_request(params)
            if data and 'Realtime Currency Exchange Rate' in data:
                return data['Realtime Currency Exchange Rate']
            return None
            
        except Exception as e:
            logger.error(f"Error getting crypto quote for {crypto}/{market}: {e}")
            return None
    
    def get_stock_quote(self, symbol: str) -> Optional[Dict]:
        """Get real-time stock quote"""
        try:
            params = {
                'function': 'GLOBAL_QUOTE',
                'symbol': symbol
            }
            
            data = self._make_request(params)
            if data and 'Global Quote' in data:
                return data['Global Quote']
            return None
            
        except Exception as e:
            logger.error(f"Error getting stock quote for {symbol}: {e}")
            return None
    
    def get_stock_intraday(self, symbol: str, interval: str = '5min', 
                           output_size: str = 'compact') -> Optional[pd.DataFrame]:
        """Get intraday stock data"""
        try:
            params = {
                'function': 'TIME_SERIES_INTRADAY',
                'symbol': symbol,
                'interval': interval,
                'outputsize': output_size
            }
            
            data = self._make_request(params)
            if data and f'Time Series ({interval})' in data:
                time_series = data[f'Time Series ({interval})']
                
                # Convert to DataFrame
                df = pd.DataFrame.from_dict(time_series, orient='index')
                df.index = pd.to_datetime(df.index)
                
                # Rename columns to match our standard format
                df.columns = ['Open', 'High', 'Low', 'Close', 'Volume']
                df = df.astype(float)
                
                return df
            return None
            
        except Exception as e:
            logger.error(f"Error getting stock intraday for {symbol}: {e}")
            return None
    
    def get_market_status(self) -> Dict[str, Any]:
        """Get current market status and limits"""
        return {
            'api_key_configured': self.api_key != 'demo',
            'max_requests_per_minute': self.max_requests_per_minute,
            'max_requests_per_day': self.max_requests_per_day,
            'service': 'Alpha Vantage'
        }
