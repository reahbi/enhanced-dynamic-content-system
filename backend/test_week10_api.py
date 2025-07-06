"""
Test script for Week 10 API endpoints
Verifies all new endpoints are properly configured
"""

import requests
import json
from datetime import datetime

# Base URL for the API
BASE_URL = "http://localhost:8000"

def test_main_endpoints():
    """Test main API endpoints"""
    print("🔍 Testing Week 10 API Endpoints...")
    print("=" * 50)
    
    # Test root endpoint
    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"✅ Root endpoint: {response.status_code}")
        data = response.json()
        print(f"   Available endpoints: {list(data.get('endpoints', {}).keys())}")
    except Exception as e:
        print(f"❌ Root endpoint failed: {e}")
    
    # Test health endpoint
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"✅ Health endpoint: {response.status_code}")
    except Exception as e:
        print(f"❌ Health endpoint failed: {e}")
    
    print("\n")

def test_health_api():
    """Test Health API endpoints"""
    print("🏥 Testing Health API...")
    print("-" * 40)
    
    endpoints = [
        "/api/v1/health/status",
        "/api/v1/health/metrics",
        "/api/v1/health/diagnostics"
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"{BASE_URL}{endpoint}")
            status = "✅" if response.status_code == 200 else "❌"
            print(f"{status} {endpoint}: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                if "status" in data:
                    print(f"   Status: {data.get('status')}")
                if "overall_status" in data:
                    print(f"   Overall Status: {data.get('overall_status')}")
        except Exception as e:
            print(f"❌ {endpoint}: {e}")
    
    print("\n")

def test_cache_api():
    """Test Cache API endpoints"""
    print("💾 Testing Cache API...")
    print("-" * 40)
    
    endpoints = [
        "/api/v1/cache/status",
        "/api/v1/cache/entries",
        "/api/v1/cache/entries?limit=10"
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"{BASE_URL}{endpoint}")
            status = "✅" if response.status_code == 200 else "❌"
            print(f"{status} {endpoint}: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                if "statistics" in data:
                    stats = data["statistics"]
                    print(f"   Cache Size: {stats.get('total_size_mb', 0)} MB")
                    print(f"   Hit Rate: {stats.get('hit_rate', 0)}%")
                if "total" in data:
                    print(f"   Total Entries: {data.get('total', 0)}")
        except Exception as e:
            print(f"❌ {endpoint}: {e}")
    
    print("\n")

def test_analytics_api():
    """Test Analytics API endpoints"""
    print("📊 Testing Analytics API...")
    print("-" * 40)
    
    endpoints = [
        "/api/v1/analytics/overview",
        "/api/v1/analytics/content-metrics",
        "/api/v1/analytics/category-performance",
        "/api/v1/analytics/paper-quality",
        "/api/v1/analytics/system-usage"
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"{BASE_URL}{endpoint}")
            status = "✅" if response.status_code == 200 else "❌"
            print(f"{status} {endpoint}: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                if "content" in data:
                    content = data["content"]
                    print(f"   Total Generated: {content.get('total_generated', 0)}")
                if "categories" in data:
                    print(f"   Categories Analyzed: {len(data['categories'])}")
                if "usage_statistics" in data:
                    print(f"   System Health: {data.get('system_health', 'unknown')}")
        except Exception as e:
            print(f"❌ {endpoint}: {e}")
    
    print("\n")

def test_api_documentation():
    """Test API documentation endpoints"""
    print("📚 Testing API Documentation...")
    print("-" * 40)
    
    endpoints = [
        "/docs",
        "/redoc"
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"{BASE_URL}{endpoint}")
            status = "✅" if response.status_code == 200 else "❌"
            print(f"{status} {endpoint}: {response.status_code}")
        except Exception as e:
            print(f"❌ {endpoint}: {e}")
    
    print("\n")

def main():
    """Run all tests"""
    print(f"\n🚀 Week 10 API Test Suite")
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    
    # Check if server is running
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code != 200:
            print("⚠️  Server is not responding properly!")
            return
    except requests.ConnectionError:
        print("❌ Cannot connect to server at", BASE_URL)
        print("💡 Make sure to run: uvicorn app.main:app --reload")
        return
    
    # Run all tests
    test_main_endpoints()
    test_health_api()
    test_cache_api()
    test_analytics_api()
    test_api_documentation()
    
    print("✨ Week 10 API testing complete!")
    print("=" * 50)

if __name__ == "__main__":
    main()