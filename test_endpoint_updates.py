#!/usr/bin/env python3
"""
Test script to verify the updated endpoint configurations
Tests that all client modules can import and use the centralized endpoints
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'purviewcli'))

def test_endpoint_imports():
    """Test that all client modules can import the endpoints module"""
    print("🧪 Testing endpoint imports...")
    
    try:
        from purviewcli.client.endpoints import PurviewEndpoints
        print("✅ PurviewEndpoints imported successfully")
        
        # Test endpoint configuration access
        assert hasattr(PurviewEndpoints, 'ENTITY'), "ENTITY endpoints not found"
        assert hasattr(PurviewEndpoints, 'GLOSSARY'), "GLOSSARY endpoints not found"
        assert hasattr(PurviewEndpoints, 'SEARCH'), "SEARCH endpoints not found"
        assert hasattr(PurviewEndpoints, 'SCAN'), "SCAN endpoints not found"
        print("✅ All endpoint categories present")
        
        # Test format_endpoint utility
        test_endpoint = PurviewEndpoints.format_endpoint(
            PurviewEndpoints.ENTITY['guid'] + "/{guid}", 
            guid="test-guid-123"
        )
        expected = "/datamap/api/atlas/v2/entity/guid/test-guid-123"
        assert test_endpoint == expected, f"Expected {expected}, got {test_endpoint}"
        print("✅ Endpoint formatting works correctly")
        
        return True
        
    except Exception as e:
        print(f"❌ Endpoint import failed: {e}")
        return False

def test_client_modules():
    """Test that all client modules can be imported with the new endpoints"""
    print("\n🧪 Testing client module imports...")
    
    modules_to_test = [
        'purviewcli.client._entity',
        'purviewcli.client._glossary',
        'purviewcli.client._search',
        'purviewcli.client._types',
        'purviewcli.client._relationship',
        'purviewcli.client._account',
        'purviewcli.client._management',
        'purviewcli.client._scan',
        'purviewcli.client._lineage'
    ]
    
    success_count = 0
    for module_name in modules_to_test:
        try:
            __import__(module_name)
            print(f"✅ {module_name} imported successfully")
            success_count += 1
        except Exception as e:
            print(f"❌ {module_name} failed to import: {e}")
    
    print(f"\n📊 Import Results: {success_count}/{len(modules_to_test)} modules imported successfully")
    return success_count == len(modules_to_test)

def test_endpoint_examples():
    """Test specific endpoint examples"""
    print("\n🧪 Testing endpoint examples...")
    
    try:
        from purviewcli.client.endpoints import PurviewEndpoints
        
        # Test various endpoint types
        test_cases = [
            ("Entity base", PurviewEndpoints.ENTITY['base'], "/datamap/api/atlas/v2/entity"),
            ("Glossary base", PurviewEndpoints.GLOSSARY['base'], "/datamap/api/atlas/v2/glossary"),
            ("Search query", PurviewEndpoints.SEARCH['query'], "/search/api/query"),
            ("Scan datasources", PurviewEndpoints.SCAN['datasources'], "/scan/datasources"),
            ("Management operations", PurviewEndpoints.MANAGEMENT['operations'], "/providers/Microsoft.Purview/operations")
        ]
        
        for name, actual, expected in test_cases:
            if actual == expected:
                print(f"✅ {name}: {actual}")
            else:
                print(f"❌ {name}: Expected {expected}, got {actual}")
                return False
                
        print("✅ All endpoint examples correct")
        return True
        
    except Exception as e:
        print(f"❌ Endpoint testing failed: {e}")
        return False

def test_api_versions():
    """Test API version configuration"""
    print("\n🧪 Testing API version configurations...")
    
    try:
        from purviewcli.client.endpoints import PurviewEndpoints
        
        # Test API version helpers
        search_params = PurviewEndpoints.get_api_version_params('search')
        mgmt_params = PurviewEndpoints.get_api_version_params('management')
        
        assert 'api-version' in search_params, "Search API version not found"
        assert 'api-version' in mgmt_params, "Management API version not found"
        assert search_params['api-version'] == '2021-05-01-preview', "Wrong search API version"
        assert mgmt_params['api-version'] == '2021-07-01', "Wrong management API version"
        
        print("✅ API version configurations correct")
        return True
        
    except Exception as e:
        print(f"❌ API version testing failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Testing Updated Purview CLI Endpoint Configuration")
    print("=" * 60)
    
    tests = [
        test_endpoint_imports,
        test_client_modules,
        test_endpoint_examples,
        test_api_versions
    ]
    
    passed = 0
    for test_func in tests:
        if test_func():
            passed += 1
    
    print(f"\n🏁 Test Results: {passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        print("🎉 All tests passed! The endpoint configuration is working correctly.")
        return True
    else:
        print("⚠️  Some tests failed. Please check the issues above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
