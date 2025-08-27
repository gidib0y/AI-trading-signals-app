#!/usr/bin/env python3
"""
Demo script for the AI Trading Signal Generator
This script demonstrates the core functionality without starting the web server
"""

import asyncio
import sys
import os

# Add the app directory to the path
sys.path.insert(0, os.path.dirname(__file__))

from app.utils.data_fetcher import DataFetcher
from app.utils.indicators import TechnicalIndicators
from app.services.ml_service import MLService
from app.services.trading_service import TradingService
from config import Config

async def main():
    """Main demo function"""
    print("🚀 AI Trading Signal Generator Demo")
    print("=" * 50)
    
    # Ensure directories exist
    Config.ensure_directories()
    
    try:
        # Initialize services
        print("📊 Initializing services...")
        data_fetcher = DataFetcher()
        indicators = TechnicalIndicators()
        ml_service = MLService()
        trading_service = TradingService()
        
        # Test with a popular stock
        symbol = "AAPL"
        period = "1y"
        
        print(f"\n📈 Fetching data for {symbol}...")
        data = await data_fetcher.fetch_data(symbol, period)
        
        if data.empty:
            print("❌ No data received")
            return
        
        print(f"✅ Received {len(data)} data points")
        print(f"📅 Date range: {data.index[0].date()} to {data.index[-1].date()}")
        print(f"💰 Current price: ${data['Close'].iloc[-1]:.2f}")
        
        # Calculate technical indicators
        print("\n🔧 Calculating technical indicators...")
        data_with_indicators = indicators.calculate_all(data)
        print("✅ Technical indicators calculated")
        
        # Get indicator summary
        indicator_summary = indicators.get_indicator_summary(data_with_indicators)
        print(f"📊 RSI: {indicator_summary['rsi']:.2f}")
        print(f"📊 MACD: {indicator_summary['macd']['macd']:.4f}")
        
        # Generate ML predictions
        print("\n🤖 Generating ML predictions...")
        predictions = ml_service.predict_signals(data_with_indicators)
        print(f"✅ ML confidence: {predictions['confidence_score']:.2%}")
        print(f"✅ Signal probability: {predictions['signal_probability']:.2%}")
        
        # Generate trading signals
        print("\n📡 Generating trading signals...")
        signals = trading_service.generate_signals(data_with_indicators, predictions)
        print(f"✅ Generated {len(signals)} signals")
        
        # Display signals
        for i, signal in enumerate(signals[:3]):  # Show first 3 signals
            print(f"\n📊 Signal {i+1}:")
            print(f"   Type: {signal.signal_type}")
            print(f"   Price: ${signal.price:.2f}")
            print(f"   Confidence: {signal.confidence:.2%}")
            print(f"   Reason: {signal.reason}")
        
        # Train the model if we have enough data
        if len(data_with_indicators) > 100:
            print("\n🎓 Training ML model...")
            ml_service.train_model(data_with_indicators)
            print("✅ Model training completed")
        
        print("\n🎉 Demo completed successfully!")
        print("\nTo start the web interface, run:")
        print("  python run.py")
        print("\nOr for the FastAPI server directly:")
        print("  uvicorn app.main:app --reload")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())



