import yfinance as yf
import pandas as pd

def test_yahoo_coverage():
    """Test what Yahoo Finance actually provides"""
    print("🧪 Testing Yahoo Finance Coverage...")
    print("=" * 50)
    
    # Test different asset types
    test_symbols = {
        "Stocks": ["AAPL", "MSFT", "TSLA"],
        "ETFs": ["SPY", "QQQ", "GLD"],
        "Forex": ["EURUSD=X", "GBPUSD=X", "USDJPY=X"],
        "Crypto": ["BTC-USD", "ETH-USD", "ADA-USD"],
        "Commodities": ["GC=F", "CL=F", "SI=F"]
    }
    
    for asset_type, symbols in test_symbols.items():
        print(f"\n📊 {asset_type}:")
        for symbol in symbols:
            try:
                ticker = yf.Ticker(symbol)
                info = ticker.info
                
                if 'regularMarketPrice' in info and info['regularMarketPrice']:
                    price = info['regularMarketPrice']
                    name = info.get('longName', info.get('shortName', 'Unknown'))
                    print(f"   ✅ {symbol}: ${price} - {name}")
                else:
                    print(f"   ❌ {symbol}: No price data")
                    
            except Exception as e:
                print(f"   ❌ {symbol}: Error - {e}")
    
    print("\n" + "=" * 50)
    print("🎯 Test Complete! Check results above.")

if __name__ == "__main__":
    test_yahoo_coverage()
