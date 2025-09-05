#!/usr/bin/env python3
"""
Complete System Test for AI Trading Signal Generator
Tests all major components and endpoints
"""

import requests
import time
import json
from datetime import datetime

class SystemTester:
    def __init__(self, base_url="http://localhost:8002"):
        self.base_url = base_url
        self.test_results = []
        
    def log_test(self, test_name, success, message=""):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        timestamp = datetime.now().strftime("%H:%M:%S")
        result = f"[{timestamp}] {status} - {test_name}"
        if message:
            result += f": {message}"
        print(result)
        
        self.test_results.append({
            "test": test_name,
            "success": success,
            "message": message,
            "timestamp": timestamp
        })
        
    def test_server_connection(self):
        """Test if server is running and accessible"""
        try:
            response = requests.get(f"{self.base_url}/", timeout=5)
            success = response.status_code == 200
            self.log_test("Server Connection", success, f"Status: {response.status_code}")
            return success
        except requests.exceptions.RequestException as e:
            self.log_test("Server Connection", False, f"Error: {e}")
            return False
    
    def test_health_endpoint(self):
        """Test health check endpoint"""
        try:
            response = requests.get(f"{self.base_url}/api/health", timeout=5)
            if response.status_code == 200:
                data = response.json()
                success = data.get("status") == "healthy"
                self.log_test("Health Endpoint", success, f"Response: {data}")
                return success
            else:
                self.log_test("Health Endpoint", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Health Endpoint", False, f"Error: {e}")
            return False
    
    def test_root_endpoint(self):
        """Test root API endpoint"""
        try:
            response = requests.get(f"{self.base_url}/api/root", timeout=5)
            if response.status_code == 200:
                data = response.json()
                success = "Trading Signals API" in data.get("message", "")
                self.log_test("Root Endpoint", success, f"Response: {data}")
                return success
            else:
                self.log_test("Root Endpoint", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Root Endpoint", False, f"Error: {e}")
            return False
    
    def test_symbol_analysis(self):
        """Test symbol analysis endpoint"""
        try:
            payload = {"symbol": "AAPL", "period": "1d"}
            response = requests.post(
                f"{self.base_url}/api/analyze", 
                json=payload, 
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                success = (
                    data.get("status") == "success" and
                    "signals" in data and
                    "summary" in data
                )
                self.log_test("Symbol Analysis", success, f"Analyzed: {data.get('symbol')}")
                return success
            else:
                self.log_test("Symbol Analysis", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Symbol Analysis", False, f"Error: {e}")
            return False
    
    def test_live_monitoring(self):
        """Test live monitoring endpoints"""
        try:
            # Test start monitoring
            start_payload = {"symbols": ["AAPL", "TSLA"], "timeframes": ["1m"]}
            start_response = requests.post(
                f"{self.base_url}/api/live/start",
                json=start_payload,
                timeout=10
            )
            
            if start_response.status_code == 200:
                start_data = start_response.json()
                start_success = start_data.get("status") == "success"
                self.log_test("Start Monitoring", start_success, start_data.get("message"))
                
                # Wait a moment for signals to generate
                time.sleep(2)
                
                # Test get signals
                signals_response = requests.get(f"{self.base_url}/api/live/signals", timeout=10)
                if signals_response.status_code == 200:
                    signals_data = signals_response.json()
                    signals_success = signals_data.get("status") == "success"
                    self.log_test("Get Signals", signals_success, f"Signals: {len(signals_data.get('signals', []))}")
                    
                    # Test get summary
                    summary_response = requests.get(f"{self.base_url}/api/live/summary", timeout=10)
                    if summary_response.status_code == 200:
                        summary_data = summary_response.json()
                        summary_success = summary_data.get("status") == "success"
                        self.log_test("Get Summary", summary_success, "Summary retrieved")
                        
                        # Test stop monitoring
                        stop_response = requests.post(f"{self.base_url}/api/live/stop", timeout=10)
                        if stop_response.status_code == 200:
                            stop_data = stop_response.json()
                            stop_success = stop_data.get("status") == "success"
                            self.log_test("Stop Monitoring", stop_success, stop_data.get("message"))
                            
                            return all([start_success, signals_success, summary_success, stop_success])
                        else:
                            self.log_test("Stop Monitoring", False, f"Status: {stop_response.status_code}")
                            return False
                    else:
                        self.log_test("Get Summary", False, f"Status: {summary_response.status_code}")
                        return False
                else:
                    self.log_test("Get Signals", False, f"Status: {signals_response.status_code}")
                    return False
            else:
                self.log_test("Start Monitoring", False, f"Status: {start_response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Live Monitoring", False, f"Error: {e}")
            return False
    
    def test_dashboard_pages(self):
        """Test dashboard page accessibility"""
        try:
            # Test main dashboard
            main_response = requests.get(f"{self.base_url}/", timeout=5)
            main_success = main_response.status_code == 200 and "AI Trading Signal Generator" in main_response.text
            
            # Test live dashboard
            live_response = requests.get(f"{self.base_url}/live", timeout=5)
            live_success = live_response.status_code == 200 and "Live Trading Signals Dashboard" in live_response.text
            
            self.log_test("Dashboard Pages", main_success and live_success, 
                         f"Main: {main_success}, Live: {live_success}")
            return main_success and live_success
            
        except Exception as e:
            self.log_test("Dashboard Pages", False, f"Error: {e}")
            return False
    
    def run_all_tests(self):
        """Run all system tests"""
        print("🚀 Starting Complete System Test")
        print("=" * 50)
        
        tests = [
            ("Server Connection", self.test_server_connection),
            ("Health Endpoint", self.test_health_endpoint),
            ("Root Endpoint", self.test_root_endpoint),
            ("Symbol Analysis", self.test_symbol_analysis),
            ("Live Monitoring", self.test_live_monitoring),
            ("Dashboard Pages", self.test_dashboard_pages),
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            try:
                if test_func():
                    passed += 1
            except Exception as e:
                self.log_test(test_name, False, f"Test crashed: {e}")
        
        print("=" * 50)
        print(f"📊 Test Results: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All tests passed! System is working correctly.")
        else:
            print("⚠️  Some tests failed. Check the logs above for details.")
        
        return passed == total
    
    def generate_report(self):
        """Generate a detailed test report"""
        print("\n📋 Detailed Test Report")
        print("=" * 50)
        
        for result in self.test_results:
            status = "✅ PASS" if result["success"] else "❌ FAIL"
            print(f"{status} - {result['test']}")
            if result["message"]:
                print(f"    Details: {result['message']}")
            print(f"    Time: {result['timestamp']}")
            print()

if __name__ == "__main__":
    print("AI Trading Signal Generator - System Test")
    print("Make sure the server is running on http://localhost:8002")
    print()
    
    tester = SystemTester()
    
    try:
        success = tester.run_all_tests()
        tester.generate_report()
        
        if success:
            print("🎯 System is ready for development and testing!")
            print("Next steps:")
            print("1. Open http://localhost:8002 in your browser")
            print("2. Test the dashboard functionality")
            print("3. Try the live monitoring features")
            print("4. Check the symbol analysis")
        else:
            print("🔧 Some issues detected. Please fix them before proceeding.")
            
    except KeyboardInterrupt:
        print("\n⏹️  Testing interrupted by user")
    except Exception as e:
        print(f"\n💥 Unexpected error during testing: {e}")
