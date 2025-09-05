import requests
import json

def test_live_data():
    """Test all live data endpoints"""
    base_url = "http://localhost:8003"
    
    print("🧪 Testing Live Data Endpoints...")
    print("=" * 50)
    
    # Test 1: Single symbol price
    print("\n1️⃣ Testing Single Symbol Price (AAPL):")
    try:
        response = requests.get(f"{base_url}/api/live/price/AAPL", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ SUCCESS: {data['data']['symbol']} = ${data['data']['current_price']}")
            print(f"   Change: {data['data']['price_change_pct']}%")
        else:
            print(f"❌ ERROR: Status {response.status_code}")
    except Exception as e:
        print(f"❌ ERROR: {e}")
    
    # Test 2: Multiple symbols
    print("\n2️⃣ Testing Multiple Symbols:")
    try:
        symbols = ["AAPL", "TSLA", "GOOGL"]
        response = requests.post(
            f"{base_url}/api/live/prices",
            json={"symbols": symbols},
            timeout=15
        )
        if response.status_code == 200:
            data = response.json()
            print(f"✅ SUCCESS: Got prices for {len(data['data'])} symbols")
            for item in data['data']:
                if 'error' not in item:
                    print(f"   {item['symbol']}: ${item['current_price']} ({item['price_change_pct']}%)")
        else:
            print(f"❌ ERROR: Status {response.status_code}")
    except Exception as e:
        print(f"❌ ERROR: {e}")
    
    # Test 3: Health check
    print("\n3️⃣ Testing Server Health:")
    try:
        response = requests.get(f"{base_url}/api/health", timeout=5)
        if response.status_code == 200:
            print("✅ SUCCESS: Server is healthy")
        else:
            print(f"❌ ERROR: Status {response.status_code}")
    except Exception as e:
        print(f"❌ ERROR: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 Test Complete! Check results above.")

if __name__ == "__main__":
    test_live_data()
