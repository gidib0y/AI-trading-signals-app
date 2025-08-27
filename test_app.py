#!/usr/bin/env python3
"""
Test script to check if the AI Trading Signal Generator can run
"""

import sys
import traceback

def test_imports():
    """Test if all required modules can be imported"""
    print("Testing imports...")
    
    try:
        print("  Importing FastAPI...")
        from fastapi import FastAPI
        print("    ✅ FastAPI imported successfully")
        
        print("  Importing uvicorn...")
        import uvicorn
        print("    ✅ uvicorn imported successfully")
        
        print("  Importing pandas...")
        import pandas
        print("    ✅ pandas imported successfully")
        
        print("  Importing numpy...")
        import numpy
        print("    ✅ numpy imported successfully")
        
        print("  Importing yfinance...")
        import yfinance
        print("    ✅ yfinance imported successfully")
        
        print("  Importing ta...")
        import ta
        print("    ✅ ta imported successfully")
        
        print("  Importing app.main...")
        from app.main import app
        print("    ✅ app.main imported successfully")
        
        print("  Importing app.services.trading_service...")
        from app.services.trading_service import TradingService
        print("    ✅ TradingService imported successfully")
        
        print("  Importing app.services.ml_service...")
        from app.services.ml_service import MLService
        print("    ✅ MLService imported successfully")
        
        print("  Importing app.utils.data_fetcher...")
        from app.utils.data_fetcher import DataFetcher
        print("    ✅ DataFetcher imported successfully")
        
        print("  Importing app.utils.indicators...")
        from app.utils.indicators import TechnicalIndicators
        print("    ✅ TechnicalIndicators imported successfully")
        
        print("\n✅ All imports successful!")
        return True
        
    except Exception as e:
        print(f"\n❌ Import failed: {e}")
        print("\nTraceback:")
        traceback.print_exc()
        return False

def test_app_creation():
    """Test if the FastAPI app can be created"""
    print("\nTesting app creation...")
    
    try:
        from app.main import app
        print(f"  ✅ App created successfully: {type(app)}")
        print(f"  ✅ App title: {app.title}")
        print(f"  ✅ App version: {app.version}")
        return True
        
    except Exception as e:
        print(f"  ❌ App creation failed: {e}")
        traceback.print_exc()
        return False

def test_services():
    """Test if services can be instantiated"""
    print("\nTesting services...")
    
    try:
        from app.services.trading_service import TradingService
        from app.services.ml_service import MLService
        from app.utils.data_fetcher import DataFetcher
        from app.utils.indicators import TechnicalIndicators
        
        trading_service = TradingService()
        print("  ✅ TradingService created successfully")
        
        ml_service = MLService()
        print("  ✅ MLService created successfully")
        
        data_fetcher = DataFetcher()
        print("  ✅ DataFetcher created successfully")
        
        indicators = TechnicalIndicators()
        print("  ✅ TechnicalIndicators created successfully")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Service creation failed: {e}")
        traceback.print_exc()
        return False

def main():
    """Main test function"""
    print("🚀 Testing AI Trading Signal Generator")
    print("=" * 50)
    
    # Test imports
    if not test_imports():
        print("\n❌ Import tests failed. Cannot proceed.")
        return False
    
    # Test app creation
    if not test_app_creation():
        print("\n❌ App creation failed. Cannot proceed.")
        return False
    
    # Test services
    if not test_services():
        print("\n❌ Service creation failed. Cannot proceed.")
        return False
    
    print("\n🎉 All tests passed! The application should be ready to run.")
    print("\nTo start the application, run:")
    print("  py run.py")
    print("  or")
    print("  py -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)


