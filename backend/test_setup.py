#!/usr/bin/env python3
"""
Simple test script to verify the API setup.
"""

import sys
import os

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

def test_imports():
    """Test that all modules can be imported."""
    try:
        from app.core.config import settings
        print("✓ Configuration imported successfully")
        
        from app.models.schemas import StockEstimationRequest, ProductType
        print("✓ Schemas imported successfully")
        
        from app.services.ai_engine import AIEngine
        print("✓ AI Engine imported successfully")
        
        from app.services.file_processor import FileProcessor
        print("✓ File Processor imported successfully")
        
        from app.api.routes.health import router as health_router
        print("✓ Health routes imported successfully")
        
        from app.api.routes.stock_estimation import router as stock_router
        print("✓ Stock estimation routes imported successfully")
        
        return True
        
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False

def test_configuration():
    """Test configuration loading."""
    try:
        from app.core.config import settings
        
        print(f"✓ Host: {settings.HOST}")
        print(f"✓ Port: {settings.PORT}")
        print(f"✓ Debug: {settings.DEBUG}")
        print(f"✓ Supported products: {settings.SUPPORTED_PRODUCTS}")
        print(f"✓ Default model: {settings.DEFAULT_MODEL}")
        
        return True
        
    except Exception as e:
        print(f"✗ Configuration error: {e}")
        return False

def test_ai_engine():
    """Test AI engine initialization."""
    try:
        from app.services.ai_engine import AIEngine
        
        engine = AIEngine()
        print(f"✓ AI Engine initialized with device: {engine.device}")
        
        return True
        
    except Exception as e:
        print(f"✗ AI Engine error: {e}")
        return False

def main():
    """Run all tests."""
    print("Testing AI Stock Level Estimation API Setup...")
    print("=" * 50)
    
    tests = [
        ("Import Tests", test_imports),
        ("Configuration Tests", test_configuration),
        ("AI Engine Tests", test_ai_engine),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        print("-" * 20)
        if test_func():
            passed += 1
            print(f"✓ {test_name} passed")
        else:
            print(f"✗ {test_name} failed")
    
    print("\n" + "=" * 50)
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The API setup is working correctly.")
        return 0
    else:
        print("❌ Some tests failed. Please check the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
