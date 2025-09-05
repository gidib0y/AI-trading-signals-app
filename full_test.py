import requests

def full_test():
    print("Testing Trading Signals API...")
    
    # Test health endpoint
    try:
        health = requests.get("http://localhost:8003/api/health")
        print(f"✅ Health check: {health.status_code} - {health.json()}")
    except:
        print("❌ Health check failed")
        return False
    
    # Test start monitoring
    try:
        start = requests.post(
            "http://localhost:8003/api/live/start",
            json={"symbols": ["AAPL", "TSLA", "GOOGL"], "timeframes": ["1m"]}
        )
        print(f"✅ Start monitoring: {start.status_code} - {start.json()}")
    except:
        print("❌ Start monitoring failed")
        return False
    
    # Test get signals
    try:
        signals = requests.get("http://localhost:8003/api/live/signals")
        print(f"✅ Get signals: {signals.status_code} - {len(signals.json()['signals'])} signals")
    except:
        print("❌ Get signals failed")
        return False
    
    # Test get summary
    try:
        summary = requests.get("http://localhost:8003/api/live/summary")
        print(f"✅ Get summary: {summary.status_code} - {summary.json()['summary']['market_status']}")
    except:
        print("❌ Get summary failed")
        return False
    
    print("\n🎉 All tests passed! Server is working correctly.")
    return True

if __name__ == "__main__":
    full_test()
