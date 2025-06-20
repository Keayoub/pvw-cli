#!/usr/bin/env python3
"""
Test script to debug Purview collections API call
"""

import os
import sys
import json

# Add the current directory to the path
sys.path.insert(0, os.path.dirname(__file__))

# Import our classes
from purviewcli.client._collections import Collections

def test_collections_api():
    """Test the collections API call directly"""
    print("=== Testing Collections API ===")
    
    # Print environment variables
    print(f"PURVIEW_ACCOUNT_NAME: {os.getenv('PURVIEW_ACCOUNT_NAME')}")
    print(f"AZURE_TENANT_ID: {os.getenv('AZURE_TENANT_ID')}")
    print(f"AZURE_CLIENT_ID: {os.getenv('AZURE_CLIENT_ID')}")
    print()
    
    try:
        # Create collections client
        print("Creating Collections client...")
        client = Collections()
        print("Collections client created successfully")
        
        # Call the list collections method
        print("Calling collectionsGetCollections...")
        result = client.collectionsGetCollections({})
        print(f"Result type: {type(result)}")
        print(f"Result: {result}")
        
        if result:
            print(f"Result keys: {result.keys() if isinstance(result, dict) else 'Not a dict'}")
            
        print("Test completed successfully")
        
    except Exception as e:
        print(f"Error occurred: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_collections_api()
