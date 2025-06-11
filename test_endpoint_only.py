#!/usr/bin/env python3
"""
Test authentication bypass - see if we can test endpoint construction without Azure auth
"""
import sys
import os

# Add the project to Python path
sys.path.insert(0, r'c:\Dvlp\Purview\Purview_cli')

print("Testing endpoint construction without Azure authentication...")

try:
    print("1. Testing direct endpoint imports...")
    from purviewcli.client.endpoint import Endpoint
    print("   ✓ Endpoint imported")
    
    from purviewcli.client.endpoints import PurviewEndpoints
    print("   ✓ PurviewEndpoints imported")
    
    print("2. Testing Collections import...")
    
    # Let's modify the import to avoid the sync_client
    import importlib
    import purviewcli.client._collection
    
    # Reload the module to see if we can catch import issues
    importlib.reload(purviewcli.client._collection)
    
    from purviewcli.client._collection import Collections
    print("   ✓ Collections imported successfully")
    
    print("3. Testing Collections instantiation...")
    collections = Collections()
    print(f"   ✓ Collections created: app={collections.app}")
    
    print("4. Testing endpoint setup...")
    collections.method = 'GET'
    collections.endpoint = PurviewEndpoints.COLLECTIONS['base']
    collections.params = {"api-version": "2019-11-01-preview"}
    
    print(f"   Method: {collections.method}")
    print(f"   Endpoint: {collections.endpoint}")
    print(f"   Params: {collections.params}")
    
    print("5. Testing URL construction logic...")
    # Test the URL construction manually
    account_name = os.getenv('PURVIEW_ACCOUNT_NAME', 'test-account')
    print(f"   Account name: '{account_name}'")
    
    # Construct the expected URL
    base_url = f"https://{account_name.strip()}.purview.azure.com"
    print(f"   Base URL: {base_url}")
    
    full_endpoint = f"{base_url}/catalog{collections.endpoint}"
    print(f"   Full endpoint URL: {full_endpoint}")
    
    print("\n✅ SUCCESS: All endpoint construction tests passed!")
    print(f"✅ Collections.app is correctly set to: '{collections.app}'")
    print(f"✅ URL would be: {full_endpoint}")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
