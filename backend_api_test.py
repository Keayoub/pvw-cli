#!/usr/bin/env python3
"""
Backend API Integration Test
Test the Purview CLI v2.0 backend API endpoints
"""
import asyncio
import json
import sys
import requests
from pathlib import Path
import time

class BackendAPITester:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.auth_token = None
        
    def test_health_check(self):
        """Test basic health check endpoint"""
        print("🔍 Testing health check endpoint...")
        try:
            response = self.session.get(f"{self.base_url}/health")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Health check passed: {data}")
                return True
            else:
                print(f"❌ Health check failed: {response.status_code}")
                return False
        except requests.exceptions.ConnectionError:
            print("❌ Cannot connect to backend server")
            return False
        except Exception as e:
            print(f"❌ Health check error: {e}")
            return False
    
    def test_api_docs(self):
        """Test if API documentation is accessible"""
        print("🔍 Testing API documentation...")
        try:
            response = self.session.get(f"{self.base_url}/docs")
            if response.status_code == 200:
                print("✅ API documentation accessible")
                return True
            else:
                print(f"❌ API docs failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ API docs error: {e}")
            return False
    
    def test_root_endpoint(self):
        """Test root API endpoint"""
        print("🔍 Testing root endpoint...")
        try:
            response = self.session.get(f"{self.base_url}/")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Root endpoint passed: {data.get('name', 'Unknown')}")
                return True
            else:
                print(f"❌ Root endpoint failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Root endpoint error: {e}")
            return False
    
    def test_api_endpoints(self):
        """Test available API endpoints"""
        print("🔍 Testing API endpoint structure...")
        endpoints_to_test = [
            "/api/v1/system/info",
            "/api/v1/system/health/detailed",
        ]
        
        success_count = 0
        for endpoint in endpoints_to_test:
            try:
                response = self.session.get(f"{self.base_url}{endpoint}")
                if response.status_code in [200, 401, 422]:  # 401/422 are expected without auth
                    print(f"✅ Endpoint accessible: {endpoint}")
                    success_count += 1
                else:
                    print(f"❌ Endpoint failed: {endpoint} - {response.status_code}")
            except Exception as e:
                print(f"❌ Endpoint error: {endpoint} - {e}")
        
        return success_count > 0
    
    def run_tests(self):
        """Run all backend API tests"""
        print("🚀 Starting Backend API Integration Tests")
        print("=" * 50)
        
        tests = [
            ("Health Check", self.test_health_check),
            ("Root Endpoint", self.test_root_endpoint),
            ("API Documentation", self.test_api_docs),
            ("API Endpoints", self.test_api_endpoints),
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            print(f"\n📋 Running: {test_name}")
            try:
                if test_func():
                    passed += 1
                    print(f"✅ {test_name}: PASSED")
                else:
                    print(f"❌ {test_name}: FAILED")
            except Exception as e:
                print(f"❌ {test_name}: ERROR - {e}")
        
        print("\n" + "=" * 50)
        print(f"📊 Test Results: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All backend API tests passed!")
            return True
        else:
            print("⚠️ Some backend API tests failed")
            return False

def main():
    """Main function to run backend API tests"""
    tester = BackendAPITester()
    
    # Wait a moment for server to be ready
    print("⏳ Waiting for backend server...")
    time.sleep(2)
    
    success = tester.run_tests()
    
    if success:
        print("\n🎯 Backend API is ready for frontend integration!")
        sys.exit(0)
    else:
        print("\n🚫 Backend API has issues that need resolution")
        sys.exit(1)

if __name__ == "__main__":
    main()
