import asyncio
import json
import time
from typing import Dict, List, Optional, Callable
# import yfinance as yf  # Temporarily disabled due to Windows compatibility issues
import aiohttp
from datetime import datetime
import logging

class RealTimePriceService:
    """Real-time price service for live trading data"""

    def __init__(self, alpha_vantage_api_key: str):
        self.alpha_vantage_api_key = alpha_vantage_api_key
        self.price_cache = {}
        self.subscribers = {}
        self.is_running = False

    async def start(self):
        """Start the real-time price service"""
        self.is_running = True
        logging.info("Starting Real-Time Price Service...")

        # Start data streams
        await asyncio.gather(
            self.start_alpha_vantage_stream(),
            self.start_stock_data_stream()
        )

    async def stop(self):
        """Stop the real-time price service"""
        self.is_running = False
        logging.info("Real-Time Price Service stopped")

    async def start_alpha_vantage_stream(self):
        """Start Alpha Vantage real-time data stream"""
        while self.is_running:
            try:
                # Get real-time quotes for major symbols
                symbols = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'GC', 'SI', 'EUR/USD', 'GBP/USD']

                for symbol in symbols:
                    if self.is_running:
                        price_data = await self.get_alpha_vantage_quote(symbol)
                        if price_data:
                            await self.update_price(symbol, price_data)

                        # Rate limiting for Alpha Vantage (5 calls per minute)
                        await asyncio.sleep(12)

                await asyncio.sleep(60)  # Update every minute

            except Exception as e:
                logging.error(f"Alpha Vantage stream error: {e}")
                await asyncio.sleep(60)

    async def start_stock_data_stream(self):
        """Start Alpha Vantage real-time stock data stream"""
        while self.is_running:
            try:
                # Get real-time data for major stocks using Alpha Vantage
                symbols = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'NVDA', 'META', 'NFLX']

                for symbol in symbols:
                    if self.is_running:
                        try:
                            # Use Alpha Vantage for stock data
                            price_data = await self.get_alpha_vantage_quote(symbol)
                            if price_data:
                                await self.update_price(symbol, price_data)
                        except Exception as e:
                            logging.error(f"Alpha Vantage error for {symbol}: {e}")

                        await asyncio.sleep(12)  # Rate limiting for Alpha Vantage (5 calls per minute)

                await asyncio.sleep(60)  # Update every minute

            except Exception as e:
                logging.error(f"Alpha Vantage stock stream error: {e}")
                await asyncio.sleep(60)

    async def get_alpha_vantage_quote(self, symbol: str) -> Optional[Dict]:
        """Get real-time quote from Alpha Vantage"""
        try:
            # Handle different market types
            if symbol in ['GC', 'SI']:  # Gold, Silver
                url = f"https://www.alphavantage.co/query?function=CURRENCY_EXCHANGE_RATE&from_currency={symbol}&to_currency=USD&apikey={self.alpha_vantage_api_key}"
            elif '/' in symbol:  # Forex
                from_curr, to_curr = symbol.split('/')
                url = f"https://www.alphavantage.co/query?function=CURRENCY_EXCHANGE_RATE&from_currency={from_curr}&to_currency={to_curr}&apikey={self.alpha_vantage_api_key}"
            else:  # Stocks
                url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey={self.alpha_vantage_api_key}"

            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()

                        if 'Global Quote' in data:  # Stocks
                            quote = data['Global Quote']
                            return {
                                'symbol': symbol,
                                'price': float(quote.get('05. price', 0)),
                                'change': float(quote.get('09. change', 0)),
                                'change_percent': quote.get('10. change percent', '0%'),
                                'volume': int(quote.get('06. volume', 0)),
                                'high': float(quote.get('03. high', 0)),
                                'low': float(quote.get('04. low', 0)),
                                'timestamp': datetime.now().isoformat(),
                                'source': 'alpha_vantage'
                            }
                        elif 'Realtime Currency Exchange Rate' in data:  # Forex/Metals
                            rate = data['Realtime Currency Exchange Rate']
                            return {
                                'symbol': symbol,
                                'price': float(rate.get('5. Exchange Rate', 0)),
                                'change': 0,  # Alpha Vantage doesn't provide change for forex
                                'change_percent': '0%',
                                'volume': 0,
                                'high': 0,
                                'low': 0,
                                'timestamp': datetime.now().isoformat(),
                                'source': 'alpha_vantage'
                            }

                return None

        except Exception as e:
            logging.error(f"Alpha Vantage API error for {symbol}: {e}")
            return None

    async def update_price(self, symbol: str, price_data: Dict):
        """Update price data and notify subscribers"""
        self.price_cache[symbol] = price_data

        # Notify subscribers
        if symbol in self.subscribers:
            for callback in self.subscribers[symbol]:
                try:
                    await callback(symbol, price_data)
                except Exception as e:
                    logging.error(f"Subscriber callback error: {e}")

    def subscribe(self, symbol: str, callback: Callable):
        """Subscribe to price updates for a symbol"""
        if symbol not in self.subscribers:
            self.subscribers[symbol] = []
        self.subscribers[symbol].append(callback)

    def unsubscribe(self, symbol: str, callback: Callable):
        """Unsubscribe from price updates for a symbol"""
        if symbol in self.subscribers and callback in self.subscribers[symbol]:
            self.subscribers[symbol].remove(callback)

    def get_current_price(self, symbol: str) -> Optional[Dict]:
        """Get current price for a symbol"""
        return self.price_cache.get(symbol)

    def get_all_prices(self) -> Dict[str, Dict]:
        """Get all current prices"""
        return self.price_cache.copy()

    async def get_historical_data(self, symbol: str, period: str = "1d", interval: str = "1m") -> Optional[List[Dict]]:
        """Get historical data for backtesting"""
        try:
            if symbol in ['GC', 'SI'] or '/' in symbol:
                # For metals/forex, use Alpha Vantage
                url = f"https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={symbol}&interval={interval}&apikey={self.alpha_vantage_api_key}"

                async with aiohttp.ClientSession() as session:
                    async with session.get(url) as response:
                        if response.status == 200:
                            data = await response.json()
                            if 'Time Series (1min)' in data:
                                time_series = data['Time Series (1min)']
                                historical_data = []

                                for timestamp, values in time_series.items():
                                    historical_data.append({
                                        'timestamp': timestamp,
                                        'open': float(values['1. open']),
                                        'high': float(values['2. high']),
                                        'low': float(values['3. low']),
                                        'close': float(values['4. close']),
                                        'volume': int(values['5. volume'])
                                    })

                                return historical_data
            else:
                # For stocks, use Yahoo Finance
                ticker = yf.Ticker(symbol)
                hist = ticker.history(period=period, interval=interval)

                historical_data = []
                for index, row in hist.iterrows():
                    historical_data.append({
                        'timestamp': index.isoformat(),
                        'open': float(row['Open']),
                        'high': float(row['High']),
                        'low': float(row['Low']),
                        'close': float(row['Close']),
                        'volume': int(row['Volume'])
                    })

                return historical_data

        except Exception as e:
            logging.error(f"Historical data error for {symbol}: {e}")
            return None
