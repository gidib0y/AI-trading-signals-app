"""
Basic tests for the AI Trading Signal Generator
"""

import pytest
import sys
import os

# Add the app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

def test_imports():
    """Test that all modules can be imported"""
    try:
        from app.main import app
        from app.services.trading_service import TradingService
        from app.services.ml_service import MLService
        from app.utils.data_fetcher import DataFetcher
        from app.utils.indicators import TechnicalIndicators
        from app.models.schemas import SignalType, AnalysisRequest
        assert True
    except ImportError as e:
        pytest.fail(f"Import failed: {e}")

def test_app_creation():
    """Test that the FastAPI app can be created"""
    try:
        from app.main import app
        assert app is not None
        assert hasattr(app, 'routes')
    except Exception as e:
        pytest.fail(f"App creation failed: {e}")

def test_schemas():
    """Test that the schemas are properly defined"""
    try:
        from app.models.schemas import SignalType, AnalysisRequest, Signal
        
        # Test enum values
        assert SignalType.BUY == "BUY"
        assert SignalType.SELL == "SELL"
        assert SignalType.HOLD == "HOLD"
        
        # Test request model
        request = AnalysisRequest(symbol="AAPL", period="1y")
        assert request.symbol == "AAPL"
        assert request.period == "1y"
        
    except Exception as e:
        pytest.fail(f"Schema test failed: {e}")

if __name__ == "__main__":
    # Run basic tests
    print("Running basic tests...")
    
    try:
        test_imports()
        print("✅ Import tests passed")
        
        test_app_creation()
        print("✅ App creation test passed")
        
        test_schemas()
        print("✅ Schema tests passed")
        
        print("\n🎉 All basic tests passed!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        sys.exit(1)













