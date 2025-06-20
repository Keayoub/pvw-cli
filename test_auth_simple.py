#!/usr/bin/env python3
"""
Simple test of Purview authentication and HTTP request
"""

import os
import requests
from azure.identity import DefaultAzureCredential

def test_purview_auth():
    """Test authentication and simple API call to Purview"""
    
    account_name = os.getenv('PURVIEW_ACCOUNT_NAME', 'kaydemopurview')
    base_url = f"https://{account_name}.purview.azure.com"
    auth_scope = "https://purview.azure.net/.default"
    
    print(f"Account: {account_name}")
    print(f"Base URL: {base_url}")
    print(f"Auth scope: {auth_scope}")
    
    try:
        # Get authentication token
        print("Getting authentication token...")
        credential = DefaultAzureCredential()
        token = credential.get_token(auth_scope)
        print(f"Token acquired successfully (length: {len(token.token)})")
        
        # Test the collections endpoint
        collections_url = f"{base_url}/account/collections?api-version=2019-11-01-preview"
        print(f"Testing endpoint: {collections_url}")
        
        headers = {
            "Authorization": f"Bearer {token.token}",
            "Content-Type": "application/json",
            "User-Agent": "purviewcli-test/1.0"
        }
        
        print("Making HTTP request...")
        response = requests.get(collections_url, headers=headers, timeout=30)
        
        print(f"Response status: {response.status_code}")
        print(f"Response headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"Response data type: {type(data)}")
                print(f"Response data: {data}")
            except Exception as e:
                print(f"Failed to parse JSON: {e}")
                print(f"Response text: {response.text}")
        else:
            print(f"Error response: {response.text}")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_purview_auth()
