#!/usr/bin/env python3
"""
Minimal test to check basic imports
"""

import sys
import os

# Add the backend directory to the Python path
backend_path = os.path.join(os.path.dirname(__file__), 'backend')
print(f"Adding to path: {backend_path}")
sys.path.insert(0, backend_path)

def test_basic_imports():
    """Test basic Python imports"""
    try:
        print("Testing basic imports...")
        import pandas as pd
        print("✅ pandas imported")
        
        import json
        print("✅ json imported")
        
        import uuid
        print("✅ uuid imported")
        
        return True
    except Exception as e:
        print(f"❌ Basic imports failed: {e}")
        return False

def test_app_structure():
    """Test app structure"""
    try:
        print("Testing app structure...")
        
        # Check if app module can be imported
        from app import __init__
        print("✅ app module imported")
        
        # Check if core config can be imported
        from app.core.config import Settings
        print("✅ Settings imported")
        
        return True
    except Exception as e:
        print(f"❌ App structure test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("Running minimal functionality tests...")
    print("=" * 50)
    
    if not test_basic_imports():
        return False
        
    if not test_app_structure():
        return False
        
    print("=" * 50)
    print("✅ All minimal tests passed!")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
