"""Find real entities in Purview using discovery endpoint"""
import os
import requests
from azure.identity import DefaultAzureCredential
import json

os.environ['PURVIEW_ACCOUNT_NAME'] = 'kaydemopurview'

# Use regular Purview API (not Unified Catalog) for discovery
credential = DefaultAzureCredential()
token = credential.get_token("https://purview.azure.net/.default")

account_name = os.environ['PURVIEW_ACCOUNT_NAME']
base_url = f"https://{account_name}.purview.azure.com"

headers = {
    "Authorization": f"Bearer {token.token}",
    "Content-Type": "application/json"
}

print("Searching for entities in Purview...\n")

# Use the catalog/api/search/query endpoint (regular Purview API)
try:
    search_payload = {
        "keywords": None,
        "limit": 10,
        "offset": 0
    }
    
    response = requests.post(
        f"{base_url}/catalog/api/search/query",
        headers=headers,
        json=search_payload,
        params={"api-version": "2023-09-01"},
        timeout=30
    )
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Found {data.get('@search.count', 0)} total entities\n")
        
        values = data.get('value', [])
        if values:
            print("First 5 entities:")
            for i, entity in enumerate(values[:5], 1):
                guid = entity.get('id', 'N/A')
                name = entity.get('name', 'N/A')
                entity_type = entity.get('entityType', 'N/A')
                qualified_name = entity.get('qualifiedName', 'N/A')
                
                print(f"\n{i}. {name}")
                print(f"   GUID: {guid}")
                print(f"   Type: {entity_type}")
                print(f"   Qualified Name: {qualified_name}")
        else:
            print("No entities found in the catalog.")
    else:
        print(f"Error: {response.text}")
        
except Exception as e:
    print(f"Failed: {e}")
