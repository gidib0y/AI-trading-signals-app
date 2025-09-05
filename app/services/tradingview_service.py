import json
from typing import Dict, List, Optional
from datetime import datetime, timedelta

class TradingViewService:
    """TradingView chart integration service for SMC/ICT analysis"""
    
    def __init__(self):
        self.supported_symbols = {
            'stocks': {
                'NASDAQ': ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'NVDA', 'META', 'NFLX'],
                'NYSE': ['JPM', 'JNJ', 'PG', 'UNH', 'HD', 'BAC', 'MA', 'V'],
                'SP500': ['SPY', 'QQQ', 'IWM', 'DIA', 'VTI', 'VOO', 'VEA', 'VWO']
            },
            'forex': {
                'MAJORS': ['EUR/USD', 'GBP/USD', 'USD/JPY', 'USD/CHF', 'AUD/USD', 'USD/CAD', 'NZD/USD'],
                'MINORS': ['EUR/GBP', 'EUR/JPY', 'GBP/JPY', 'AUD/JPY', 'EUR/AUD', 'GBP/AUD'],
                'EXOTICS': ['USD/TRY', 'USD/ZAR', 'USD/BRL', 'USD/MXN', 'USD/INR', 'USD/CNY']
            },
            'futures': {
                'METALS': ['GC', 'SI', 'PL', 'PA', 'HG', 'AL', 'NI', 'ZN'],
                'ENERGY': ['CL', 'NG', 'HO', 'RB', 'BZ', 'QS', 'BZ=F'],
                'INDICES': ['ES', 'NQ', 'YM', 'RTY', 'SPX', 'NDX', 'DJI', 'RUT'],
                'AGRICULTURE': ['ZC', 'ZS', 'ZW', 'KC', 'CC', 'CT', 'SB', 'CC=F'],
                'BONDS': ['ZB', 'ZN', 'ZF', 'ZT', 'GE', 'TU', 'FV', 'TY']
            },
            'crypto': {
                'MAJORS': ['BTCUSD', 'ETHUSD', 'BNBUSD', 'ADAUSD', 'DOTUSD', 'LINKUSD', 'LTCUSD', 'XRPUSD'],
                'DEFI': ['UNIUSD', 'AAVEUSD', 'COMPUSD', 'MKRUSD', 'SUSHIUSD', 'YFIUSD'],
                'LAYER1': ['SOLUSD', 'AVAXUSD', 'MATICUSD', 'ATOMUSD', 'NEARUSD', 'FTMUSD']
            }
        }
        
        self.timeframes = {
            'intraday': ['1m', '5m', '15m', '30m', '1h', '2h', '4h'],
            'daily': ['1D', '1W', '1M', '3M', '6M', '1Y', '5Y', 'MAX']
        }
        
        self.smc_ict_indicators = [
            'Order Blocks',
            'Fair Value Gaps', 
            'Liquidity Levels',
            'Market Structure',
            'Volume Profile',
            'Premium/Discount Zones'
        ]
    
    def get_tradingview_widget_config(self, symbol: str, timeframe: str = '1D', 
                                    theme: str = 'dark', show_smc_indicators: bool = True) -> Dict:
        """Generate TradingView widget configuration"""
        
        # Map symbols to TradingView format
        tv_symbol = self.map_symbol_to_tradingview(symbol)
        
        # Base widget configuration
        config = {
            "width": "100%",
            "height": "600",
            "symbol": tv_symbol,
            "interval": timeframe,
            "timezone": "Etc/UTC",
            "theme": theme,
            "style": "1",  # 1 = Bars, 2 = Candles, 3 = Hollow Candles, 4 = Heikin Ashi, 8 = Line
            "locale": "en",
            "toolbar_bg": "#f1f3f6" if theme == 'light' else "#131722",
            "enable_publishing": False,
            "hide_top_toolbar": False,
            "hide_legend": False,
            "save_image": True,
            "container_id": f"tradingview_{symbol.replace('/', '_').replace('-', '_')}",
            "studies": self.get_smc_ict_studies() if show_smc_indicators else [],
            "show_popup_button": True,
            "popup_width": "1000",
            "popup_height": "650"
        }
        
        return config
    
    def map_symbol_to_tradingview(self, symbol: str) -> str:
        """Map internal symbols to TradingView format"""
        
        # Handle different market types
        if symbol in ['GC', 'SI', 'PL', 'PA']:  # Metals
            return f"COMEX:{symbol}1!"
        elif symbol in ['CL', 'NG', 'HO', 'RB']:  # Energy
            return f"NYMEX:{symbol}1!"
        elif symbol in ['ES', 'NQ', 'YM', 'RTY']:  # Index futures
            return f"CME:{symbol}1!"
        elif symbol in ['ZB', 'ZN', 'ZF', 'ZT']:  # Bond futures
            return f"CBOT:{symbol}1!"
        elif '/' in symbol:  # Forex
            return f"FX:{symbol}"
        elif symbol in ['BTCUSD', 'ETHUSD']:  # Crypto
            return f"CRYPTOCAP:{symbol}"
        else:  # Stocks
            return symbol
    
    def get_smc_ict_studies(self) -> List[str]:
        """Get SMC/ICT indicator studies for TradingView"""
        return [
            "MASimple@tv-basicstudies",      # Moving Averages
            "RSI@tv-basicstudies",           # RSI
            "MACD@tv-basicstudies",          # MACD
            "BB@tv-basicstudies",            # Bollinger Bands
            "Volume@tv-basicstudies",        # Volume
            "PivotPointsStandard@tv-basicstudies",  # Pivot Points
            "FibonacciRetracement@tv-basicstudies", # Fibonacci
            "LinearRegression@tv-basicstudies",     # Linear Regression
            "VWAP@tv-basicstudies",          # VWAP
            "ATR@tv-basicstudies"            # Average True Range
        ]
    
    def generate_tradingview_html(self, symbol: str, timeframe: str = '1D', 
                                theme: str = 'dark', height: str = '600px') -> str:
        """Generate complete TradingView HTML widget"""
        
        container_id = f"tradingview_{symbol.replace('/', '_').replace('-', '_')}"
        
        html = f"""
        <div class="tradingview-widget-container">
            <div id="{container_id}" style="height: {height}; width: 100%;"></div>
            <div class="tradingview-widget-copyright">
                <a href="https://www.tradingview.com/" rel="noopener nofollow" target="_blank">
                    <span class="blue-text">Track all markets on TradingView</span>
                </a>
            </div>
            <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
            <script type="text/javascript">
                new TradingView.widget({{
                    "width": "100%",
                    "height": "{height}",
                    "symbol": "{self.map_symbol_to_tradingview(symbol)}",
                    "interval": "{timeframe}",
                    "timezone": "Etc/UTC",
                    "theme": "{theme}",
                    "style": "1",
                    "locale": "en",
                    "toolbar_bg": "{'#f1f3f6' if theme == 'light' else '#131722'}",
                    "enable_publishing": false,
                    "hide_top_toolbar": false,
                    "hide_legend": false,
                    "save_image": true,
                    "container_id": "{container_id}",
                    "studies": {json.dumps(self.get_smc_ict_studies())},
                    "show_popup_button": true,
                    "popup_width": "1000",
                    "popup_height": "650"
                }});
            </script>
        </div>
        """
        
        return html
    
    def get_multi_timeframe_analysis(self, symbol: str) -> Dict:
        """Get analysis for multiple timeframes"""
        timeframes = {
            'intraday': ['5m', '15m', '1h', '4h'],
            'daily': ['1D', '1W', '1M']
        }
        
        analysis = {}
        for category, tf_list in timeframes.items():
            analysis[category] = {}
            for tf in tf_list:
                analysis[category][tf] = {
                    'widget_config': self.get_tradingview_widget_config(symbol, tf),
                    'html_widget': self.generate_tradingview_html(symbol, tf, height='400px')
                }
        
        return analysis
    
    def get_smc_ict_chart_annotations(self, smc_analysis: Dict) -> List[Dict]:
        """Generate chart annotations for SMC/ICT levels"""
        annotations = []
        
        # Order Block annotations
        if 'order_blocks' in smc_analysis:
            for block_type, price in smc_analysis['order_blocks'].items():
                annotations.append({
                    'type': 'horizontal_line',
                    'price': price,
                    'color': '#00ff00' if 'bullish' in block_type else '#ff0000',
                    'style': 'solid',
                    'width': 2,
                    'text': f'{block_type.replace("_", " ").title()}',
                    'position': 'left'
                })
        
        # Fair Value Gap annotations
        if 'fair_value_gaps' in smc_analysis:
            for gap_type, price in smc_analysis['fair_value_gaps'].items():
                annotations.append({
                    'type': 'horizontal_line',
                    'price': price,
                    'color': '#0080ff' if 'bullish' in gap_type else '#ff8000',
                    'style': 'dashed',
                    'width': 1,
                    'text': f'{gap_type.replace("_", " ").title()}',
                    'position': 'right'
                })
        
        # Liquidity Level annotations
        if 'liquidity_levels' in smc_analysis:
            for level_type, price in smc_analysis['liquidity_levels'].items():
                annotations.append({
                    'type': 'horizontal_line',
                    'price': price,
                    'color': '#ff00ff',
                    'style': 'dotted',
                    'width': 1,
                    'text': f'Liquidity {level_type.title()}',
                    'position': 'left'
                })
        
        # Premium/Discount Zone annotations
        if 'premium_discount_zones' in smc_analysis:
            for zone_type, price in smc_analysis['premium_discount_zones'].items():
                annotations.append({
                    'type': 'horizontal_line',
                    'price': price,
                    'color': '#ffff00' if 'premium' in zone_type else '#00ffff',
                    'style': 'solid',
                    'width': 1,
                    'text': f'{zone_type.replace("_", " ").title()}',
                    'position': 'right'
                })
        
        return annotations
    
    def get_chart_theme_config(self, theme: str = 'dark') -> Dict:
        """Get chart theme configuration"""
        themes = {
            'dark': {
                'background': '#131722',
                'text_color': '#d1d4dc',
                'grid_color': '#363c4e',
                'border_color': '#363c4e',
                'accent_color': '#2962ff'
            },
            'light': {
                'background': '#ffffff',
                'text_color': '#131722',
                'grid_color': '#e1e3e6',
                'border_color': '#e1e3e6',
                'accent_color': '#2962ff'
            },
            'blue': {
                'background': '#0d1117',
                'text_color': '#c9d1d9',
                'grid_color': '#21262d',
                'border_color': '#30363d',
                'accent_color': '#58a6ff'
            }
        }
        
        return themes.get(theme, themes['dark'])
    
    def get_symbol_info(self, symbol: str) -> Dict:
        """Get detailed information about a symbol"""
        info = {
            'symbol': symbol,
            'display_name': self.get_display_name(symbol),
            'market_type': self.get_market_type(symbol),
            'exchange': self.get_exchange(symbol),
            'trading_hours': self.get_trading_hours(symbol),
            'contract_size': self.get_contract_size(symbol),
            'tick_size': self.get_tick_size(symbol),
            'margin_requirements': self.get_margin_requirements(symbol)
        }
        
        return info
    
    def get_display_name(self, symbol: str) -> str:
        """Get human-readable display name for symbol"""
        names = {
            'GC': 'Gold Futures',
            'SI': 'Silver Futures',
            'PL': 'Platinum Futures',
            'PA': 'Palladium Futures',
            'CL': 'Crude Oil Futures',
            'NG': 'Natural Gas Futures',
            'ES': 'E-mini S&P 500',
            'NQ': 'E-mini NASDAQ-100',
            'BTCUSD': 'Bitcoin',
            'ETHUSD': 'Ethereum'
        }
        
        return names.get(symbol, symbol)
    
    def get_market_type(self, symbol: str) -> str:
        """Determine market type for symbol"""
        if symbol in ['GC', 'SI', 'PL', 'PA', 'CL', 'NG', 'ES', 'NQ']:
            return 'futures'
        elif '/' in symbol:
            return 'forex'
        elif symbol in ['BTCUSD', 'ETHUSD']:
            return 'crypto'
        else:
            return 'stocks'
    
    def get_exchange(self, symbol: str) -> str:
        """Get exchange for symbol"""
        exchanges = {
            'GC': 'COMEX',
            'SI': 'COMEX',
            'PL': 'NYMEX',
            'PA': 'NYMEX',
            'CL': 'NYMEX',
            'NG': 'NYMEX',
            'ES': 'CME',
            'NQ': 'CME',
            'BTCUSD': 'CRYPTOCAP',
            'ETHUSD': 'CRYPTOCAP'
        }
        
        return exchanges.get(symbol, 'NASDAQ')
    
    def get_trading_hours(self, symbol: str) -> str:
        """Get trading hours for symbol"""
        if symbol in ['GC', 'SI', 'PL', 'PA', 'CL', 'NG', 'ES', 'NQ']:
            return 'Sunday 6:00 PM - Friday 5:00 PM ET'
        elif '/' in symbol:
            return '24/5 (Sunday 5:00 PM - Friday 5:00 PM ET)'
        elif symbol in ['BTCUSD', 'ETHUSD']:
            return '24/7'
        else:
            return 'Monday 9:30 AM - Friday 4:00 PM ET'
    
    def get_contract_size(self, symbol: str) -> str:
        """Get contract size for futures"""
        sizes = {
            'GC': '100 troy ounces',
            'SI': '5,000 troy ounces',
            'PL': '50 troy ounces',
            'PA': '100 troy ounces',
            'CL': '1,000 barrels',
            'NG': '10,000 MMBtu',
            'ES': '$50 × S&P 500 Index',
            'NQ': '$20 × NASDAQ-100 Index'
        }
        
        return sizes.get(symbol, 'N/A')
    
    def get_tick_size(self, symbol: str) -> str:
        """Get tick size for futures"""
        ticks = {
            'GC': '$0.10 per troy ounce',
            'SI': '$0.005 per troy ounce',
            'PL': '$0.10 per troy ounce',
            'PA': '$0.05 per troy ounce',
            'CL': '$0.01 per barrel',
            'NG': '$0.001 per MMBtu',
            'ES': '0.25 index points',
            'NQ': '0.25 index points'
        }
        
        return ticks.get(symbol, 'N/A')
    
    def get_margin_requirements(self, symbol: str) -> str:
        """Get margin requirements for futures"""
        margins = {
            'GC': '$8,800 (Initial) / $8,000 (Maintenance)',
            'SI': '$12,375 (Initial) / $11,250 (Maintenance)',
            'PL': '$4,400 (Initial) / $4,000 (Maintenance)',
            'PA': '$8,800 (Initial) / $8,000 (Maintenance)',
            'CL': '$7,700 (Initial) / $7,000 (Maintenance)',
            'NG': '$6,600 (Initial) / $6,000 (Maintenance)',
            'ES': '$13,200 (Initial) / $12,000 (Maintenance)',
            'NQ': '$16,500 (Initial) / $15,000 (Maintenance)'
        }
        
        return margins.get(symbol, 'N/A')
