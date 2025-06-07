#!/usr/bin/env python3
"""
Simple test to verify basic functionality
"""

import sys
import os

# Add the backend directory to the Python path
backend_path = os.path.join(os.path.dirname(__file__), 'backend')
print(f"Adding to path: {backend_path}")
sys.path.insert(0, backend_path)

def test_imports():
    """Test that we can import our services"""
    try:
        print("Attempting to import FileProcessingService...")
        from app.services.file_processing_service import FileProcessingService
        print("✅ FileProcessingService imported successfully")
        
        print("Attempting to import EntitiesService...")
        from app.services.entities_service import EntitiesService
        print("✅ EntitiesService imported successfully")
        
        return True
    except Exception as e:
        print(f"❌ Import failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_service_creation():
    """Test that we can create service instances"""
    try:
        from app.services.file_processing_service import FileProcessingService
        from app.services.entities_service import EntitiesService
        
        # Create service instances
        file_service = FileProcessingService()
        entities_service = EntitiesService()
        
        print("✅ Service instances created successfully")
        return True
    except Exception as e:
        print(f"❌ Service creation failed: {e}")
        return False

def main():
    print("Running simple functionality tests...")
    print("=" * 50)
    
    if not test_imports():
        return False
        
    if not test_service_creation():
        return False
        
    print("=" * 50)
    print("✅ All simple tests passed!")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
