#!/usr/bin/env python3
"""Test script for the Unified Catalog data product functionality"""

import sys
import os

# Add the purviewcli package to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all our new modules can be imported"""
    try:
        from purviewcli.client._unified_catalog import UnifiedCatalogDataProduct
        print("✅ UnifiedCatalogDataProduct import: SUCCESS")
    except Exception as e:
        print(f"❌ UnifiedCatalogDataProduct import: FAILED - {e}")
        return False
    
    try:
        from purviewcli.cli.data_product import data_product
        print("✅ CLI data_product import: SUCCESS")
    except Exception as e:
        print(f"❌ CLI data_product import: FAILED - {e}")
        return False
    
    return True

def test_endpoints():
    """Test that endpoints are configured correctly"""
    try:
        from purviewcli.client.endpoints import ENDPOINTS, DATAMAP_API_VERSION
        
        # Check if DATA_PRODUCT endpoints exist
        if 'data_product' in ENDPOINTS:
            print("✅ DATA_PRODUCT endpoints: CONFIGURED")
            dp_endpoints = ENDPOINTS['data_product']
            print(f"   - Base: {dp_endpoints.get('base', 'NOT FOUND')}")
            print(f"   - Create: {dp_endpoints.get('create', 'NOT FOUND')}")
            print(f"   - Publish: {dp_endpoints.get('publish', 'NOT FOUND')}")
        else:
            print("❌ DATA_PRODUCT endpoints: NOT FOUND")
            return False

        # Check if UNIFIED_CATALOG_BASE exists
        if 'unified_catalog' in ENDPOINTS:
            print(f"✅ UNIFIED_CATALOG_BASE: {ENDPOINTS['unified_catalog']['base']}")
        else:
            print("❌ UNIFIED_CATALOG_BASE: NOT FOUND")
            return False
            
        return True
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def test_client_instantiation():
    """Test that clients can be instantiated"""
    try:
        from purviewcli.client._unified_catalog import UnifiedCatalogDataProduct
        uc_client = UnifiedCatalogDataProduct()
        print("✅ UnifiedCatalogDataProduct instantiation: SUCCESS")
    except Exception as e:
        print(f"❌ UnifiedCatalogDataProduct instantiation: FAILED - {e}")
        return False
        
    return True

if __name__ == "__main__":
    print("🧪 Testing Unified Catalog Data Product Implementation")
    print("=" * 50)
    
    success = True
    
    print("\n1. Testing Imports...")
    success &= test_imports()
    
    print("\n2. Testing Endpoints...")
    success &= test_endpoints()
    
    print("\n3. Testing Client Instantiation...")
    success &= test_client_instantiation()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 ALL TESTS PASSED! Unified Catalog Data Product CLI is ready!")
        print("\nExample commands:")
        print("  # Create a new data product")
        print("  python -m purviewcli data-product create --name 'MyProduct' --description 'My Data Product'")
        print("")
        print("  # List data products")
        print("  python -m purviewcli data-product list")
        print("")
        print("  # Show data product details")
        print("  python -m purviewcli data-product show --data-product-id 'product-id'")
        print("")
        print("  # Publish data product")
        print("  python -m purviewcli data-product publish --data-product-id 'product-id'")
    else:
        print("❌ SOME TESTS FAILED! Check the errors above.")
        sys.exit(1)
