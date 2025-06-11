#!/usr/bin/env python3
"""
Debug script to test collections functionality
"""
import os
import sys
import time

# Add current directory to path
sys.path.insert(0, '.')

print("=== Debug Collections Test ===")
print(f"PURVIEW_ACCOUNT_NAME: '{os.getenv('PURVIEW_ACCOUNT_NAME')}'")
print(f"AZURE_REGION: '{os.getenv('AZURE_REGION')}'")

# Test URL construction
from purviewcli.client.sync_client import SyncPurviewConfig, SyncPurviewClient

try:
    # Test config creation
    account_name = os.getenv('PURVIEW_ACCOUNT_NAME', 'test-account')
    print(f"Account name: '{account_name}'")
    print(f"Account name length: {len(account_name)}")
    print(f"Account name repr: {repr(account_name)}")
    
    config = SyncPurviewConfig(
        account_name=account_name,
        azure_region=os.getenv('AZURE_REGION', 'public')
    )
    
    client = SyncPurviewClient(config)
    print(f"Base URL: {client.base_url}")
    
    # Test Collections import
    from purviewcli.client._collection import Collections
    collections = Collections()
    print(f"Collections app: {collections.app}")
    
    # Test endpoint construction
    endpoint_info = {
        'app': collections.app,
        'method': 'GET',
        'endpoint': '/collections',
        'params': {"api-version": "2019-11-01-preview"},
        'payload': None
    }
    
    print(f"Endpoint info: {endpoint_info}")
      # Test actual request with timeout
    print("Making request...")
    start_time = time.time()    
    # Test just the client creation and URL
    print("Testing client creation...")
    client = SyncPurviewClient(config)
    print(f"Base URL: {client.base_url}")
    print(f"Auth scope: {client.auth_scope}")
    
    # Exit here for now to avoid hanging
    print("Debug complete - exiting before actual request")

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
