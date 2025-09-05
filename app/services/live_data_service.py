import yfinance as yf
import pandas as pd
from typing import Dict, List
from datetime import datetime
import time

class LiveDataService:
    def __init__(self):
        self.data_cache = {}
        self.cache_expiry = {}
        self.cache_duration = 60
        
    def get_live_price(self, symbol: str) -> Dict:
        """Get current live price for any symbol"""
        try:
            # Check cache first
            if symbol in self.data_cache and time.time() < self.cache_expiry.get(symbol, 0):
                return self.data_cache[symbol]
            
            # Get live data from Yahoo Finance
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="1d", interval="1m")
            
            if hist.empty:
                return {"error": "No data available"}
            
            current_price = hist.iloc[-1]['Close']
            prev_price = hist.iloc[-2]['Close'] if len(hist) > 1 else current_price
            price_change = current_price - prev_price
            price_change_pct = (price_change / prev_price) * 100 if prev_price != 0 else 0
            
            result = {
                "symbol": symbol,
                "current_price": round(current_price, 4),
                "previous_price": round(prev_price, 4),
                "price_change": round(price_change, 4),
                "price_change_pct": round(price_change_pct, 2),
                "timestamp": datetime.now().isoformat()
            }
            
            # Cache the result
            self.data_cache[symbol] = result
            self.cache_expiry[symbol] = time.time() + self.cache_duration
            
            return result
            
        except Exception as e:
            return {"error": str(e)}
    
    def get_market_data_batch(self, symbols: List[str]) -> List[Dict]:
        """Get live prices for multiple symbols"""
        results = []
        for symbol in symbols:
            price_data = self.get_live_price(symbol)
            results.append(price_data)
            time.sleep(0.1)  # Avoid rate limiting
        return results

# Global instance
live_data_service = LiveDataService()
