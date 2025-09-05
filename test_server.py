import requests
import time

def test_server():
    print("Testing server connection...")
    try:
        response = requests.get("http://localhost:8002/api/health", timeout=5)
        print(f"✅ Server is running! Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return True
    except requests.ConnectionError:
        print("❌ Server is not running - connection refused")
        return False
    except Exception as e:
        print(f"❌ Error testing server: {e}")
        return False

if __name__ == "__main__":
    test_server()
