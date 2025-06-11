#!/usr/bin/env python3
"""
Debug Collections Endpoint URL Construction
"""
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'purviewcli'))

from purviewcli.client.endpoints import PurviewEndpoints
from purviewcli.client._collection import Collections

def debug_collections_url():
    print("=== Collections Endpoint Debug ===")
    
    # Check what the Collections class is configured with
    collections = Collections()
    print(f"Collections.app = {collections.app}")
    
    # Check the endpoint URL construction
    base_endpoint = PurviewEndpoints.COLLECTIONS['base']
    print(f"PurviewEndpoints.COLLECTIONS['base'] = {base_endpoint}")
    
    # Check what the account name environment variable is
    account_name = os.environ.get('PURVIEW_ACCOUNT_NAME', 'NOT_SET')
    print(f"PURVIEW_ACCOUNT_NAME = '{account_name}'")
    
    # Construct the full URL
    if account_name != 'NOT_SET':
        full_url = f"https://{account_name}.purview.azure.com{base_endpoint}"
        print(f"Full URL would be: {full_url}")
    else:
        print("ERROR: PURVIEW_ACCOUNT_NAME environment variable is not set!")
    
    print("\n=== Method Details ===")
    # Mock args for the method
    mock_args = {}
    collections.collectionsGetCollections(mock_args)
    print(f"Method: {collections.method}")
    print(f"Endpoint: {collections.endpoint}")
    print(f"Params: {getattr(collections, 'params', 'None')}")
    
    return full_url if account_name != 'NOT_SET' else None

if __name__ == "__main__":
    url = debug_collections_url()
    print(f"\n=== Summary ===")
    print(f"Expected URL: {url}")
    print("If this URL looks correct, the issue is likely authentication-related.")
