#!/usr/bin/env python3
"""
Test script to verify the API is working.
"""

import requests
import time
import json

def test_health_endpoint():
    """Test the health endpoint."""
    try:
        response = requests.get("http://localhost:8000/api/v1/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("✓ Health endpoint working")
            print(f"  Status: {data.get('status')}")
            print(f"  Version: {data.get('version')}")
            print(f"  GPU Available: {data.get('gpu_available')}")
            return True
        else:
            print(f"❌ Health endpoint returned status {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Health endpoint failed: {e}")
        return False

def test_models_endpoint():
    """Test the models endpoint."""
    try:
        response = requests.get("http://localhost:8000/api/v1/models", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("✓ Models endpoint working")
            print(f"  Available models: {len(data)}")
            for model in data:
                print(f"    - {model.get('name')}: {model.get('description')}")
            return True
        else:
            print(f"❌ Models endpoint returned status {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Models endpoint failed: {e}")
        return False

def test_products_endpoint():
    """Test the products endpoint."""
    try:
        response = requests.get("http://localhost:8000/api/v1/products", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("✓ Products endpoint working")
            print(f"  Supported products: {', '.join(data)}")
            return True
        else:
            print(f"❌ Products endpoint returned status {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Products endpoint failed: {e}")
        return False

def main():
    """Main test function."""
    print("Testing AI Stock Level Estimation API")
    print("=" * 40)
    
    # Wait a moment for server to start
    print("Waiting for server to start...")
    time.sleep(3)
    
    tests = [
        ("Health Check", test_health_endpoint),
        ("Models Endpoint", test_models_endpoint),
        ("Products Endpoint", test_products_endpoint),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        print("-" * 20)
        if test_func():
            passed += 1
        else:
            print(f"❌ {test_name} failed")
    
    print("\n" + "=" * 40)
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All API tests passed!")
        print("\nAPI is ready to use:")
        print("- Documentation: http://localhost:8000/docs")
        print("- Health Check: http://localhost:8000/api/v1/health")
        print("- Models: http://localhost:8000/api/v1/models")
        return 0
    else:
        print("❌ Some API tests failed")
        return 1

if __name__ == "__main__":
    main()
